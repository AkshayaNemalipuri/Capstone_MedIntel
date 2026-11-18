from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class PatientRegister(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    age: int = Field(ge=1, le=120)
    gender: str = Field(min_length=1, max_length=30)
    phone: Optional[str] = Field(default=None, max_length=30)
    blood_group: Optional[str] = Field(default=None, max_length=10)
    allergies: Optional[str] = None


class DoctorRegister(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    phone: Optional[str] = Field(default=None, max_length=30)
    registration_number: str = Field(min_length=2, max_length=100)
    specialization: str = Field(min_length=2, max_length=100)
    qualification: str = Field(min_length=2, max_length=100)
    experience: int = Field(ge=0, le=80)
    hospital: Optional[str] = Field(default=None, max_length=200)
    address: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class HistoryCreate(BaseModel):
    condition: str = Field(min_length=2, max_length=200)
    diagnosis_date: Optional[str] = None
    treatment: Optional[str] = None
    medications: Optional[str] = None
    doctor_name: Optional[str] = None
    notes: Optional[str] = None
