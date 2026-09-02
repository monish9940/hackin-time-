import datetime
from app.agents.base import BaseAgent
from app.db_helpers import get_next_sequence_value

class MissingInfoAgent(BaseAgent):
    def __init__(self):
        super().__init__("Missing Information Agent")

    async def analyze_and_update(self, db, patient_id, document_id: int) -> None:
        """
        Analyzes patient history in MongoDB to find missing routine documentation based on known conditions.
        """
        prompt = "Analyze history and suggest missing clinical documentation gaps. Return JSON."
        result = await self.call_llm(prompt, self._fallback_missing_info, db=db, patient_id=patient_id)
        
        missing = result.get("missing_info", [])
        p_id = int(patient_id) if str(patient_id).isdigit() else patient_id
        for m in missing:
            db.ai_insights.insert_one({
                "id": get_next_sequence_value(db, "ai_insights"),
                "patient_id": p_id,
                "document_id": document_id,
                "category": "missing_info",
                "insight_type": "Missing Info",
                "severity": m.get("priority", "Low").lower(),
                "priority": m.get("priority", "Low"),
                "title": m.get("title", "Potential Information Gap"),
                "description": m.get("description", ""),
                "action_required": m.get("action_required", "Request updated documentation"),
                "status": "pending",
                "created_at": datetime.datetime.utcnow().isoformat()
            })

    def _fallback_missing_info(self, db, patient_id) -> dict:
        missing_info = []
        p_id = int(patient_id) if str(patient_id).isdigit() else patient_id
        
        # Check if patient has Diabetes diagnosis in medical records
        has_diabetes = db.timeline_events.find_one({
            "$or": [{"patient_id": p_id}, {"patient_id": str(patient_id)}],
            "description": {"$regex": "Diabetes", "$options": "i"}
        })
        
        if has_diabetes:
            has_hba1c = db.lab_results.find_one({
                "$or": [{"patient_id": p_id}, {"patient_id": str(patient_id)}],
                "test_name": {"$regex": "HbA1c", "$options": "i"}
            })
            if not has_hba1c:
                missing_info.append({
                    "priority": "High",
                    "title": "Missing Glycemic Control Lab",
                    "description": "Patient diagnosed with Type 2 Diabetes has no recorded HbA1c result in active records.",
                    "action_required": "Order HbA1c lab test."
                })

        return {"missing_info": missing_info}
