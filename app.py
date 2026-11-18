"""Samriddhi Swasthya Seva - Flask API + static site server (SQLite storage).

Run:  python app.py   ->  http://127.0.0.1:5000
"""
import os
import re
import secrets
import sqlite3
from datetime import date, timedelta
from functools import wraps

from flask import Flask, g, jsonify, request, session
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

PROFILE_FIELDS = ["name", "phone", "blood_group", "gender", "birth_date", "weight",
                  "state", "zip_code", "district", "area", "landmark"]

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    blood_group TEXT NOT NULL,
    gender TEXT NOT NULL,
    birth_date TEXT NOT NULL,
    weight REAL NOT NULL,
    state TEXT NOT NULL,
    zip_code TEXT NOT NULL,
    district TEXT NOT NULL,
    area TEXT NOT NULL,
    landmark TEXT DEFAULT '',
    is_available INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS donations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    donated_on TEXT NOT NULL,
    location TEXT NOT NULL,
    units INTEGER NOT NULL DEFAULT 1,
    notes TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS response_back (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def create_app(db_path=None):
    app = Flask(__name__, static_folder="static", static_url_path="")
    app.config["DB_PATH"] = db_path or os.path.join(BASE_DIR, "instance", "redstream.db")
    os.makedirs(os.path.dirname(app.config["DB_PATH"]), exist_ok=True)
    app.config.update(SECRET_KEY=_secret_key(app), SESSION_COOKIE_HTTPONLY=True,
                      SESSION_COOKIE_SAMESITE="Lax", MAX_CONTENT_LENGTH=64 * 1024)

    with sqlite3.connect(app.config["DB_PATH"]) as con:
        con.executescript(SCHEMA)

    # ---------- helpers ----------
    def db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DB_PATH"])
            g.db.row_factory = sqlite3.Row
            g.db.execute("PRAGMA foreign_keys = ON")
        return g.db

    @app.teardown_appcontext
    def close_db(_):
        con = g.pop("db", None)
        if con is not None:
            con.close()

    def error(msg, code=400):
        return jsonify(error=msg), code

    def login_required(fn):
        @wraps(fn)
        def wrapper(*a, **kw):
            if "user_id" not in session:
                return error("Please log in first.", 401)
            return fn(*a, **kw)
        return wrapper

    def current_user():
        return db().execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()

    def user_json(u):
        d = {k: u[k] for k in ["id", "email", "created_at"] + PROFILE_FIELDS}
        d["is_available"] = bool(u["is_available"])
        d["donations_count"] = db().execute(
            "SELECT COUNT(*) FROM donations WHERE user_id = ?", (u["id"],)).fetchone()[0]
        return d

    def clean_profile(data, partial=False):
        """Validate profile fields. Returns (values, error)."""
        out = {}
        for f in PROFILE_FIELDS:
            if f not in data:
                if partial or f == "landmark":
                    continue
                return None, f"'{f}' is required."
            out[f] = str(data[f]).strip()
            if not out[f] and f != "landmark":
                return None, f"'{f}' cannot be empty."
        if "blood_group" in out and out["blood_group"] not in BLOOD_GROUPS:
            return None, "Invalid blood group."
        if "gender" in out and out["gender"] not in ("Male", "Female", "Other"):
            return None, "Invalid gender."
        if "phone" in out and not re.fullmatch(r"\+?[0-9 \-]{7,15}", out["phone"]):
            return None, "Enter a valid phone number."
        if "weight" in out:
            try:
                out["weight"] = float(out["weight"])
            except ValueError:
                return None, "Weight must be a number."
            if not 20 <= out["weight"] <= 300:
                return None, "Weight must be between 20 and 300 kg."
        if "birth_date" in out:
            try:
                born = date.fromisoformat(out["birth_date"])
            except ValueError:
                return None, "Birth date must be YYYY-MM-DD."
            if born > date.today() - timedelta(days=365 * 18):
                return None, "Donors must be at least 18 years old."
        return out, None

    def clean_donation(data):
        try:
            d = date.fromisoformat(str(data.get("donated_on", "")))
        except ValueError:
            return None, "Donation date must be YYYY-MM-DD."
        if d > date.today():
            return None, "Donation date cannot be in the future."
        location = str(data.get("location", "")).strip()
        if not location:
            return None, "Location is required."
        try:
            units = int(data.get("units", 1))
        except (TypeError, ValueError):
            return None, "Units must be a number."
        if not 1 <= units <= 5:
            return None, "Units must be between 1 and 5."
        return {"donated_on": d.isoformat(), "location": location[:120],
                "units": units, "notes": str(data.get("notes", "")).strip()[:300]}, None

    # ---------- auth ----------
    @app.post("/api/register")
    def register():
        data = request.get_json(silent=True) or {}
        values, err = clean_profile(data)
        if err:
            return error(err)
        email = str(data.get("email", "")).strip().lower()
        password = str(data.get("password", ""))
        if not EMAIL_RE.match(email):
            return error("Enter a valid email address.")
        if len(password) < 6:
            return error("Password must be at least 6 characters.")
        try:
            cols = ["email", "password_hash"] + list(values)
            vals = [email, generate_password_hash(password)] + list(values.values())
            cur = db().execute(
                f"INSERT INTO users ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})", vals)
            db().commit()
        except sqlite3.IntegrityError:
            return error("This email is already registered.", 409)
        session["user_id"] = cur.lastrowid
        return jsonify(message="Registration successful!"), 201

    @app.post("/api/login")
    def login():
        data = request.get_json(silent=True) or {}
        email = str(data.get("email", "")).strip().lower()
        u = db().execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if not u or not check_password_hash(u["password_hash"], str(data.get("password", ""))):
            return error("Incorrect email or password.", 401)
        session.clear()
        session["user_id"] = u["id"]
        session.permanent = bool(data.get("remember_me"))
        app.permanent_session_lifetime = timedelta(days=30)
        return jsonify(message="Logged in.")

    @app.post("/api/logout")
    def logout():
        session.clear()
        return jsonify(message="Logged out.")

    # ---------- users: Read / Update / Delete ----------
    @app.get("/api/me")
    @login_required
    def me():
        u = current_user()
        if not u:
            session.clear()
            return error("Account not found.", 401)
        return jsonify(user_json(u))

    @app.put("/api/me")
    @login_required
    def update_me():
        data = request.get_json(silent=True) or {}
        values, err = clean_profile(data, partial=True)
        if err:
            return error(err)
        if "is_available" in data:
            values["is_available"] = 1 if data["is_available"] else 0
        if not values:
            return error("Nothing to update.")
        sets = ", ".join(f"{k} = ?" for k in values)
        db().execute(f"UPDATE users SET {sets} WHERE id = ?", [*values.values(), session["user_id"]])
        db().commit()
        return jsonify(message="Information updated successfully.", user=user_json(current_user()))

    @app.put("/api/me/password")
    @login_required
    def change_password():
        data = request.get_json(silent=True) or {}
        u = current_user()
        if not check_password_hash(u["password_hash"], str(data.get("current_password", ""))):
            return error("Old password is incorrect.")
        new = str(data.get("new_password", ""))
        if len(new) < 6:
            return error("Password must be at least 6 characters long.")
        if new != data.get("confirm_new_password"):
            return error("New password and confirmation do not match.")
        db().execute("UPDATE users SET password_hash = ? WHERE id = ?",
                     (generate_password_hash(new), u["id"]))
        db().commit()
        return jsonify(message="Password updated successfully.")

    @app.delete("/api/me")
    @login_required
    def delete_me():
        data = request.get_json(silent=True) or {}
        u = current_user()
        if not check_password_hash(u["password_hash"], str(data.get("password", ""))):
            return error("Password is incorrect.", 403)
        db().execute("DELETE FROM users WHERE id = ?", (u["id"],))
        db().commit()
        session.clear()
        return jsonify(message="Your account has been deleted.")

    # ---------- find donors (public read) ----------
    @app.get("/api/donors")
    def donors():
        sql = ("SELECT id, name, blood_group, gender, state, district, area, phone "
               "FROM users WHERE is_available = 1")
        args = []
        bg = request.args.get("blood_group", "").strip()
        if bg:
            if bg not in BLOOD_GROUPS:
                return error("Invalid blood group.")
            sql += " AND blood_group = ?"
            args.append(bg)
        for f in ("state", "district", "area"):
            v = request.args.get(f, "").strip()
            if v:
                sql += f" AND LOWER({f}) LIKE ?"
                args.append(f"%{v.lower()}%")
        rows = db().execute(sql + " ORDER BY name LIMIT 100", args).fetchall()
        return jsonify([dict(r) for r in rows])

    # ---------- donations: full CRUD ----------
    @app.get("/api/donations")
    @login_required
    def list_donations():
        rows = db().execute("SELECT * FROM donations WHERE user_id = ? ORDER BY donated_on DESC",
                            (session["user_id"],)).fetchall()
        return jsonify([dict(r) for r in rows])

    @app.post("/api/donations")
    @login_required
    def add_donation():
        v, err = clean_donation(request.get_json(silent=True) or {})
        if err:
            return error(err)
        cur = db().execute(
            "INSERT INTO donations (user_id, donated_on, location, units, notes) VALUES (?,?,?,?,?)",
            (session["user_id"], v["donated_on"], v["location"], v["units"], v["notes"]))
        db().commit()
        return jsonify(id=cur.lastrowid, message="Donation added."), 201

    @app.put("/api/donations/<int:did>")
    @login_required
    def edit_donation(did):
        v, err = clean_donation(request.get_json(silent=True) or {})
        if err:
            return error(err)
        cur = db().execute(
            "UPDATE donations SET donated_on=?, location=?, units=?, notes=? WHERE id=? AND user_id=?",
            (v["donated_on"], v["location"], v["units"], v["notes"], did, session["user_id"]))
        db().commit()
        return jsonify(message="Donation updated.") if cur.rowcount else error("Not found.", 404)

    @app.delete("/api/donations/<int:did>")
    @login_required
    def delete_donation(did):
        cur = db().execute("DELETE FROM donations WHERE id=? AND user_id=?", (did, session["user_id"]))
        db().commit()
        return jsonify(message="Donation deleted.") if cur.rowcount else error("Not found.", 404)

    # ---------- contact ("Get Response Back") ----------
    @app.post("/api/contact")
    def contact():
        email = str((request.get_json(silent=True) or {}).get("email", "")).strip().lower()
        if not EMAIL_RE.match(email):
            return error("Enter a valid email address.")
        db().execute("INSERT INTO response_back (email) VALUES (?)", (email,))
        db().commit()
        return jsonify(message="Thanks! We will get back to you soon."), 201

    @app.errorhandler(404)
    def not_found(_):
        if request.path.startswith("/api/"):
            return error("Not found.", 404)
        return app.send_static_file("index.html"), 404

    @app.route("/")
    def home():
        return app.send_static_file("index.html")

    return app


def _secret_key(app):
    """Use SECRET_KEY env var, otherwise generate one and keep it in instance/."""
    if os.environ.get("SECRET_KEY"):
        return os.environ["SECRET_KEY"]
    path = os.path.join(os.path.dirname(app.config["DB_PATH"]), "secret.key")
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write(secrets.token_hex(32))
    with open(path) as f:
        return f.read().strip()


app = create_app()

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
