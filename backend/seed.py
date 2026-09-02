import os
import datetime
from app.config import settings
from app.database import get_db, init_db
from app.db_helpers import get_next_sequence_value

def seed_db():
    print("Initializing database connection...")
    init_db()
    db = get_db()
    
    print("Clearing patient & clinical collections in MongoDB...")
    db.patients.drop()
    db.documents.drop()
    db.medical_records.drop()
    db.medications.drop()
    db.lab_results.drop()
    db.allergies.drop()
    db.timeline_events.drop()
    db.ai_insights.drop()
    db.doctor_notes.drop()
    db.audit_logs.drop()
    db.counters.drop()
    
    # Re-create required indexes
    db.users.create_index("email", unique=True)
    db.patients.create_index("patient_id", unique=True)
    db.documents.create_index("patient_id")
    db.timeline_events.create_index("patient_id")
    db.ai_insights.create_index("patient_id")
    
    print("Seeding synthetic clinical patient records...")
    
    # Patients
    p1_id = get_next_sequence_value(db, "patients")
    p1 = {
        "id": p1_id,
        "patient_id": "CB-2026-1042",
        "name": "Arun Kumar",
        "age": 45,
        "gender": "Male",
        "blood_group": "O+",
        "created_at": datetime.datetime.utcnow().isoformat()
    }
    
    p2_id = get_next_sequence_value(db, "patients")
    p2 = {
        "id": p2_id,
        "patient_id": "CB-2026-1038",
        "name": "Priya Sharma",
        "age": 32,
        "gender": "Female",
        "blood_group": "A+",
        "created_at": datetime.datetime.utcnow().isoformat()
    }
    
    p3_id = get_next_sequence_value(db, "patients")
    p3 = {
        "id": p3_id,
        "patient_id": "CB-2026-1021",
        "name": "Ravi Kumar",
        "age": 61,
        "gender": "Male",
        "blood_group": "B+",
        "created_at": datetime.datetime.utcnow().isoformat()
    }
    
    db.patients.insert_many([p1, p2, p3])
    
    # Arun Kumar clinical events
    # Timeline
    db.timeline_events.insert_many([
        {
            "id": get_next_sequence_value(db, "timeline_events"),
            "patient_id": p1_id,
            "date": "2026-06-10",
            "category": "Lab Report",
            "title": "Blood Test",
            "description": "HbA1c: 7.8%, Fasting Blood Sugar: 145 mg/dL",
            "hospital": "City Hospital",
            "badge_color": "blue"
        },
        {
            "id": get_next_sequence_value(db, "timeline_events"),
            "patient_id": p1_id,
            "date": "2026-06-15",
            "category": "Consultation",
            "title": "Initial Consultation",
            "description": "Diagnosis documented: Type 2 Diabetes, Hypertension",
            "hospital": "Cardiology Clinic",
            "badge_color": "blue"
        },
        {
            "id": get_next_sequence_value(db, "timeline_events"),
            "patient_id": p1_id,
            "date": "2026-06-15",
            "category": "Prescription",
            "title": "Prescription Added",
            "description": "Metformin 500mg (Once daily)",
            "hospital": "Cardiology Clinic",
            "badge_color": "green"
        },
        {
            "id": get_next_sequence_value(db, "timeline_events"),
            "patient_id": p1_id,
            "date": "2026-06-15",
            "category": "Prescription",
            "title": "Prescription Added",
            "description": "Amlodipine 5mg (Once daily)",
            "hospital": "Cardiology Clinic",
            "badge_color": "green"
        },
        {
            "id": get_next_sequence_value(db, "timeline_events"),
            "patient_id": p1_id,
            "date": "2026-07-20",
            "category": "Lab Report",
            "title": "Follow-up Lab",
            "description": "HbA1c: 7.1%, Serum Creatinine: 1.1 mg/dL",
            "hospital": "City Hospital",
            "badge_color": "blue"
        },
        {
            "id": get_next_sequence_value(db, "timeline_events"),
            "patient_id": p1_id,
            "date": "2026-07-22",
            "category": "Prescription",
            "title": "Dosage Increased",
            "description": "Metformin increased to 1000mg twice daily",
            "hospital": "City Hospital",
            "badge_color": "orange"
        },
        {
            "id": get_next_sequence_value(db, "timeline_events"),
            "patient_id": p1_id,
            "date": "2026-08-05",
            "category": "Allergy",
            "title": "Allergy Noted",
            "description": "Severe reaction to Penicillin (Skin Rash, Anaphylaxis risk).",
            "hospital": "Apollo Hospital",
            "badge_color": "red"
        }
    ])
    
    # Medications
    db.medications.insert_many([
        {
            "id": get_next_sequence_value(db, "medications"),
            "patient_id": p1_id,
            "name": "Metformin",
            "generic_name": "Glucophage",
            "dosage": "1000mg",
            "frequency": "Twice daily",
            "prescribed_by": "Attending Clinician",
            "start_date": "2026-07-22",
            "status": "Active",
            "dosage_history": "500mg once daily -> 1000mg twice daily"
        },
        {
            "id": get_next_sequence_value(db, "medications"),
            "patient_id": p1_id,
            "name": "Amlodipine",
            "generic_name": "Norvasc",
            "dosage": "5mg",
            "frequency": "Once daily",
            "prescribed_by": "Attending Clinician",
            "start_date": "2026-06-15",
            "status": "Active"
        }
    ])
    
    # Lab results
    db.lab_results.insert_many([
        {
            "id": get_next_sequence_value(db, "lab_results"),
            "patient_id": p1_id,
            "test_name": "HbA1c",
            "test_value": "7.8%",
            "unit": "%",
            "reference_range": "< 5.7%",
            "test_date": "2026-06-10"
        },
        {
            "id": get_next_sequence_value(db, "lab_results"),
            "patient_id": p1_id,
            "test_name": "Fasting Glucose",
            "test_value": "145",
            "unit": "mg/dL",
            "reference_range": "70-99 mg/dL",
            "test_date": "2026-06-10"
        }
    ])
    
    # Allergies
    db.allergies.insert_one({
        "id": get_next_sequence_value(db, "allergies"),
        "patient_id": p1_id,
        "allergen": "Penicillin",
        "severity": "High",
        "reaction": "Skin Rash, Anaphylaxis risk",
        "documented_date": "2026-08-05"
    })
    
    # AI Insights
    db.ai_insights.insert_many([
        {
            "id": get_next_sequence_value(db, "ai_insights"),
            "patient_id": p1_id,
            "category": "allergy_conflict",
            "insight_type": "Inconsistency",
            "severity": "high",
            "priority": "Critical",
            "title": "Penicillin Allergy Conflict",
            "description": "Prescription record lists Amoxicillin (Penicillin derivative) despite documented high severity Penicillin allergy.",
            "action_required": "Verify prescription before administration.",
            "status": "pending",
            "created_at": datetime.datetime.utcnow().isoformat()
        },
        {
            "id": get_next_sequence_value(db, "ai_insights"),
            "patient_id": p1_id,
            "category": "missing_info",
            "insight_type": "Missing Info",
            "severity": "medium",
            "priority": "High",
            "title": "Missing Lipid Profile",
            "description": "Patient diagnosed with Hypertension and Type 2 Diabetes has no recorded Lipid Profile in active history.",
            "action_required": "Order Lipid Panel at next consult.",
            "status": "pending",
            "created_at": datetime.datetime.utcnow().isoformat()
        },
        {
            "id": get_next_sequence_value(db, "ai_insights"),
            "patient_id": p1_id,
            "category": "medication_change",
            "insight_type": "Medication Change",
            "severity": "medium",
            "priority": "Medium",
            "title": "Metformin Dosage Doubled",
            "description": "Metformin dosage increased from 500mg once daily to 1000mg twice daily.",
            "action_required": "Monitor renal function and GI tolerance.",
            "status": "pending",
            "created_at": datetime.datetime.utcnow().isoformat()
        }
    ])
    
    # Audit Log
    db.audit_logs.insert_one({
        "id": get_next_sequence_value(db, "audit_logs"),
        "user_email": "system@carebridge.ai",
        "action": "System Initialization",
        "details": "MongoDB Atlas seeded with synthetic patient clinical data",
        "timestamp": datetime.datetime.utcnow().isoformat()
    })

    print("Synthetic clinical data seeded successfully into MongoDB.")

if __name__ == "__main__":
    seed_db()
