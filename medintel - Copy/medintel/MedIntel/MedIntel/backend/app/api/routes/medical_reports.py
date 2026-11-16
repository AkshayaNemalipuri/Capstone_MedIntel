import os
import shutil

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db


router = APIRouter(
    prefix="/medical-reports",
    tags=["Medical Reports"],
)


# ============================================================
# UPLOAD DIRECTORY
# ============================================================

UPLOAD_DIR = "uploads/medical_reports"

os.makedirs(UPLOAD_DIR, exist_ok=True)


# ============================================================
# UPLOAD MEDICAL REPORT
# ============================================================

@router.post(
    "/upload",
    response_model=schemas.MedicalReportResponse,
)
def upload_medical_report(
    patient_id: int = Form(...),
    report_name: str = Form(...),
    report_type: str | None = Form(None),
    report_date: str | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # Check patient exists
    patient = (
        db.query(models.PatientProfile)
        .filter(models.PatientProfile.id == patient_id)
        .first()
    )

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found",
        )

    # Validate file
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file selected",
        )

    # Create a safe unique filename
    filename = os.path.basename(file.filename)

    file_path = os.path.join(
        UPLOAD_DIR,
        filename,
    )

    # Prevent overwriting an existing file
    base_name, extension = os.path.splitext(filename)
    counter = 1

    while os.path.exists(file_path):
        filename = f"{base_name}_{counter}{extension}"
        file_path = os.path.join(
            UPLOAD_DIR,
            filename,
        )
        counter += 1

    # Save uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Save report information in database
    report = models.MedicalReport(
        patient_id=patient_id,
        report_name=report_name,
        report_type=report_type,
        file_name=filename,
        file_path=file_path,
        report_date=report_date,
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    return report


# ============================================================
# VIEW PREVIOUS MEDICAL REPORTS
# ============================================================

@router.get(
    "/patient/{patient_id}",
    response_model=list[schemas.MedicalReportResponse],
)
def get_medical_reports(
    patient_id: int,
    db: Session = Depends(get_db),
):
    patient = (
        db.query(models.PatientProfile)
        .filter(models.PatientProfile.id == patient_id)
        .first()
    )

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found",
        )

    return (
        db.query(models.MedicalReport)
        .filter(models.MedicalReport.patient_id == patient_id)
        .order_by(models.MedicalReport.uploaded_at.desc())
        .all()
    )


# ============================================================
# DOWNLOAD MEDICAL REPORT
# ============================================================

@router.get(
    "/download/{report_id}",
)
def download_medical_report(
    report_id: int,
    db: Session = Depends(get_db),
):
    report = (
        db.query(models.MedicalReport)
        .filter(models.MedicalReport.id == report_id)
        .first()
    )

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Medical report not found",
        )

    if not os.path.exists(report.file_path):
        raise HTTPException(
            status_code=404,
            detail="Report file not found",
        )

    return FileResponse(
        path=report.file_path,
        filename=report.file_name,
        media_type="application/octet-stream",
    )


# ============================================================
# DELETE MEDICAL REPORT
# ============================================================

@router.delete("/{report_id}")
def delete_medical_report(
    report_id: int,
    db: Session = Depends(get_db),
):
    report = (
        db.query(models.MedicalReport)
        .filter(models.MedicalReport.id == report_id)
        .first()
    )

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Medical report not found",
        )

    # Delete physical file
    if os.path.exists(report.file_path):
        os.remove(report.file_path)

    # Delete database record
    db.delete(report)
    db.commit()

    return {
        "message": "Medical report deleted successfully"
    }