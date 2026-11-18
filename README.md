# MedIntel — Complete Starter Project

A fresh, local full-stack starter with:
- Patient registration and login
- Doctor registration and login
- Separate patient and doctor dashboards
- Patient profile, medical history, report upload/download, and timeline
- SQLite database
- FastAPI backend with password hashing and signed bearer tokens

> This is an academic/demo starter, not a production-ready medical-record system. Do not use real patient data. Before real deployment, add HTTPS, stronger token/session management, audit logs, consent and doctor-patient authorization, backups, privacy controls, malware scanning for uploads, and security review.

## Project structure

```text
MedIntel_Complete_Project/
  README.md
  frontend/
    index.html
    patient-register.html
    patient-login.html
    patient-dashboard.html
    doctor-register.html
    doctor-login.html
    doctor-dashboard.html
    assets/
      styles.css
      config.js
      common.js
  backend/
    main.py
    database.py
    models.py
    schemas.py
    security.py
    requirements.txt
    .env.example
    uploads/
```

## 1. Start the backend (Windows)

Open Command Prompt:

```cmd
cd Downloads\MedIntel_Complete_Project\backend
py -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
uvicorn main:app --reload
```

If `py` is unavailable, use `python` instead.

Backend:
- API: http://127.0.0.1:8000
- Swagger docs: http://127.0.0.1:8000/docs

Keep this terminal open while using the application.

## 2. Start the frontend

Open a second Command Prompt:

```cmd
cd Downloads\MedIntel_Complete_Project\frontend
py -m http.server 5500
```

If `py` is unavailable, use `python -m http.server 5500`.

Open:
- http://127.0.0.1:5500/

Do not double-click the HTML files for this setup; use the local frontend server.

## 3. Test the application

1. Open the homepage.
2. Register a test patient with a unique email and password.
3. Log in as that patient and try adding a medical-history entry or uploading a PDF/JPG/PNG report.
4. Log out.
5. Register a test doctor using a unique email and medical registration number.
6. Log in as the doctor and view the patient list and records.

The SQLite database `medintel.db` is created automatically in the backend folder on first run. Uploaded files are stored in `backend/uploads/`.

## Notes

- Patient and doctor accounts are separate.
- Passwords are stored as salted PBKDF2 hashes, not plain text.
- The app uses a simple HMAC-signed bearer token suitable only for a local academic demo. Change `MEDINTEL_SECRET` before any deployment.
- This demo allows a logged-in doctor to browse demo patients. A real system must enforce explicit doctor-patient assignment and patient consent.
- Uploaded files are restricted by extension and size in the API, but production systems need additional file scanning and storage controls.
- If you change the database model after first run, delete `backend/medintel.db` only if it contains no data you need, or implement migrations.
