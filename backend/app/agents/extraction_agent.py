import re
import datetime
from app.agents.base import BaseAgent

class ExtractionAgent(BaseAgent):
    def __init__(self):
        super().__init__("Record Extraction Agent")

    async def analyze(self, text: str) -> dict:
        prompt = f"""Extract medical entities from the following text and return ONLY a JSON object:
{{
  "patient_name": "...",
  "date": "YYYY-MM-DD",
  "hospital": "...",
  "doctor_name": "...",
  "document_type": "...",
  "diagnoses": ["...", "..."],
  "medications": [{{"name": "...", "dosage": "...", "frequency": "..."}}],
  "lab_results": [{{"test_name": "...", "test_value": "..."}}],
  "allergies": ["..."]
}}
Text: {text}
"""
        return await self.call_llm(prompt, self._fallback_extraction, text=text)

    def _fallback_extraction(self, text: str) -> dict:
        text_lower = text.lower()
        today_str = datetime.date.today().isoformat()
        
        result = {
            "patient_name": "",
            "date": today_str,
            "hospital": "",
            "doctor_name": "",
            "document_type": "Medical Record",
            "diagnoses": [],
            "medications": [],
            "lab_results": [],
            "allergies": []
        }

        # Date extraction heuristic
        date_match = re.search(r'\b(\d{4}-\d{2}-\d{2})\b', text)
        if date_match:
            result["date"] = date_match.group(1)

        # Hospital / Clinic extraction heuristic
        hospital_match = re.search(r'(?:hospital|clinic|center|medical center):\s*([^\n\r,]+)', text, re.IGNORECASE)
        if hospital_match:
            result["hospital"] = hospital_match.group(1).strip()
        elif "apollo" in text_lower:
            result["hospital"] = "Apollo Hospital"

        # Diagnoses extraction heuristic
        if "diabetes" in text_lower: result["diagnoses"].append("Type 2 Diabetes")
        if "hypertension" in text_lower: result["diagnoses"].append("Hypertension")
        if "asthma" in text_lower: result["diagnoses"].append("Asthma")

        # Lab Results extraction heuristic
        if "hba1c" in text_lower:
            match = re.search(r'hba1c:\s*([\d\.]+)%', text_lower)
            if match:
                result["lab_results"].append({"test_name": "HbA1c", "test_value": f"{match.group(1)}%"})
        if "glucose" in text_lower:
            match = re.search(r'glucose:\s*([\d\.]+)', text_lower)
            if match:
                result["lab_results"].append({"test_name": "Fasting Glucose", "test_value": f"{match.group(1)} mg/dL"})

        # Medications extraction heuristic
        if "metformin" in text_lower:
            dosage_match = re.search(r'metformin\s*(\d+\s*mg)', text_lower)
            dosage = dosage_match.group(1) if dosage_match else "500mg"
            result["medications"].append({"name": "Metformin", "dosage": dosage, "frequency": "Daily"})
            result["document_type"] = "Prescription"
        if "amlodipine" in text_lower:
            dosage_match = re.search(r'amlodipine\s*(\d+\s*mg)', text_lower)
            dosage = dosage_match.group(1) if dosage_match else "5mg"
            result["medications"].append({"name": "Amlodipine", "dosage": dosage, "frequency": "Once daily"})
            result["document_type"] = "Prescription"

        # Allergy extraction heuristic
        if "penicillin" in text_lower and ("allergy" in text_lower or "allergic" in text_lower):
            result["allergies"].append("Penicillin")

        return result

