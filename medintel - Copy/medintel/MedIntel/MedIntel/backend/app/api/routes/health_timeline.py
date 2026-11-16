from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db


router = APIRouter(
    prefix="/health-timeline",
    tags=["Health Timeline"],
)


# ============================================================
# ADD TIMELINE EVENT
# ============================================================

@router.post(
    "/",
    response_model=schemas.HealthTimelineResponse,
)
def add_timeline_event(
    event: schemas.HealthTimelineCreate,
    db: Session = Depends(get_db),
):
    patient = (
        db.query(models.PatientProfile)
        .filter(models.PatientProfile.id == event.patient_id)
        .first()
    )

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found",
        )

    new_event = models.HealthTimeline(
        patient_id=event.patient_id,
        event_type=event.event_type,
        title=event.title,
        description=event.description,
        event_date=event.event_date or datetime.now(),
    )

    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    return new_event


# ============================================================
# VIEW HEALTH TIMELINE
# ============================================================

@router.get(
    "/patient/{patient_id}",
    response_model=list[schemas.HealthTimelineResponse],
)
def get_health_timeline(
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
        db.query(models.HealthTimeline)
        .filter(models.HealthTimeline.patient_id == patient_id)
        .order_by(models.HealthTimeline.event_date.desc())
        .all()
    )


# ============================================================
# UPDATE TIMELINE EVENT
# ============================================================

@router.put(
    "/{event_id}",
    response_model=schemas.HealthTimelineResponse,
)
def update_timeline_event(
    event_id: int,
    event: schemas.HealthTimelineUpdate,
    db: Session = Depends(get_db),
):
    existing_event = (
        db.query(models.HealthTimeline)
        .filter(models.HealthTimeline.id == event_id)
        .first()
    )

    if not existing_event:
        raise HTTPException(
            status_code=404,
            detail="Timeline event not found",
        )

    update_data = event.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(existing_event, field, value)

    db.commit()
    db.refresh(existing_event)

    return existing_event


# ============================================================
# DELETE TIMELINE EVENT
# ============================================================

@router.delete("/{event_id}")
def delete_timeline_event(
    event_id: int,
    db: Session = Depends(get_db),
):
    existing_event = (
        db.query(models.HealthTimeline)
        .filter(models.HealthTimeline.id == event_id)
        .first()
    )

    if not existing_event:
        raise HTTPException(
            status_code=404,
            detail="Timeline event not found",
        )

    db.delete(existing_event)
    db.commit()

    return {
        "message": "Timeline event deleted successfully"
    }