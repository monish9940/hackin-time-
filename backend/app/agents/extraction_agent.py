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

        lines = [line.strip() for line in text.splitlines() if line.strip()]

        # 1. Date extraction heuristic
        date_match = re.search(r'\b(\d{4}-\d{2}-\d{2})\b', text)
        if not date_match:
            date_match = re.search(r'\b(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})\b', text)
        if date_match:
            result["date"] = date_match.group(1)

        # 2. Hospital / Clinic extraction heuristic
        hospital_match = re.search(r'(?:hospital|clinic|center|medical center|facility):\s*([^\n\r,]+)', text, re.IGNORECASE)
        if hospital_match:
            result["hospital"] = hospital_match.group(1).strip()
        elif "medical center" in text_lower or "clinic" in text_lower or "hospital" in text_lower:
            for line in lines[:5]:
                if any(k in line.lower() for k in ["center", "hospital", "clinic", "diagnostics", "health"]):
                    result["hospital"] = line.strip()
                    break

        # 3. Doctor Name extraction heuristic
        doctor_match = re.search(r'(?:doctor|dr\.|physician|attending):\s*([^\n\r,]+)', text, re.IGNORECASE)
        if doctor_match:
            result["doctor_name"] = doctor_match.group(1).strip()
        else:
            dr_match2 = re.search(r'\b(dr\.\s+[a-z\s]+)', text, re.IGNORECASE)
            if dr_match2:
                result["doctor_name"] = dr_match2.group(1).strip().title()

        # 4. Document Type heuristic
        if "discharge summary" in text_lower:
            result["document_type"] = "Discharge Summary"
        elif "lab report" in text_lower or "laboratory" in text_lower or "diagnostics" in text_lower:
            result["document_type"] = "Lab Report"
        elif "prescription" in text_lower or "prescribed" in text_lower or "rx" in text_lower:
            result["document_type"] = "Prescription"

        # 5. Diagnoses extraction heuristic
        diagnosis_section = False
        for line in lines:
            if re.match(r'^(?:diagnosis|diagnoses|impression|assessment|condition|chief complaint):', line, re.IGNORECASE):
                diagnosis_section = True
                val = re.sub(r'^(?:diagnosis|diagnoses|impression|assessment|condition|chief complaint):\s*', '', line, flags=re.IGNORECASE).strip()
                if val and val not in result["diagnoses"]:
                    result["diagnoses"].append(val)
                continue
            elif diagnosis_section and (":" in line or line.isupper()):
                diagnosis_section = False

            if diagnosis_section and line and line not in result["diagnoses"]:
                result["diagnoses"].append(line)

        # Keyword-based diagnoses fallback
        known_conditions = [
            ("bronchitis", "Acute Bronchitis"),
            ("hypertension", "Hypertension"),
            ("diabetes", "Type 2 Diabetes"),
            ("asthma", "Asthma"),
            ("pneumonia", "Pneumonia"),
            ("hyperlipidemia", "Hyperlipidemia"),
            ("anemia", "Anemia"),
            ("fever", "Fever / Infection"),
            ("covid", "COVID-19"),
            ("influenza", "Influenza")
        ]
        for kw, canonical in known_conditions:
            if kw in text_lower and not any(kw in d.lower() for d in result["diagnoses"]):
                result["diagnoses"].append(canonical)

        # 6. Medications extraction heuristic
        # A. Look for numbered list or lines with drug name + dosage + frequency
        med_pattern = re.compile(
            r'(?:^\d+[\.\)]\s*)?([A-Z][a-z0-9\-]+)\s+(\d+(?:\.\d+)?\s*(?:mg|mcg|g|ml|units?|puffs?|tablets?|capsules?))\b(?:\s*([^\n\r\.;\)]+))?',
            re.IGNORECASE
        )
        
        med_section = False
        for line in lines:
            if re.match(r'^(?:prescribed medications|medications|medication list|current medications|rx):', line, re.IGNORECASE):
                med_section = True
                continue
            elif med_section and (re.match(r'^[A-Z\s]{4,}:', line) or "LABORATORY" in line.upper() or "ALLERGIES" in line.upper()):
                med_section = False

            # Check if line matches medication pattern
            m = med_pattern.search(line)
            if m:
                drug_name = m.group(1).strip().capitalize()
                dosage = m.group(2).strip()
                details = m.group(3).strip() if m.group(3) else "As directed"
                # Exclude common non-drug words
                non_drugs = ["patient", "doctor", "date", "hospital", "diagnosis", "wbc", "glucose", "hba1c", "hemoglobin", "platelets", "creatinine", "serum", "test", "report"]
                if drug_name.lower() not in non_drugs and not any(med["name"].lower() == drug_name.lower() for med in result["medications"]):
                    result["medications"].append({
                        "name": drug_name,
                        "dosage": dosage,
                        "frequency": details if details else "Daily"
                    })

        # Known common medications fallback check
        known_drugs = [
            "amoxicillin", "lisinopril", "albuterol", "atorvastatin", "metformin",
            "amlodipine", "metoprolol", "omeprazole", "levothyroxine", "gabapentin",
            "hydrochlorothiazide", "losartan", "ibuprofen", "paracetamol", "aspirin",
            "sertraline", "simvastatin", "furosemide", "pantoprazole", "prednisone"
        ]
        for drug in known_drugs:
            if drug in text_lower and not any(m["name"].lower() == drug for m in result["medications"]):
                dosage_match = re.search(r'\b' + drug + r'\s*(\d+(?:\.\d+)?\s*(?:mg|mcg|g|ml|puffs?))\b', text_lower)
                dosage = dosage_match.group(1) if dosage_match else "As directed"
                freq_match = re.search(r'\b' + drug + r'\b[^\n\r]*?(daily|twice daily|three times daily|once daily|every \d+ hours|as needed)', text_lower)
                freq = freq_match.group(1).capitalize() if freq_match else "Daily"
                result["medications"].append({
                    "name": drug.capitalize(),
                    "dosage": dosage,
                    "frequency": freq
                })

        # 7. Lab Results extraction heuristic
        lab_pattern = re.compile(
            r'([A-Za-z0-9\s\-\/\(\)]+):\s*([\d\.]+\s*(?:k\/uL|g\/dL|mg\/dL|mmol\/L|%|uIU\/mL|pg\/mL|ng\/mL|mEq\/L|U\/L|IU\/L)\b[^\n\r]*)',
            re.IGNORECASE
        )
        for line in lines:
            m = lab_pattern.search(line)
            if m:
                t_name = m.group(1).strip()
                t_val = m.group(2).strip()
                if not any(k in t_name.lower() for k in ["patient", "doctor", "date", "hospital", "phone", "id"]):
                    result["lab_results"].append({
                        "test_name": t_name,
                        "test_value": t_val
                    })

        # Known common lab tests fallback check
        known_labs = [
            ("wbc", "WBC Count"),
            ("hemoglobin", "Hemoglobin"),
            ("platelets", "Platelets"),
            ("creatinine", "Serum Creatinine"),
            ("glucose", "Fasting Glucose"),
            ("cholesterol", "Cholesterol"),
            ("triglycerides", "Triglycerides"),
            ("hba1c", "HbA1c")
        ]
        for kw, canonical in known_labs:
            if kw in text_lower and not any(l["test_name"].lower() == canonical.lower() for l in result["lab_results"]):
                m = re.search(kw + r':?\s*([\d\.]+\s*(?:k\/uL|g\/dL|mg\/dL|%|mmol\/L)?)', text_lower)
                if m and m.group(1).strip():
                    result["lab_results"].append({
                        "test_name": canonical,
                        "test_value": m.group(1).strip()
                    })

        # 8. Allergies extraction heuristic
        allergy_match = re.search(r'(?:allergies|allergy|allergic to):\s*([^\n\r]+)', text, re.IGNORECASE)
        if allergy_match:
            allergies_str = allergy_match.group(1).strip()
            for alg in re.split(r'[,;]', allergies_str):
                alg_clean = alg.strip()
                if alg_clean and alg_clean.lower() != "none" and alg_clean not in result["allergies"]:
                    result["allergies"].append(alg_clean)

        known_allergens = ["penicillin", "sulfa", "aspirin", "latex", "codeine", "peanuts", "shellfish"]
        for alg in known_allergens:
            if alg in text_lower and "allergy" in text_lower and not any(alg in a.lower() for a in result["allergies"]):
                result["allergies"].append(alg.capitalize())

        return result

