import datetime
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Union
from app.database import get_db
from app.db_helpers import clean_doc, clean_docs, get_next_sequence_value
from app.schemas import PatientResponse, PatientCreate, TimelineEventResponse, MedicationResponse
from app.auth import get_current_user
from app.agents.priority_engine import PriorityEngine

router = APIRouter()
priority_engine = PriorityEngine()

def calculate_patient_priority(db, patient_db_id) -> int:
    insights = list(db.ai_insights.find({
        "patient_id": patient_db_id,
        "status": "pending"
    }))
    score = 0
    for insight in insights:
        p = insight.get("priority", "Medium")
        if p == "Critical": score += 50
        elif p == "High": score += 30
        elif p == "Medium": score += 15
        elif p == "Low": score += 5
    return min(score, 100)

@router.get("", response_model=List[PatientResponse])
@router.get("/", response_model=List[PatientResponse])
def get_patients(db = Depends(get_db), current_user: dict = Depends(get_current_user)):
    patients = list(db.patients.find())
    result = []
    for p in patients:
        p_id = p.get("id")
        active_meds = db.medications.count_documents({
            "patient_id": p_id,
            "status": {"$ne": "Discontinued"}
        })
        records_count = db.documents.count_documents({"patient_id": p_id})
        score = calculate_patient_priority(db, p_id)
        
        status = "Normal"
        if score > 70:
            status = "Critical Review"
        elif score > 30:
            status = "Review Needed"
            
        doc = clean_doc(p)
        doc["active_medications_count"] = active_meds
        doc["records_count"] = records_count
        doc["review_status"] = status
        doc["review_priority_score"] = score
        result.append(doc)
        
    return result

@router.post("", response_model=PatientResponse)
@router.post("/", response_model=PatientResponse)
def create_patient(patient_in: PatientCreate, db = Depends(get_db), current_user: dict = Depends(get_current_user)):
    existing = db.patients.find_one({"patient_id": patient_in.patient_id})
    if existing:
        raise HTTPException(status_code=400, detail="Patient ID already exists")
        
    p_id = get_next_sequence_value(db, "patients")
    patient_doc = {
        "id": p_id,
        "patient_id": patient_in.patient_id,
        "name": patient_in.name,
        "age": patient_in.age,
        "gender": patient_in.gender,
        "blood_group": patient_in.blood_group or "O+",
        "created_at": datetime.datetime.utcnow().isoformat()
    }
    db.patients.insert_one(patient_doc)
    
    db.audit_logs.insert_one({
        "id": get_next_sequence_value(db, "audit_logs"),
        "user_email": current_user["email"],
        "action": "Create Patient",
        "details": f"Created patient record for {patient_in.name} ({patient_in.patient_id})",
        "timestamp": datetime.datetime.utcnow().isoformat()
    })
    
    doc = clean_doc(patient_doc)
    doc["active_medications_count"] = 0
    doc["records_count"] = 0
    doc["review_status"] = "Normal"
    doc["review_priority_score"] = 0
    return doc

@router.get("/{id}", response_model=PatientResponse)
def get_patient(id: Union[int, str], db = Depends(get_db), current_user: dict = Depends(get_current_user)):
    query = {"$or": [{"id": id}, {"patient_id": str(id)}]}
    if str(id).isdigit():
        query["$or"].append({"id": int(id)})
        
    p = db.patients.find_one(query)
    if not p:
        raise HTTPException(status_code=404, detail="Patient not found")
        
    p_id = p.get("id")
    active_meds = db.medications.count_documents({
        "patient_id": p_id,
        "status": {"$ne": "Discontinued"}
    })
    records_count = db.documents.count_documents({"patient_id": p_id})
    score = calculate_patient_priority(db, p_id)
    
    status = "Normal"
    if score > 70:
        status = "Critical Review"
    elif score > 30:
        status = "Review Needed"
        
    doc = clean_doc(p)
    doc["active_medications_count"] = active_meds
    doc["records_count"] = records_count
    doc["review_status"] = status
    doc["review_priority_score"] = score
    return doc

@router.put("/{id}", response_model=PatientResponse)
def update_patient(id: Union[int, str], patient_in: PatientCreate, db = Depends(get_db), current_user: dict = Depends(get_current_user)):
    query = {"$or": [{"id": id}, {"patient_id": str(id)}]}
    if str(id).isdigit():
        query["$or"].append({"id": int(id)})
        
    p = db.patients.find_one(query)
    if not p:
        raise HTTPException(status_code=404, detail="Patient not found")
        
    update_data = {
        "name": patient_in.name,
        "age": patient_in.age,
        "gender": patient_in.gender,
        "blood_group": patient_in.blood_group or p.get("blood_group", "O+")
    }
    db.patients.update_one({"_id": p["_id"]}, {"$set": update_data})
    
    p.update(update_data)
    p_id = p.get("id")
    active_meds = db.medications.count_documents({"patient_id": p_id, "status": {"$ne": "Discontinued"}})
    records_count = db.documents.count_documents({"patient_id": p_id})
    score = calculate_patient_priority(db, p_id)
    
    doc = clean_doc(p)
    doc["active_medications_count"] = active_meds
    doc["records_count"] = records_count
    doc["review_status"] = "Normal" if score <= 30 else ("Review Needed" if score <= 70 else "Critical Review")
    doc["review_priority_score"] = score
    return doc



