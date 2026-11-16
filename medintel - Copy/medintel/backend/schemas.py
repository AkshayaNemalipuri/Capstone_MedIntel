from pydantic import BaseModel
from typing import Optional


class PatientCreate(BaseModel):
    name: str
    age: int
    gender: str
    blood_group: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    allergies: Optional[str] = None
    medical_history: Optional[str] = None


class PatientResponse(PatientCreate):
    id: int

    class Config:
        from_attributes = True
class MedicalHistoryCreate(BaseModel):
    patient_id: int
    condition: str
    diagnosis_date: Optional[str] = None
    treatment: Optional[str] = None
    medications: Optional[str] = None
    doctor_name: Optional[str] = None
    notes: Optional[str] = None


class MedicalHistoryResponse(MedicalHistoryCreate):
    id: int

    class Config:
        from_attributes = True