import datetime
from typing import List, Union
from fastapi import APIRouter, Depends
from app.database import get_db
from app.db_helpers import clean_doc, clean_docs, get_next_sequence_value
from app.schemas import DoctorNoteCreate, DoctorNoteResponse
from app.auth import get_current_user

router = APIRouter()

@router.get("/{patient_id}", response_model=List[DoctorNoteResponse])
def get_notes(patient_id: Union[int, str], db = Depends(get_db), current_user: dict = Depends(get_current_user)):
    p_id = int(patient_id) if str(patient_id).isdigit() else patient_id
    query = {"$or": [{"patient_id": p_id}, {"patient_id": str(patient_id)}]}
    notes = list(db.doctor_notes.find(query).sort("created_at", -1))
    return clean_docs(notes)

@router.post("/{patient_id}", response_model=DoctorNoteResponse)
def add_note(patient_id: Union[int, str], note_in: DoctorNoteCreate, db = Depends(get_db), current_user: dict = Depends(get_current_user)):
    p_id = int(patient_id) if str(patient_id).isdigit() else patient_id
    note_doc = {
        "id": get_next_sequence_value(db, "doctor_notes"),
        "patient_id": p_id,
        "author_name": current_user.get("full_name", "Doctor"),
        "note": note_in.note,
        "created_at": datetime.datetime.utcnow().isoformat()
    }
    db.doctor_notes.insert_one(note_doc)
    
    db.audit_logs.insert_one({
        "id": get_next_sequence_value(db, "audit_logs"),
        "user_email": current_user["email"],
        "action": "Add Note",
        "details": "Added a new clinical note",
        "timestamp": datetime.datetime.utcnow().isoformat()
    })
    
    return clean_doc(note_doc)
