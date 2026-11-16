from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.routes.auth import get_current_user
from app.database import get_db
from app.models import PatientProfile, User
from app.schemas import PatientProfileCreate, PatientProfileResponse


router = APIRouter()


# ============================================================
# TEST PATIENT MODULE
# ============================================================

@router.get("/test")
def patient_module_test(
    current_user: User = Depends(get_current_user),
):
    return {
        "message": "Patient module is working",
        "user_id": current_user.id,
        "user_name": current_user.full_name,
    }


# ============================================================
# ADD / UPDATE PATIENT DETAILS
# ============================================================

@router.post(
    "/profile",
    response_model=PatientProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_patient_profile(
    request: PatientProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing_profile = db.scalar(
        select(PatientProfile).where(
            PatientProfile.user_id == current_user.id
        )
    )

    if existing_profile:
        existing_profile.date_of_birth = request.date_of_birth
        existing_profile.gender = request.gender
        existing_profile.phone = request.phone
        existing_profile.blood_group = request.blood_group
        existing_profile.address = request.address
        existing_profile.emergency_contact = request.emergency_contact

        db.commit()
        db.refresh(existing_profile)

        return existing_profile

    patient_profile = PatientProfile(
        user_id=current_user.id,
        date_of_birth=request.date_of_birth,
        gender=request.gender,
        phone=request.phone,
        blood_group=request.blood_group,
        address=request.address,
        emergency_contact=request.emergency_contact,
    )

    db.add(patient_profile)
    db.commit()
    db.refresh(patient_profile)

    return patient_profile


# ============================================================
# VIEW PATIENT DETAILS
# ============================================================

@router.get(
    "/profile",
    response_model=PatientProfileResponse,
)
def get_patient_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    patient_profile = db.scalar(
        select(PatientProfile).where(
            PatientProfile.user_id == current_user.id
        )
    )

    if not patient_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found",
        )

    return patient_profile