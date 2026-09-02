import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    organization = Column(String, default="General Hospital")
    specialization = Column(String, default="General Physician")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, unique=True, index=True, nullable=False) # e.g. CB-2026-1042
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)
    blood_group = Column(String, default="O+")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    documents = relationship("Document", back_populates="patient", cascade="all, delete-orphan")
    medical_records = relationship("MedicalRecord", back_populates="patient", cascade="all, delete-orphan")
    medications = relationship("Medication", back_populates="patient", cascade="all, delete-orphan")
    lab_results = relationship("LabResult", back_populates="patient", cascade="all, delete-orphan")
    allergies = relationship("Allergy", back_populates="patient", cascade="all, delete-orphan")
    timeline_events = relationship("TimelineEvent", back_populates="patient", cascade="all, delete-orphan")
    ai_insights = relationship("AIInsight", back_populates="patient", cascade="all, delete-orphan")
    doctor_notes = relationship("DoctorNote", back_populates="patient", cascade="all, delete-orphan")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    document_type = Column(String, default="Medical Record")
    hospital = Column(String, default="Unknown Hospital")
    doctor_name = Column(String, default="Unassigned")
    extracted_text = Column(Text, nullable=True)
    structured_json = Column(Text, nullable=True)
    upload_date = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="processed") # processed, processing, failed

    patient = relationship("Patient", back_populates="documents")

class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    record_date = Column(String, nullable=False)
    hospital = Column(String, nullable=True)
    doctor_name = Column(String, nullable=True)
    diagnosis = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

    patient = relationship("Patient", back_populates="medical_records")

class Medication(Base):
    __tablename__ = "medications"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    name = Column(String, nullable=False)
    generic_name = Column(String, nullable=True)
    dosage = Column(String, nullable=False)
    frequency = Column(String, default="Once daily")
    prescribed_by = Column(String, nullable=True)
    start_date = Column(String, nullable=False)
    end_date = Column(String, nullable=True)
    status = Column(String, default="Active") # Active, Changed, Discontinued
    dosage_history = Column(String, nullable=True) # e.g. "500mg -> 1000mg"

    patient = relationship("Patient", back_populates="medications")

class LabResult(Base):
    __tablename__ = "lab_results"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    test_name = Column(String, nullable=False)
    test_value = Column(String, nullable=False)
    unit = Column(String, nullable=True)
    reference_range = Column(String, nullable=True)
    test_date = Column(String, nullable=False)

    patient = relationship("Patient", back_populates="lab_results")

class Allergy(Base):
    __tablename__ = "allergies"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    allergen = Column(String, nullable=False)
    severity = Column(String, default="High")
    reaction = Column(String, nullable=True)
    documented_date = Column(String, nullable=False)

    patient = relationship("Patient", back_populates="allergies")

class TimelineEvent(Base):
    __tablename__ = "timeline_events"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    date = Column(String, nullable=False)
    category = Column(String, nullable=False) # Consultation, Lab Report, Prescription, Allergy
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    hospital = Column(String, nullable=True)
    badge_color = Column(String, default="blue") # blue, green, orange, red

    patient = relationship("Patient", back_populates="timeline_events")

class AIInsight(Base):
    __tablename__ = "ai_insights"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    category = Column(String, nullable=False) # medication_change, allergy_conflict, missing_info, trend
    insight_type = Column(String, nullable=True) # Inconsistency, Missing Info, Medication Change
    severity = Column(String, default="medium") # high, medium, low
    priority = Column(String, nullable=False) # Critical, High, Medium, Low
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    action_required = Column(Text, nullable=False)
    status = Column(String, default="pending") # pending, reviewed, dismissed
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    patient = relationship("Patient", back_populates="ai_insights")

class DoctorNote(Base):
    __tablename__ = "doctor_notes"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    author_name = Column(String, nullable=False)
    note = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    patient = relationship("Patient", back_populates="doctor_notes")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, nullable=False)
    action = Column(String, nullable=False)
    details = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
