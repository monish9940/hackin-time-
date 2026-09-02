from typing import List, Union
from fastapi import APIRouter, Depends
from app.database import get_db
from app.db_helpers import clean_docs
from app.schemas import TimelineEventResponse
from app.auth import get_current_user

router = APIRouter()

@router.get("/{patient_id}", response_model=List[TimelineEventResponse])
def get_timeline(patient_id: Union[int, str], db = Depends(get_db), current_user: dict = Depends(get_current_user)):
    p_id = int(patient_id) if str(patient_id).isdigit() else patient_id
    query = {"$or": [{"patient_id": p_id}, {"patient_id": str(patient_id)}]}
    events = list(db.timeline_events.find(query).sort("date", -1))
    return clean_docs(events)
