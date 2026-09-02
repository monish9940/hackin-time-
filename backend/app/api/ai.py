import json
import datetime
import logging
import traceback
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Union
from app.database import get_db
from app.db_helpers import clean_doc, clean_docs, get_next_sequence_value
from app.schemas import AIInsightResponse
from app.auth import get_current_user
from app.services.ocr import extract_text_from_file
from app.agents import ExtractionAgent, TimelineAgent, ConsistencyAgent, MissingInfoAgent, PriorityEngine

logger = logging.getLogger("carebridge")
router = APIRouter()


extraction_agent = ExtractionAgent()
timeline_agent = TimelineAgent()
consistency_agent = ConsistencyAgent()
missing_info_agent = MissingInfoAgent()
priority_engine = PriorityEngine()

async def process_document_pipeline(document_id: Union[int, str], db, user_email: str):
    doc_id = int(document_id) if str(document_id).isdigit() else document_id
    doc = db.documents.find_one({"id": doc_id})
    if not doc:
        print(f"DOCUMENT PROCESSING FAILED - Document id={doc_id} not found in MongoDB.")
        return
        
    patient_id = doc["patient_id"]
    p_id = int(patient_id) if str(patient_id).isdigit() else patient_id
    
    print("\n" + "="*60)
    print("DOCUMENT PROCESSING START")
    print("DOCUMENT ID:", doc_id)
    print("PATIENT ID:", p_id)
    print("="*60)
    
    try:
        # Step 1: OCR / Text Extraction
        db.documents.update_one({"id": doc_id}, {"$set": {"status": "extracting_text"}})
        try:
            extracted_text = extract_text_from_file(doc.get("file_path", ""))
        except Exception as ocr_err:
            error_msg = str(ocr_err) if str(ocr_err) else "Text could not be reliably extracted. Manual review required."
            db.documents.update_one({"id": doc_id}, {"$set": {
                "status": "failed",
                "error_message": "Text could not be reliably extracted. Manual review required.",
                "details": error_msg
            }})
            db.audit_logs.insert_one({
                "id": get_next_sequence_value(db, "audit_logs"),
                "user_email": user_email,
                "action": "OCR Extraction Failed",
                "details": f"Failed extraction for {doc.get('file_name')}: {error_msg}",
                "timestamp": datetime.datetime.utcnow().isoformat()
            })
            print("OCR EXTRACTION FAILED:", repr(ocr_err))
            traceback.print_exc()
            return

        print("EXTRACTED TEXT LENGTH:", len(extracted_text))
        print("EXTRACTED TEXT PREVIEW:", extracted_text[:300].replace("\n", " "))
        
        db.documents.update_one({"id": doc_id}, {"$set": {
            "extracted_text": extracted_text,
            "text": extracted_text
        }})
        
        db.audit_logs.insert_one({
            "id": get_next_sequence_value(db, "audit_logs"),
            "user_email": user_email,
            "action": "OCR Extraction",
            "details": f"Extracted text for {doc.get('file_name')}",
            "timestamp": datetime.datetime.utcnow().isoformat()
        })
        
        # Step 2: Extraction Agent
        db.documents.update_one({"id": doc_id}, {"$set": {"status": "ai_extraction"}})
        print("ENTITY EXTRACTION START")
        structured_data = await extraction_agent.analyze(extracted_text)
        
        diagnoses = structured_data.get("diagnoses", [])
        medications = structured_data.get("medications", [])
        lab_results = structured_data.get("lab_results", [])
        allergies = structured_data.get("allergies", [])
        
        print("ENTITIES FOUND:", len(diagnoses))
        print("MEDICATIONS FOUND:", len(medications))
        print("LAB RESULTS FOUND:", len(lab_results))
        print("ALLERGIES FOUND:", len(allergies))
        
        update_fields = {"structured_json": json.dumps(structured_data)}
        if structured_data.get("hospital"):
            update_fields["hospital"] = structured_data["hospital"]
        if structured_data.get("document_type"):
            update_fields["document_type"] = structured_data["document_type"]
        if structured_data.get("doctor_name"):
            update_fields["doctor_name"] = structured_data["doctor_name"]
        
        db.documents.update_one({"id": doc_id}, {"$set": update_fields})
        
        # Store extracted medications & lab results into database collections
        med_count = 0
        for med in medications:
            med_name = med.get("name")
            if med_name:
                db.medications.insert_one({
                    "id": get_next_sequence_value(db, "medications"),
                    "patient_id": p_id,
                    "document_id": doc_id,
                    "name": med_name,
                    "generic_name": med_name,
                    "dosage": med.get("dosage", "As directed"),
                    "frequency": med.get("frequency", "Daily"),
                    "prescribed_by": structured_data.get("doctor_name", "Attending Physician"),
                    "start_date": structured_data.get("date", datetime.date.today().isoformat()),
                    "status": "Active"
                })
                med_count += 1
                
        print("MEDICATION RECORDS CREATED:", med_count)
                
        for lab in lab_results:
            if lab.get("test_name"):
                db.lab_results.insert_one({
                    "id": get_next_sequence_value(db, "lab_results"),
                    "patient_id": p_id,
                    "document_id": doc_id,
                    "test_name": lab.get("test_name"),
                    "test_value": lab.get("test_value"),
                    "date": structured_data.get("date", datetime.date.today().isoformat())
                })

        for allergy in allergies:
            if allergy:
                db.allergies.insert_one({
                    "id": get_next_sequence_value(db, "allergies"),
                    "patient_id": p_id,
                    "document_id": doc_id,
                    "allergen": allergy,
                    "severity": "Moderate"
                })

        db.audit_logs.insert_one({
            "id": get_next_sequence_value(db, "audit_logs"),
            "user_email": user_email,
            "action": "AI Extraction",
            "details": f"Structured JSON created for {doc.get('file_name')}",
            "timestamp": datetime.datetime.utcnow().isoformat()
        })
        
        # Step 3: Timeline Agent
        db.documents.update_one({"id": doc_id}, {"$set": {"status": "updating_timeline"}})
        timeline_before = db.timeline_events.count_documents({"$or": [{"patient_id": p_id}, {"patient_id": str(p_id)}]})
        timeline_agent.analyze_and_update(db, p_id, doc_id, structured_data)
        timeline_after = db.timeline_events.count_documents({"$or": [{"patient_id": p_id}, {"patient_id": str(p_id)}]})
        timeline_count = timeline_after - timeline_before
        print("TIMELINE EVENTS CREATED:", timeline_count)
        
        # Step 4: Consistency Agent
        db.documents.update_one({"id": doc_id}, {"$set": {"status": "consistency_check"}})
        insights_before = db.ai_insights.count_documents({"$or": [{"patient_id": p_id}, {"patient_id": str(p_id)}]})
        await consistency_agent.analyze_and_update(db, p_id, doc_id, structured_data)
        
        # Step 5: Missing Info Agent
        db.documents.update_one({"id": doc_id}, {"$set": {"status": "missing_info_check"}})
        await missing_info_agent.analyze_and_update(db, p_id, doc_id)
        insights_after = db.ai_insights.count_documents({"$or": [{"patient_id": p_id}, {"patient_id": str(p_id)}]})
        insights_count = insights_after - insights_before
        print("AI INSIGHTS CREATED:", insights_count)
        
        # Done
        db.documents.update_one({"id": doc_id}, {"$set": {"status": "completed"}})
        print("DOCUMENT PROCESSING COMPLETE")
        print("="*60 + "\n")
        logger.info(f"Pipeline completed successfully for document_id={doc_id}")
        
    except Exception as e:
        error_msg = str(e) if str(e) else "Processing error occurred."
        db.documents.update_one({"id": doc_id}, {"$set": {
            "status": "failed",
            "error_message": error_msg
        }})
        print("PIPELINE EXCEPTION:", repr(e))
        traceback.print_exc()
        logger.error(f"Pipeline error for document_id={doc_id}: {e}\n{traceback.format_exc()}")



@router.post("/process-document")
async def trigger_ai_pipeline(
    document_id: Union[int, str],
    background_tasks: BackgroundTasks,
    db = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    doc_id = int(document_id) if str(document_id).isdigit() else document_id
    doc = db.documents.find_one({"id": doc_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    background_tasks.add_task(process_document_pipeline, doc_id, db, current_user["email"])
    return {"message": "Processing started in background", "status": "processing"}

@router.get("/insights/{patient_id}")
def get_insights(patient_id: Union[int, str], db = Depends(get_db), current_user: dict = Depends(get_current_user)):
    p_id = int(patient_id) if str(patient_id).isdigit() else patient_id
    insights = list(db.ai_insights.find({"$or": [{"patient_id": p_id}, {"patient_id": str(patient_id)}]}))
    return clean_docs(insights)

@router.post("/insights/{insight_id}/review")
def review_insight(insight_id: Union[int, str], db = Depends(get_db), current_user: dict = Depends(get_current_user)):
    i_id = int(insight_id) if str(insight_id).isdigit() else insight_id
    insight = db.ai_insights.find_one({"id": i_id})
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")
        
    db.ai_insights.update_one({"id": i_id}, {"$set": {"status": "reviewed"}})
    
    db.audit_logs.insert_one({
        "id": get_next_sequence_value(db, "audit_logs"),
        "user_email": current_user["email"],
        "action": "Insight Review",
        "details": f"Clinician reviewed insight: {insight.get('title')}",
        "timestamp": datetime.datetime.utcnow().isoformat()
    })
    
    return {"status": "reviewed"}
