from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


# ============================================================
# COMMON CONFIG
# ============================================================

class ORMBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ============================================================
# PATIENT PROFILE
# ============================================================

class PatientProfileBase(BaseModel):
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    blood_group: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None


class PatientProfileCreate(PatientProfileBase):
    pass


class PatientProfileResponse(PatientProfileBase):
    id: int
    user_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# AUTHENTICATION
# ============================================================

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Optional[str] = "patient"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Optional["UserResponse"] = None


class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class RoleAssignmentRequest(BaseModel):
    role: str


# ============================================================
# USER
# ============================================================

class UserResponse(ORMBaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    is_active: Optional[bool] = True
    created_at: Optional[datetime] = None


# ============================================================
# FORGOT / RESET PASSWORD
# ============================================================

class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class PasswordResetResponse(BaseModel):
    message: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


# ============================================================
# MEDICAL HISTORY
# ============================================================

class MedicalHistoryCreate(BaseModel):
    patient_id: int
    condition: Optional[str] = None
    diagnosis: Optional[str] = None
    medications: Optional[str] = None
    allergies: Optional[str] = None
    surgeries: Optional[str] = None
    notes: Optional[str] = None
    diagnosed_date: Optional[str] = None


class MedicalHistoryUpdate(BaseModel):
    condition: Optional[str] = None
    diagnosis: Optional[str] = None
    medications: Optional[str] = None
    allergies: Optional[str] = None
    surgeries: Optional[str] = None
    notes: Optional[str] = None
    diagnosed_date: Optional[str] = None


class MedicalHistoryResponse(ORMBaseModel):
    id: int
    patient_id: int
    condition: Optional[str] = None
    diagnosis: Optional[str] = None
    medications: Optional[str] = None
    allergies: Optional[str] = None
    surgeries: Optional[str] = None
    notes: Optional[str] = None
    diagnosed_date: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ============================================================
# MEDICAL REPORTS
# ============================================================

class MedicalReportResponse(ORMBaseModel):
    id: int
    patient_id: int
    file_name: Optional[str] = None
    file_path: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    uploaded_at: Optional[datetime] = None


# ============================================================
# HEALTH TIMELINE
# ============================================================

class HealthTimelineCreate(BaseModel):
    patient_id: int
    event_type: str
    title: Optional[str] = None
    description: Optional[str] = None
    event_date: Optional[str] = None


class HealthTimelineUpdate(BaseModel):
    event_type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    event_date: Optional[str] = None


class HealthTimelineResponse(ORMBaseModel):
    id: int
    patient_id: int
    event_type: str
    title: Optional[str] = None
    description: Optional[str] = None
    event_date: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ============================================================
# HEALTH CHECK
# ============================================================

class HealthResponse(BaseModel):
    status: str


# ============================================================
# DASHBOARD
# ============================================================

class DashboardResponse(BaseModel):
    message: Optional[str] = None
    user: Optional[UserResponse] = None
    profile: Optional[PatientProfileResponse] = None
    medical_history_count: Optional[int] = 0
    medical_reports_count: Optional[int] = 0
    timeline_events_count: Optional[int] = 0


# ============================================================
# FILE UPLOAD
# ============================================================

class UploadMedicalReportResponse(BaseModel):
    message: str
    report_id: Optional[int] = None
    file_name: Optional[str] = None


# ============================================================
# FORWARD REFERENCES
# ============================================================

AuthResponse.model_rebuild()