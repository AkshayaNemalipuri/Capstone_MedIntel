from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas

router = APIRouter(
    prefix="/medical-history",
    tags=["Medical History"],
)


# ============================================================
# ADD MEDICAL HISTORY
# ============================================================

@router.post("/", response_model=schemas.MedicalHistoryResponse)
def add_medical_history(
    history: schemas.MedicalHistoryCreate,
    db: Session = Depends(get_db),
):
    patient = (
        db.query(models.PatientProfile)
        .filter(models.PatientProfile.id == history.patient_id)
        .first()
    )

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found",
        )

    new_history = models.MedicalHistory(
        patient_id=history.patient_id,
        condition=history.condition,
        diagnosis_date=history.diagnosis_date,
        treatment=history.treatment,
        medications=history.medications,
        allergies=history.allergies,
        notes=history.notes,
    )

    db.add(new_history)
    db.commit()
    db.refresh(new_history)

    return new_history


# ============================================================
# VIEW MEDICAL HISTORY
# ============================================================

@router.get(
    "/patient/{patient_id}",
    response_model=list[schemas.MedicalHistoryResponse],
)
def get_medical_history(
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
        db.query(models.MedicalHistory)
        .filter(models.MedicalHistory.patient_id == patient_id)
        .order_by(models.MedicalHistory.created_at.desc())
        .all()
    )


# ============================================================
# UPDATE MEDICAL HISTORY
# ============================================================

@router.put(
    "/{history_id}",
    response_model=schemas.MedicalHistoryResponse,
)
def update_medical_history(
    history_id: int,
    history: schemas.MedicalHistoryUpdate,
    db: Session = Depends(get_db),
):
    existing_history = (
        db.query(models.MedicalHistory)
        .filter(models.MedicalHistory.id == history_id)
        .first()
    )

    if not existing_history:
        raise HTTPException(
            status_code=404,
            detail="Medical history record not found",
        )

    update_data = history.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(existing_history, field, value)

    db.commit()
    db.refresh(existing_history)

    return existing_history


# ============================================================
# DELETE MEDICAL HISTORY
# ============================================================

@router.delete("/{history_id}")
def delete_medical_history(
    history_id: int,
    db: Session = Depends(get_db),
):
    existing_history = (
        db.query(models.MedicalHistory)
        .filter(models.MedicalHistory.id == history_id)
        .first()
    )

    if not existing_history:
        raise HTTPException(
            status_code=404,
            detail="Medical history record not found",
        )

    db.delete(existing_history)
    db.commit()

    return {
        "message": "Medical history deleted successfully"
    }