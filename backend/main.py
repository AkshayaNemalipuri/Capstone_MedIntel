from pathlib import Path
import shutil
import uuid

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

import models
import schemas
from database import Base, engine, get_db
from security import hash_password, verify_password, create_token, require_role

Base.metadata.create_all(bind=engine)

app = FastAPI(title="MedIntel API", version="1.0.0")

# Frontend is served at localhost:5500 using python -m http.server.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}


def patient_or_404(db: Session, patient_id: int):
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found.")
    return patient


def doctor_or_404(db: Session, doctor_id: int):
    doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found.")
    return doctor


def patient_dict(p):
    return {
        "id": p.id, "name": p.name, "email": p.email, "age": p.age,
        "gender": p.gender, "phone": p.phone, "blood_group": p.blood_group,
        "allergies": p.allergies,
    }


def doctor_dict(d):
    return {
        "id": d.id, "full_name": d.full_name, "email": d.email,
        "phone": d.phone, "registration_number": d.registration_number,
        "specialization": d.specialization, "qualification": d.qualification,
        "experience": d.experience, "hospital": d.hospital, "address": d.address,
    }


def history_dict(h):
    return {
        "id": h.id, "patient_id": h.patient_id, "condition": h.condition,
        "diagnosis_date": h.diagnosis_date, "treatment": h.treatment,
        "medications": h.medications, "doctor_name": h.doctor_name, "notes": h.notes,
    }


def report_dict(r):
    return {
        "id": r.id, "patient_id": r.patient_id, "report_name": r.report_name,
        "content_type": r.content_type,
        "uploaded_at": r.uploaded_at.isoformat() if r.uploaded_at else None,
    }


@app.get("/")
def home():
    return {"message": "MedIntel API is running", "docs": "/docs"}


# ---------------- PATIENT AUTH ----------------

@app.post("/auth/patient/register", status_code=201)
def register_patient(data: schemas.PatientRegister, db: Session = Depends(get_db)):
    email = data.email.lower()
    if db.query(models.Patient).filter(models.Patient.email == email).first():
        raise HTTPException(status_code=409, detail="This patient email is already registered.")
    patient = models.Patient(
        name=data.name.strip(), email=email, password_hash=hash_password(data.password),
        age=data.age, gender=data.gender, phone=data.phone,
        blood_group=data.blood_group, allergies=data.allergies,
    )
    db.add(patient)
    try:
        db.commit()
        db.refresh(patient)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="This email is already registered.")
    return {"message": "Patient registered successfully.", "patient_id": patient.id}


@app.post("/auth/patient/login")
def login_patient(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    patient = db.query(models.Patient).filter(models.Patient.email == data.email.lower()).first()
    if not patient or not verify_password(data.password, patient.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect patient email or password.")
    return {
        "message": "Patient login successful.", "access_token": create_token(patient.id, "patient"),
        "token_type": "bearer", "role": "patient", "user": patient_dict(patient),
    }


@app.get("/auth/patient/me")
def patient_me(user=Depends(require_role("patient")), db: Session = Depends(get_db)):
    return patient_dict(patient_or_404(db, int(user["sub"])))


# ---------------- DOCTOR AUTH ----------------

@app.post("/doctor/register", status_code=201)
def register_doctor(data: schemas.DoctorRegister, db: Session = Depends(get_db)):
    email = data.email.lower()
    if db.query(models.Doctor).filter(models.Doctor.email == email).first():
        raise HTTPException(status_code=409, detail="This doctor email is already registered.")
    if db.query(models.Doctor).filter(
        models.Doctor.registration_number == data.registration_number
    ).first():
        raise HTTPException(status_code=409, detail="This medical registration number is already used.")
    doctor = models.Doctor(
        full_name=data.full_name.strip(), email=email,
        password_hash=hash_password(data.password), phone=data.phone,
        registration_number=data.registration_number.strip(),
        specialization=data.specialization, qualification=data.qualification,
        experience=data.experience, hospital=data.hospital, address=data.address,
    )
    db.add(doctor)
    try:
        db.commit()
        db.refresh(doctor)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Doctor email or registration number already exists.")
    return {"message": "Doctor registered successfully.", "doctor_id": doctor.id}


@app.post("/doctor/login")
def login_doctor(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    doctor = db.query(models.Doctor).filter(models.Doctor.email == data.email.lower()).first()
    if not doctor or not verify_password(data.password, doctor.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect doctor email or password.")
    return {
        "message": "Doctor login successful.", "access_token": create_token(doctor.id, "doctor"),
        "token_type": "bearer", "role": "doctor", "user": doctor_dict(doctor),
    }


@app.get("/doctor/profile")
def doctor_profile(user=Depends(require_role("doctor")), db: Session = Depends(get_db)):
    return doctor_dict(doctor_or_404(db, int(user["sub"])))


# ---------------- PATIENT DATA ----------------

@app.get("/patients")
def get_patients(user=Depends(require_role("doctor")), db: Session = Depends(get_db)):
    return [patient_dict(p) for p in db.query(models.Patient).order_by(models.Patient.id.desc()).all()]


@app.get("/patients/{patient_id}")
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = patient_or_404(db, patient_id)
    return patient_dict(patient)


@app.post("/patients/{patient_id}/medical-history", status_code=201)
def add_medical_history(
    patient_id: int, data: schemas.HistoryCreate,
    user=Depends(require_role("doctor")), db: Session = Depends(get_db)
):
    patient_or_404(db, patient_id)
    item = models.MedicalHistory(patient_id=patient_id, **data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return history_dict(item)


@app.get("/patients/{patient_id}/medical-history")
def get_medical_history(
    patient_id: int, user=Depends(get_current_user_placeholder := __import__("security").get_current_user),
    db: Session = Depends(get_db)
):
    # Patient can see only their own history; doctors can see records in this demo.
    patient_or_404(db, patient_id)
    if user["role"] == "patient" and int(user["sub"]) != patient_id:
        raise HTTPException(status_code=403, detail="You can only view your own medical history.")
    rows = db.query(models.MedicalHistory).filter(
        models.MedicalHistory.patient_id == patient_id
    ).order_by(models.MedicalHistory.id.desc()).all()
    return [history_dict(h) for h in rows]


@app.post("/patients/{patient_id}/reports", status_code=201)
async def upload_report(
    patient_id: int, file: UploadFile = File(...),
    user=Depends(__import__("security").get_current_user), db: Session = Depends(get_db)
):
    patient_or_404(db, patient_id)
    if user["role"] == "patient" and int(user["sub"]) != patient_id:
        raise HTTPException(status_code=403, detail="You can only upload to your own profile.")
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PDF, PNG, JPG and JPEG files are allowed.")
    contents = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File is too large. Maximum size is 10 MB.")
    stored_name = f"{patient_id}_{uuid.uuid4().hex}{suffix}"
    destination = UPLOAD_DIR / stored_name
    destination.write_bytes(contents)
    report = models.MedicalReport(
        patient_id=patient_id, report_name=Path(file.filename).name,
        stored_name=stored_name, content_type=file.content_type,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return {"message": "Report uploaded successfully.", "report": report_dict(report)}


@app.get("/patients/{patient_id}/reports")
def get_reports(
    patient_id: int, user=Depends(__import__("security").get_current_user),
    db: Session = Depends(get_db)
):
    patient_or_404(db, patient_id)
    if user["role"] == "patient" and int(user["sub"]) != patient_id:
        raise HTTPException(status_code=403, detail="You can only view your own reports.")
    rows = db.query(models.MedicalReport).filter(
        models.MedicalReport.patient_id == patient_id
    ).order_by(models.MedicalReport.id.desc()).all()
    return [report_dict(r) for r in rows]


@app.get("/reports/{report_id}/download")
def download_report(
    report_id: int, user=Depends(__import__("security").get_current_user),
    db: Session = Depends(get_db)
):
    report = db.query(models.MedicalReport).filter(models.MedicalReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    if user["role"] == "patient" and int(user["sub"]) != report.patient_id:
        raise HTTPException(status_code=403, detail="You can only download your own reports.")
    path = UPLOAD_DIR / report.stored_name
    if not path.exists():
        raise HTTPException(status_code=404, detail="Stored report file is missing.")
    return FileResponse(path, filename=report.report_name, media_type=report.content_type or "application/octet-stream")


@app.get("/patients/{patient_id}/timeline")
def patient_timeline(
    patient_id: int, user=Depends(__import__("security").get_current_user),
    db: Session = Depends(get_db)
):
    patient = patient_or_404(db, patient_id)
    if user["role"] == "patient" and int(user["sub"]) != patient_id:
        raise HTTPException(status_code=403, detail="You can only view your own timeline.")
    history = db.query(models.MedicalHistory).filter(
        models.MedicalHistory.patient_id == patient_id
    ).all()
    reports = db.query(models.MedicalReport).filter(
        models.MedicalReport.patient_id == patient_id
    ).all()
    events = [
        {"type": "Medical history", "date": h.diagnosis_date or "", "title": h.condition, "details": h.notes or ""}
        for h in history
    ] + [
        {"type": "Medical report", "date": r.uploaded_at.isoformat() if r.uploaded_at else "", "title": r.report_name, "details": f"Report ID: {r.id}"}
        for r in reports
    ]
    events.sort(key=lambda x: x["date"], reverse=True)
    return {"patient": patient_dict(patient), "timeline": events}


# ---------------- DOCTOR DASHBOARD ----------------

@app.get("/doctor/patients")
def doctor_patients(user=Depends(require_role("doctor")), db: Session = Depends(get_db)):
    return [patient_dict(p) for p in db.query(models.Patient).order_by(models.Patient.id.desc()).all()]


@app.get("/doctor/patients/{patient_id}/medical-history")
def doctor_patient_history(
    patient_id: int, user=Depends(require_role("doctor")), db: Session = Depends(get_db)
):
    patient_or_404(db, patient_id)
    rows = db.query(models.MedicalHistory).filter(
        models.MedicalHistory.patient_id == patient_id
    ).order_by(models.MedicalHistory.id.desc()).all()
    return [history_dict(h) for h in rows]


@app.get("/doctor/patients/{patient_id}/reports")
def doctor_patient_reports(
    patient_id: int, user=Depends(require_role("doctor")), db: Session = Depends(get_db)
):
    patient_or_404(db, patient_id)
    rows = db.query(models.MedicalReport).filter(
        models.MedicalReport.patient_id == patient_id
    ).order_by(models.MedicalReport.id.desc()).all()
    return [report_dict(r) for r in rows]
