import datetime
from typing import Union
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from app.database import get_db
from app.db_helpers import clean_doc, get_next_sequence_value
from app.auth import get_current_user
from app.services.pdf_export import generate_patient_summary_pdf

router = APIRouter()

@router.get("/{patient_id}/export")
def export_patient_summary(patient_id: Union[int, str], db = Depends(get_db), current_user: dict = Depends(get_current_user)):
    p_id = int(patient_id) if str(patient_id).isdigit() else patient_id
    patient = db.patients.find_one({"$or": [{"id": p_id}, {"patient_id": str(patient_id)}]})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
        
    pdf_path = generate_patient_summary_pdf(db, patient)
    
    db.audit_logs.insert_one({
        "id": get_next_sequence_value(db, "audit_logs"),
        "user_email": current_user["email"],
        "action": "Export Summary",
        "details": f"Exported PDF summary for {patient.get('name')}",
        "timestamp": datetime.datetime.utcnow().isoformat()
    })
    
    return FileResponse(pdf_path, media_type="application/pdf", filename=f"CareBridge_Summary_{patient.get('patient_id')}.pdf")
