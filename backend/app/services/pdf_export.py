import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from app.config import settings

def generate_patient_summary_pdf(db, patient: dict) -> str:
    patient_id_str = patient.get("patient_id", "patient")
    pdf_filename = f"CareBridge_Summary_{patient_id_str}.pdf"
    pdf_path = os.path.join(settings.UPLOAD_DIR, pdf_filename)
    
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    
    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "CareBridge AI - Patient Summary")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Patient Name: {patient.get('name')}")
    c.drawString(50, height - 100, f"Patient ID: {patient.get('patient_id')}")
    c.drawString(50, height - 120, f"Age: {patient.get('age')} | Gender: {patient.get('gender')} | Blood Group: {patient.get('blood_group')}")
    
    # Disclaimer
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, height - 150, "DISCLAIMER: AI-generated information is intended to support clinician")
    c.drawString(50, height - 165, "review and should be independently verified. Does not provide medical diagnosis.")
    
    # AI Insights Section
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 200, "AI Insights & Review Flags")
    
    p_id = patient.get("id")
    insights = list(db.ai_insights.find({"patient_id": p_id}))
    y = height - 220
    c.setFont("Helvetica", 10)
    for insight in insights:
        priority_str = insight.get('priority', 'MEDIUM').upper()
        title_str = insight.get('title', 'Insight')
        desc_str = insight.get('description', '')
        c.drawString(60, y, f"[{priority_str}] {title_str}: {desc_str}")
        y -= 20
        c.drawString(80, y, f"Action: {insight.get('action_required', 'N/A')}")
        y -= 25
        if y < 100:
            c.showPage()
            y = height - 50
            
    c.save()
    return pdf_path
