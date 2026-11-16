from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
import os
import shutil
from datetime import datetime

from database import engine, Base, SessionLocal
import models
import schemas


# Create database tables
Base.metadata.create_all(bind=engine)


# Create FastAPI app
app = FastAPI(title="MedIntel API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():
    return {
        "message": "MedIntel backend is running",
        "database": "SQLite connected"
    }


# =========================================================
# PATIENT MANAGEMENT
# =========================================================

# Add Patient
@app.post("/patients", response_model=schemas.PatientResponse)
def add_patient(
    patient: schemas.PatientCreate,
    db: Session = Depends(get_db)
):
    new_patient = models.Patient(
        name=patient.name,
        age=patient.age,
        gender=patient.gender,
        blood_group=patient.blood_group,
        phone=patient.phone,
        email=patient.email,
        allergies=patient.allergies,
        medical_history=patient.medical_history
    )

    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)

    return new_patient


# Get All Patients
@app.get("/patients", response_model=list[schemas.PatientResponse])
def get_patients(db: Session = Depends(get_db)):
    return db.query(models.Patient).all()


# Get Patient by ID
@app.get("/patients/{patient_id}", response_model=schemas.PatientResponse)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db)
):
    patient = (
        db.query(models.Patient)
        .filter(models.Patient.id == patient_id)
        .first()
    )

    if patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    return patient


# =========================================================
# MEDICAL HISTORY
# =========================================================

# Add Medical History
@app.post(
    "/medical-history",
    response_model=schemas.MedicalHistoryResponse
)
def add_medical_history(
    history: schemas.MedicalHistoryCreate,
    db: Session = Depends(get_db)
):
    # Check patient exists
    patient = (
        db.query(models.Patient)
        .filter(models.Patient.id == history.patient_id)
        .first()
    )

    if patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    new_history = models.MedicalHistory(
        patient_id=history.patient_id,
        condition=history.condition,
        diagnosis_date=history.diagnosis_date,
        treatment=history.treatment,
        medications=history.medications,
        doctor_name=history.doctor_name,
        notes=history.notes
    )

    db.add(new_history)
    db.commit()
    db.refresh(new_history)

    return new_history


# View Medical History for a Patient
@app.get(
    "/patients/{patient_id}/medical-history",
    response_model=list[schemas.MedicalHistoryResponse]
)
def get_medical_history(
    patient_id: int,
    db: Session = Depends(get_db)
):
    # Check patient exists
    patient = (
        db.query(models.Patient)
        .filter(models.Patient.id == patient_id)
        .first()
    )

    if patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    histories = (
        db.query(models.MedicalHistory)
        .filter(
            models.MedicalHistory.patient_id == patient_id
        )
        .all()
    )

    return histories


# =========================================================
# MEDICAL REPORTS
# =========================================================

# Upload Medical Report
@app.post("/patients/{patient_id}/reports")
def upload_medical_report(
    patient_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Check patient exists
    patient = (
        db.query(models.Patient)
        .filter(models.Patient.id == patient_id)
        .first()
    )

    if patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    # Allowed file types
    allowed_types = [
        "application/pdf",
        "image/jpeg",
        "image/png"
    ]

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, JPG and PNG files are allowed"
        )

    # Create uploads folder
    os.makedirs("uploads", exist_ok=True)

    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    safe_filename = os.path.basename(file.filename)

    stored_filename = (
        f"{patient_id}_{timestamp}_{safe_filename}"
    )

    file_path = os.path.join(
        "uploads",
        stored_filename
    )

    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )

    # Save report information in database
    report = models.MedicalReport(
        patient_id=patient_id,
        report_name=safe_filename,
        file_name=stored_filename,
        file_path=file_path,
        file_type=file.content_type,
        upload_date=datetime.now().isoformat()
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    return {
        "message": "Medical report uploaded successfully",
        "report_id": report.id,
        "patient_id": patient_id,
        "file_name": report.report_name
    }


# View Previous Medical Reports
@app.get("/patients/{patient_id}/reports")
def get_patient_reports(
    patient_id: int,
    db: Session = Depends(get_db)
):
    # Check patient exists
    patient = (
        db.query(models.Patient)
        .filter(models.Patient.id == patient_id)
        .first()
    )

    if patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    reports = (
        db.query(models.MedicalReport)
        .filter(
            models.MedicalReport.patient_id == patient_id
        )
        .all()
    )

    return [
        {
            "id": report.id,
            "patient_id": report.patient_id,
            "report_name": report.report_name,
            "file_type": report.file_type,
            "upload_date": report.upload_date
        }
        for report in reports
    ]


# =========================================================
# DOWNLOAD MEDICAL REPORT
# =========================================================

@app.get("/reports/{report_id}/download")
def download_medical_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    # Find report
    report = (
        db.query(models.MedicalReport)
        .filter(
            models.MedicalReport.id == report_id
        )
        .first()
    )

    # Report doesn't exist
    if report is None:
        raise HTTPException(
            status_code=404,
            detail="Medical report not found"
        )

    # File doesn't exist
    if not os.path.exists(report.file_path):
        raise HTTPException(
            status_code=404,
            detail="Report file not found"
        )

    # Return file
    return FileResponse(
        path=report.file_path,
        filename=report.report_name,
        media_type=report.file_type
    )
# =========================================================
# HEALTH TIMELINE
# =========================================================

@app.get("/patients/{patient_id}/timeline")
def get_health_timeline(
    patient_id: int,
    db: Session = Depends(get_db)
):
    # Check patient exists
    patient = (
        db.query(models.Patient)
        .filter(models.Patient.id == patient_id)
        .first()
    )

    if patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    timeline = []

    # Get medical history
    histories = (
        db.query(models.MedicalHistory)
        .filter(
            models.MedicalHistory.patient_id == patient_id
        )
        .all()
    )

    for history in histories:
        timeline.append({
            "type": "medical_history",
            "date": history.diagnosis_date,
            "title": history.condition,
            "details": {
                "treatment": history.treatment,
                "medications": history.medications,
                "doctor_name": history.doctor_name,
                "notes": history.notes
            }
        })

    # Get medical reports
    reports = (
        db.query(models.MedicalReport)
        .filter(
            models.MedicalReport.patient_id == patient_id
        )
        .all()
    )

    for report in reports:
        timeline.append({
            "type": "medical_report",
            "date": report.upload_date,
            "title": report.report_name,
            "details": {
                "report_id": report.id,
                "file_type": report.file_type,
                "uploaded_file": report.file_name
            }
        })

    # Sort newest first
    timeline.sort(
        key=lambda event: event["date"] or "",
        reverse=True
    )

    return {
        "patient_id": patient_id,
        "patient_name": patient.name,
        "timeline": timeline
    }