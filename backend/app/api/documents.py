import os
import shutil
import datetime
from typing import List, Union
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from app.database import get_db
from app.db_helpers import clean_doc, clean_docs, get_next_sequence_value
from app.schemas import DocumentResponse
from app.config import settings
from app.auth import get_current_user

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    patient_id: Union[int, str] = Form(...),
    file: UploadFile = File(...),
    db = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Allowed formats: PDF, JPG, JPEG, PNG."
        )
        
    p_id = int(patient_id) if str(patient_id).isdigit() else patient_id
    patient = db.patients.find_one({"$or": [{"id": p_id}, {"patient_id": str(patient_id)}]})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
        
    file_path = os.path.join(settings.UPLOAD_DIR, f"{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}")
    
    file_size = 0
    with open(file_path, "wb") as buffer:
        while chunk := await file.read(1024 * 1024):
            file_size += len(chunk)
            if file_size > MAX_FILE_SIZE:
                buffer.close()
                if os.path.exists(file_path):
                    os.remove(file_path)
                raise HTTPException(
                    status_code=413,
                    detail="File size exceeds maximum allowed limit of 10 MB."
                )
            buffer.write(chunk)
        
    doc_id = get_next_sequence_value(db, "documents")
    doc_data = {
        "id": doc_id,
        "patient_id": patient["id"],
        "file_name": file.filename,
        "file_path": file_path,
        "document_type": "Medical Record",
        "hospital": "Uploaded Record",
        "doctor_name": "",
        "upload_date": datetime.datetime.utcnow().isoformat(),
        "status": "uploaded"
    }
    
    db.documents.insert_one(doc_data)
    
    # Audit log
    db.audit_logs.insert_one({
        "id": get_next_sequence_value(db, "audit_logs"),
        "user_email": current_user["email"],
        "action": "Upload Document",
        "details": f"Uploaded {file.filename} for patient {patient['name']}",
        "timestamp": datetime.datetime.utcnow().isoformat()
    })
    
    return clean_doc(doc_data)

@router.get("/", response_model=List[DocumentResponse])
def get_documents(patient_id: Union[int, str] = None, db = Depends(get_db), current_user: dict = Depends(get_current_user)):
    query = {}
    if patient_id:
        p_id = int(patient_id) if str(patient_id).isdigit() else patient_id
        query = {"$or": [{"patient_id": p_id}, {"patient_id": str(patient_id)}]}
    docs = list(db.documents.find(query))
    return clean_docs(docs)

@router.get("/{id}", response_model=DocumentResponse)
def get_document(id: Union[int, str], db = Depends(get_db), current_user: dict = Depends(get_current_user)):
    doc_id = int(id) if str(id).isdigit() else id
    doc = db.documents.find_one({"$or": [{"id": doc_id}, {"_id": str(id)}]})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return clean_doc(doc)

@router.delete("/{id}")
def delete_document(id: Union[int, str], db = Depends(get_db), current_user: dict = Depends(get_current_user)):
    doc_id = int(id) if str(id).isdigit() else id
    doc = db.documents.find_one({"$or": [{"id": doc_id}, {"_id": str(id)}]})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    db.documents.delete_one({"_id": doc["_id"]})
    if doc.get("file_path") and os.path.exists(doc["file_path"]):
        try:
            os.remove(doc["file_path"])
        except Exception:
            pass
            
    db.audit_logs.insert_one({
        "id": get_next_sequence_value(db, "audit_logs"),
        "user_email": current_user["email"],
        "action": "Delete Document",
        "details": f"Deleted document {doc.get('file_name')}",
        "timestamp": datetime.datetime.utcnow().isoformat()
    })
    return {"message": "Document deleted successfully"}

