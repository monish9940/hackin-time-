import datetime
from typing import List, Optional, Union, Any
from pydantic import BaseModel, EmailStr

# Auth Schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    confirm_password: Optional[str] = None
    full_name: str
    organization: Optional[str] = "General Hospital"
    specialization: Optional[str] = "General Physician"
    role: Optional[str] = "clinician"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: Union[int, str]
    email: str
    full_name: str
    organization: str
    specialization: str
    role: str = "clinician"
    is_active: bool = True
    created_at: Optional[Union[datetime.datetime, str]] = None

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Patient Schemas
class PatientCreate(BaseModel):
    patient_id: str
    name: str
    age: int
    gender: str
    blood_group: Optional[str] = "O+"

class PatientResponse(BaseModel):
    id: Union[int, str]
    patient_id: str
    name: str
    age: int
    gender: str
    blood_group: str
    created_at: Optional[Union[datetime.datetime, str]] = None
    active_medications_count: Optional[int] = 0
    records_count: Optional[int] = 0
    review_status: Optional[str] = "Normal"
    review_priority_score: Optional[int] = 50

    class Config:
        orm_mode = True

# Document Schemas
class DocumentResponse(BaseModel):
    id: Union[int, str]
    patient_id: Union[int, str]
    file_name: str
    document_type: str = "Medical Record"
    hospital: Optional[str] = "City Hospital"
    doctor_name: Optional[str] = ""
    extracted_text: Optional[str] = None
    structured_json: Optional[str] = None
    upload_date: Optional[Union[datetime.datetime, str]] = None
    status: str = "uploaded"

    class Config:
        orm_mode = True

# Medication Schemas
class MedicationResponse(BaseModel):
    id: Union[int, str]
    patient_id: Union[int, str]
    name: str
    generic_name: Optional[str] = ""
    dosage: str
    frequency: str
    prescribed_by: Optional[str] = "Unknown Doctor"
    start_date: str
    end_date: Optional[str] = None
    status: str = "Active"
    dosage_history: Optional[str] = None

    class Config:
        orm_mode = True

# Lab Result Schemas
class LabResultResponse(BaseModel):
    id: Union[int, str]
    patient_id: Union[int, str]
    test_name: str
    test_value: str
    unit: Optional[str] = ""
    reference_range: Optional[str] = ""
    test_date: str

    class Config:
        orm_mode = True

# Allergy Schemas
class AllergyResponse(BaseModel):
    id: Union[int, str]
    patient_id: Union[int, str]
    allergen: str
    severity: str
    reaction: Optional[str] = ""
    documented_date: str

    class Config:
        orm_mode = True

# Timeline Event Schemas
class TimelineEventResponse(BaseModel):
    id: Union[int, str]
    patient_id: Union[int, str]
    date: str
    category: str
    title: str
    description: str
    hospital: Optional[str] = "City Hospital"
    badge_color: str = "blue"

    class Config:
        orm_mode = True

# AI Insight Schemas
class AIInsightResponse(BaseModel):
    id: Union[int, str]
    patient_id: Union[int, str]
    category: str
    insight_type: Optional[str] = ""
    severity: Optional[str] = "medium"
    priority: str = "Medium"
    title: str
    description: str
    action_required: str
    status: str = "pending"
    created_at: Optional[Union[datetime.datetime, str]] = None

    class Config:
        orm_mode = True

# Doctor Note Schemas
class DoctorNoteCreate(BaseModel):
    note: str

class DoctorNoteResponse(BaseModel):
    id: Union[int, str]
    patient_id: Union[int, str]
    author_name: str
    note: str
    created_at: Optional[Union[datetime.datetime, str]] = None

    class Config:
        orm_mode = True

# Audit Log Schema
class AuditLogResponse(BaseModel):
    id: Union[int, str]
    user_email: str
    action: str
    details: str
    timestamp: Optional[Union[datetime.datetime, str]] = None

    class Config:
        orm_mode = True
