from app.agents.base import BaseAgent
from app.db_helpers import get_next_sequence_value

class TimelineAgent(BaseAgent):
    def __init__(self):
        super().__init__("Timeline Agent")

    def analyze_and_update(self, db, patient_id, document_id: int, structured_data: dict) -> None:
        """
        Reads structured medical records and generates timeline events in MongoDB.
        """
        date = structured_data.get("date", "Unknown Date")
        hospital = structured_data.get("hospital", "General Hospital")
        p_id = int(patient_id) if str(patient_id).isdigit() else patient_id
        
        # Add diagnoses events
        for diagnosis in structured_data.get("diagnoses", []):
            db.timeline_events.insert_one({
                "id": get_next_sequence_value(db, "timeline_events"),
                "patient_id": p_id,
                "document_id": document_id,
                "date": date,
                "category": "Consultation",
                "title": "Diagnosis Recorded",
                "description": f"Diagnosis documented: {diagnosis}",
                "hospital": hospital,
                "badge_color": "blue"
            })
            
        # Add medication events
        for med in structured_data.get("medications", []):
            db.timeline_events.insert_one({
                "id": get_next_sequence_value(db, "timeline_events"),
                "patient_id": p_id,
                "document_id": document_id,
                "date": date,
                "category": "Prescription",
                "title": "Prescription Added",
                "description": f"{med.get('name')} {med.get('dosage')} ({med.get('frequency')})",
                "hospital": hospital,
                "badge_color": "green"
            })
            
        # Add lab result events
        for lab in structured_data.get("lab_results", []):
            db.timeline_events.insert_one({
                "id": get_next_sequence_value(db, "timeline_events"),
                "patient_id": p_id,
                "document_id": document_id,
                "date": date,
                "category": "Lab Report",
                "title": "Lab Result",
                "description": f"{lab.get('test_name')}: {lab.get('test_value')}",
                "hospital": hospital,
                "badge_color": "blue"
            })
            
        # Add allergy events
        for allergy in structured_data.get("allergies", []):
            db.timeline_events.insert_one({
                "id": get_next_sequence_value(db, "timeline_events"),
                "patient_id": p_id,
                "document_id": document_id,
                "date": date,
                "category": "Allergy",
                "title": "Allergy Noted",
                "description": f"Allergy to {allergy} documented.",
                "hospital": hospital,
                "badge_color": "red"
            })
