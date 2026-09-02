import re
import datetime
from app.agents.base import BaseAgent
from app.db_helpers import get_next_sequence_value

class ConsistencyAgent(BaseAgent):
    def __init__(self):
        super().__init__("Consistency Agent")

    async def analyze_and_update(self, db, patient_id, document_id: int, structured_data: dict) -> None:
        """
        Compares new structured data against historical database entries to detect inconsistencies.
        """
        prompt = f"""Given the patient's historical records and the new document extraction, detect any medical inconsistencies.
New extraction: {structured_data}
Output JSON only: {{"inconsistencies": [{{"category": "...", "priority": "...", "title": "...", "description": "...", "action_required": "..."}}]}}
"""
        result = await self.call_llm(prompt, self._fallback_consistency, db=db, patient_id=patient_id, structured_data=structured_data)
        
        inconsistencies = result.get("inconsistencies", [])
        p_id = int(patient_id) if str(patient_id).isdigit() else patient_id
        for inc in inconsistencies:
            db.ai_insights.insert_one({
                "id": get_next_sequence_value(db, "ai_insights"),
                "patient_id": p_id,
                "document_id": document_id,
                "source_document_id": document_id,
                "category": inc.get("category", "clinical_issue"),
                "insight_type": "Inconsistency",
                "severity": inc.get("priority", "Medium").lower(),
                "priority": inc.get("priority", "Medium"),
                "title": inc.get("title", "Potential Inconsistency Detected"),
                "description": inc.get("description", ""),
                "action_required": inc.get("action_required", "Requires clinician review"),
                "status": "pending",
                "confidence": 0.85,
                "generated_at": datetime.datetime.utcnow().isoformat(),
                "created_at": datetime.datetime.utcnow().isoformat()
            })

    def _fallback_consistency(self, db, patient_id, structured_data: dict) -> dict:
        inconsistencies = []
        p_id = int(patient_id) if str(patient_id).isdigit() else patient_id
        
        # 1. Medication dosage check
        new_meds = structured_data.get("medications", [])
        for new_med in new_meds:
            med_name = new_med.get("name", "")
            if not med_name:
                continue
            historical_med = db.medications.find_one({
                "$or": [{"patient_id": p_id}, {"patient_id": str(patient_id)}],
                "name": {"$regex": f"^{re.escape(med_name)}$", "$options": "i"}
            })
            
            if historical_med and historical_med.get("dosage") != new_med.get("dosage"):
                inconsistencies.append({
                    "category": "medication_change",
                    "priority": "Medium",
                    "title": "Potential Medication Dosage Change Detected",
                    "description": f"{med_name} dosage changed from {historical_med.get('dosage')} to {new_med.get('dosage')}.",
                    "action_required": "Requires clinician review to verify dosage adjustment."
                })
                db.medications.update_one({"id": historical_med["id"]}, {"$set": {"status": "Changed"}})

        # 2. Allergy conflict check
        historical_allergies = list(db.allergies.find({"$or": [{"patient_id": p_id}, {"patient_id": str(patient_id)}]}))
        allergy_names = [a.get("allergen", "").lower() for a in historical_allergies]
        
        for new_med in new_meds:
            med_lower = new_med.get("name", "").lower()
            for allergen in allergy_names:
                if allergen and (allergen in med_lower or med_lower in allergen):
                    inconsistencies.append({
                        "category": "allergy_conflict",
                        "priority": "Critical",
                        "title": f"Potential {new_med.get('name').capitalize()} Allergy Conflict",
                        "description": f"Documented allergy to {allergen.capitalize()} conflicts with prescribed medication {new_med.get('name')}.",
                        "action_required": "Requires clinician review prior to administration."
                    })
                
        return {"inconsistencies": inconsistencies}

