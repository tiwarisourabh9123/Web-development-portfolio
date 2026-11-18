import pytest
from app import create_app

USER = dict(name="Asha Nair", email="asha@example.com", password="secret1", phone="+91 9876543210",
            blood_group="O+", gender="Female", birth_date="1998-05-10", weight="58",
            state="Kerala", zip_code="686141", district="Kottayam", area="Vaikom", landmark="Near bus stand")


@pytest.fixture
def client(tmp_path):
    return create_app(str(tmp_path / "test.db")).test_client()


def register(client, **over):
    return client.post("/api/register", json={**USER, **over})


def test_register_login_logout(client):
    assert register(client).status_code == 201
    assert register(client).status_code == 409                       # duplicate email
    client.post("/api/logout")
    assert client.get("/api/me").status_code == 401
    assert client.post("/api/login", json={"email": USER["email"], "password": "bad"}).status_code == 401
    assert client.post("/api/login", json={"email": USER["email"], "password": "secret1"}).status_code == 200
    assert client.get("/api/me").json["blood_group"] == "O+"


def test_validation(client):
    assert register(client, blood_group="Z+").status_code == 400
    assert register(client, password="123").status_code == 400
    assert register(client, birth_date="2015-01-01").status_code == 400   # under 18
    assert register(client, weight="abc").status_code == 400


def test_update_profile_and_password(client):
    register(client)
    r = client.put("/api/me", json={"name": "Asha K", "is_available": False})
    assert r.json["user"]["name"] == "Asha K" and r.json["user"]["is_available"] is False
    assert client.put("/api/me/password", json={"current_password": "x", "new_password": "newpass1",
                                                "confirm_new_password": "newpass1"}).status_code == 400
    assert client.put("/api/me/password", json={"current_password": "secret1", "new_password": "newpass1",
                                                "confirm_new_password": "newpass1"}).status_code == 200


def test_find_donors_hides_private_data(client):
    register(client)
    rows = client.get("/api/donors?blood_group=O%2B&state=kerala").json
    assert len(rows) == 1 and "email" not in rows[0] and "password_hash" not in rows[0]
    assert client.get("/api/donors?blood_group=A%2B").json == []
    client.put("/api/me", json={"is_available": False})
    assert client.get("/api/donors").json == []                        # hidden when unavailable


def test_donations_crud_and_isolation(client):
    register(client)
    d = {"donated_on": "2024-01-15", "location": "City Hospital", "units": 1, "notes": "ok"}
    did = client.post("/api/donations", json=d).json["id"]
    assert client.put(f"/api/donations/{did}", json={**d, "units": 2}).status_code == 200
    assert client.get("/api/donations").json[0]["units"] == 2
    assert client.post("/api/donations", json={**d, "donated_on": "2999-01-01"}).status_code == 400
    # another user cannot touch it
    other = create_app(client.application.config["DB_PATH"]).test_client()
    register(other, email="b@example.com")
    assert other.delete(f"/api/donations/{did}").status_code == 404
    assert client.delete(f"/api/donations/{did}").status_code == 200
    assert client.get("/api/donations").json == []


def test_delete_account(client):
    register(client)
    client.post("/api/donations", json={"donated_on": "2024-01-15", "location": "X"})
    assert client.delete("/api/me", json={"password": "wrong"}).status_code == 403
    assert client.delete("/api/me", json={"password": "secret1"}).status_code == 200
    assert client.get("/api/me").status_code == 401
    assert client.post("/api/login", json={"email": USER["email"], "password": "secret1"}).status_code == 401


def test_contact_and_static(client):
    assert client.post("/api/contact", json={"email": "bad"}).status_code == 400
    assert client.post("/api/contact", json={"email": "x@y.com"}).status_code == 201
    assert client.get("/").status_code == 200
    assert client.get("/dashboard.html").status_code == 200
    assert client.get("/api/nope").status_code == 404
