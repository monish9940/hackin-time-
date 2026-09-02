from typing import List
from fastapi import APIRouter, Depends
from app.database import get_db
from app.db_helpers import clean_docs
from app.schemas import AuditLogResponse
from app.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[AuditLogResponse])
def get_audit_logs(db = Depends(get_db), current_user: dict = Depends(get_current_user)):
    logs = list(db.audit_logs.find().sort("timestamp", -1).limit(100))
    return clean_docs(logs)
