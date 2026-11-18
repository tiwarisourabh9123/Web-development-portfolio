
# 🩺 Samriddhi Swasthya Seva

A community health service website that connects people in need with blood donors, ambulance support and trusted health guidance. The idea is simple: a healthy family is a prosperous family.

**Frontend:** HTML, CSS, vanilla JavaScript
**Backend:** Python Flask REST API with SQLite storage (no database server needed)

---

## Features

| Area | What it does |
|---|---|
| Create | Register a donor account, add donation records, send a "Get Response Back" email request |
| Read | View your profile and donation history, public **Find Donor** search |
| Update | Edit profile, edit donations, change password, toggle "available to donate" |
| Delete | Delete donation records, delete your own account |

### Pages
- **Home:** hero, donor search, about, services, initiatives
- **Find Donor:** search by blood group, state and district
- **About Us / Contact**
- **Why Donate / Can You Donate:** awareness and eligibility information
- **Login / Register / Dashboard:** donor account area

### Security
- Hashed passwords (Werkzeug)
- Parameterised SQL queries
- HttpOnly session cookies
- Output escaping
- Input validation

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, JavaScript (ES6) |
| Backend | Python, Flask |
| Database | SQLite |
| Testing | pytest |

---

## Getting Started

```bash
git clone https://github.com/tiwarisourabh9123/Web-development-portfolio.git
cd Web-development-portfolio/samriddhi-swasthya-seva

python -m venv .venv
source .venv/Scripts/activate      # Windows (Git Bash)
# .venv\Scripts\activate           # Windows (Command Prompt)
# source .venv/bin/activate        # macOS / Linux

pip install -r requirements.txt
python app.py
```

Open **http://127.0.0.1:5000** in your browser. The SQLite database is created automatically at `instance/redstream.db`.

### Run the tests
```bash
pip install pytest
pytest
```

---

## Project Structure

```
samriddhi-swasthya-seva/
├── app.py                # Flask app: API routes + serves the static site
├── requirements.txt
├── tests/
│   └── test_api.py       # pytest suite
└── static/               # frontend
    ├── index.html, about.html, contact.html
    ├── donors.html, whydonate.html, canyoudonate.html
    ├── login.html, register.html, dashboard.html
    └── assets/
        ├── css/
        ├── js/
        └── images/
```

---

## Design
- Responsive layout for desktop, tablet and mobile
- Green health-care theme
- Card-based service and initiative sections

---

## Notes
- Back up `instance/redstream.db` regularly if you use it for real data.
- The `instance/` folder and `.venv/` are not included in the repository.
- Based on an open-source donor-website template. See the `LICENSE` file for license details.

---

