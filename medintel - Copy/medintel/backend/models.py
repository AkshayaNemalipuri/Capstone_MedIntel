from sqlalchemy import Column, Integer, String, Text
from database import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(20), nullable=False)
    blood_group = Column(String(10))

    phone = Column(String(20))
    email = Column(String(100))

    allergies = Column(Text)
    medical_history = Column(Text)
class MedicalHistory(Base):
    __tablename__ = "medical_history"

    id = Column(Integer, primary_key=True, index=True)

    patient_id = Column(Integer, nullable=False)

    condition = Column(String(200), nullable=False)
    diagnosis_date = Column(String(20))
    treatment = Column(Text)
    medications = Column(Text)
    doctor_name = Column(String(100))
    notes = Column(Text)
class MedicalReport(Base):
    __tablename__ = "medical_reports"

    id = Column(Integer, primary_key=True, index=True)

    patient_id = Column(Integer, nullable=False)

    report_name = Column(String(200), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50))

    upload_date = Column(String(50), nullable=False)