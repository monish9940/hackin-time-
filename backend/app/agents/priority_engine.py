from app.agents.base import BaseAgent

class PriorityEngine(BaseAgent):
    def __init__(self):
        super().__init__("Priority Engine")

    def calculate_priority(self, db, patient_id) -> int:
        """
        Calculates an overall AI Review Priority score (0-100) based on unresolved insights in MongoDB.
        """
        p_id = int(patient_id) if str(patient_id).isdigit() else patient_id
        insights = list(db.ai_insights.find({
            "$or": [{"patient_id": p_id}, {"patient_id": str(patient_id)}],
            "status": "pending"
        }))
        
        score = 0
        for insight in insights:
            p = insight.get("priority", "Medium")
            if p == "Critical":
                score += 50
            elif p == "High":
                score += 30
            elif p == "Medium":
                score += 15
            elif p == "Low":
                score += 5
                
        return min(score, 100)
