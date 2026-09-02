import os
import time
import requests
from PIL import Image, ImageDraw, ImageFont

BASE_URL = "http://127.0.0.1:8000"

def run_test():
    print("=== CAREBRIDGE AI END-TO-END OCR & DOCUMENT PROCESSING VERIFICATION ===")
    
    # 1. Register / Login
    email = "ocrtestdoc@carebridge.ai"
    password = "Password123!"
    reg_resp = requests.post(f"{BASE_URL}/api/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Dr. OCR Tester",
        "organization": "CareBridge Clinical Lab",
        "specialization": "Internal Medicine"
    })
    print(f"[1] User Register Status: {reg_resp.status_code}")
    
    login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={"email": email, "password": password})
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("[2] User Login Status: 200 OK (JWT Received)")
    
    # 2. Create Patient
    unique_pid = f"PAT-OCR-{int(time.time())}"
    patient_payload = {
        "patient_id": unique_pid,
        "name": "Sarah Connor",
        "age": 42,
        "gender": "Female",
        "blood_group": "A+"
    }
    p_resp = requests.post(f"{BASE_URL}/api/patients/", json=patient_payload, headers=headers)
    print(f"[3] Create Patient Status: {p_resp.status_code}")
    if p_resp.status_code == 200:
        patient_id = p_resp.json()["id"]
    else:
        pts = requests.get(f"{BASE_URL}/api/patients/", headers=headers).json()
        patient_id = pts[0]["id"]
    print(f"    Target Patient DB ID: {patient_id}")

    # 3. Generate Real PDF Document using PyMuPDF
    import pymupdf as fitz
    pdf_path = "e:/hackin time/scratch/test_clinical_note.pdf"
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    
    doc = fitz.open()
    page = doc.new_page()
    pdf_text = (
        "CAREBRIDGE MEDICAL CENTER - CLINICAL DISCHARGE SUMMARY\n"
        "Patient: Sarah Connor (ID: PAT-OCR-99)\n"
        "Date: 2026-09-02\n"
        "Attending Physician: Dr. OCR Tester\n\n"
        "DIAGNOSIS: Acute Bronchitis and Mild Hypertension.\n\n"
        "PRESCRIBED MEDICATIONS:\n"
        "1. Amoxicillin 500mg oral capsule - 1 capsule three times daily for 7 days.\n"
        "2. Lisinopril 10mg tablet - 1 tablet daily every morning.\n"
        "3. Albuterol Inhaler 90mcg - 2 puffs every 4 to 6 hours as needed for shortness of breath.\n\n"
        "LABORATORY RESULTS:\n"
        "WBC Count: 11.5 k/uL (Elevated)\n"
        "Hemoglobin: 14.2 g/dL (Normal)\n"
        "Platelets: 250 k/uL (Normal)\n"
        "Serum Creatinine: 0.9 mg/dL (Normal)\n\n"
        "ALLERGIES: Penicillin (Moderate rash)\n"
        "FOLLOW-UP: Return in 2 weeks for blood pressure re-evaluation."
    )
    page.insert_text((50, 50), pdf_text, fontsize=11)
    doc.save(pdf_path)
    doc.close()
    print(f"[4] Generated test PDF at {pdf_path}")
    
    # 4. Upload PDF
    with open(pdf_path, "rb") as f:
        files = {"file": ("test_clinical_note.pdf", f, "application/pdf")}
        data = {"patient_id": str(patient_id), "document_type": "Discharge Summary"}
        upload_resp = requests.post(f"{BASE_URL}/api/documents/upload", files=files, data=data, headers=headers)
        
    print(f"[5] PDF Upload Status: {upload_resp.status_code}")
    assert upload_resp.status_code == 200, f"Upload PDF failed: {upload_resp.text}"
    pdf_doc_data = upload_resp.json()
    pdf_doc_id = pdf_doc_data["id"]
    print(f"    Uploaded PDF Document ID: {pdf_doc_id}")

    # 5. Trigger AI Pipeline for PDF
    proc_resp = requests.post(f"{BASE_URL}/api/ai/process-document?document_id={pdf_doc_id}", headers=headers)
    print(f"[6] PDF Pipeline Trigger Status: {proc_resp.status_code}")
    
    # Poll PDF document status
    pdf_final_status = "processing"
    for _ in range(15):
        time.sleep(1)
        chk = requests.get(f"{BASE_URL}/api/documents/{pdf_doc_id}", headers=headers).json()
        pdf_final_status = chk.get("status")
        print(f"    Polling PDF status: {pdf_final_status}")
        if pdf_final_status in ["completed", "processed", "failed"]:
            break
            
    print(f"[7] PDF Processing Final Status: {pdf_final_status}")
    assert pdf_final_status in ["completed", "processed"], f"PDF processing failed: {chk}"
    assert len(chk.get("extracted_text", "")) > 50, "Extracted text length too short"
    print(f"    PDF Extracted Text Length: {len(chk['extracted_text'])} chars")

    # 6. Generate Real Medical Image Document using PyMuPDF page rendering (crisp 300dpi text image)
    img_pdf = fitz.open()
    img_page = img_pdf.new_page(width=600, height=400)
    img_text = (
        "CAREBRIDGE CLINICAL LAB REPORT\n"
        "Patient Name: Sarah Connor\n"
        "Lab Test: Fasting Blood Glucose & Lipid Panel\n"
        "Glucose: 95 mg/dL (Normal)\n"
        "Cholesterol: 180 mg/dL (Normal)\n"
        "Triglycerides: 140 mg/dL\n"
        "Prescribed Atorvastatin 10mg daily"
    )
    img_page.insert_text((40, 50), img_text, fontsize=18)
    pix = img_page.get_pixmap(dpi=200)
    img_path = "e:/hackin time/scratch/test_lab_report.png"
    pix.save(img_path)
    img_pdf.close()
    print(f"[8] Generated test Image at {img_path}")

    # 7. Upload Image
    with open(img_path, "rb") as f:
        files = {"file": ("test_lab_report.png", f, "image/png")}
        data = {"patient_id": str(patient_id), "document_type": "Lab Report"}
        img_upload_resp = requests.post(f"{BASE_URL}/api/documents/upload", files=files, data=data, headers=headers)
        
    print(f"[9] Image Upload Status: {img_upload_resp.status_code}")
    assert img_upload_resp.status_code == 200, f"Upload Image failed: {img_upload_resp.text}"
    img_doc_id = img_upload_resp.json()["id"]

    # 8. Trigger AI Pipeline for Image
    img_proc_resp = requests.post(f"{BASE_URL}/api/ai/process-document?document_id={img_doc_id}", headers=headers)
    print(f"[10] Image Pipeline Trigger Status: {img_proc_resp.status_code}")
    
    # Poll Image document status
    img_final_status = "processing"
    for _ in range(15):
        time.sleep(1)
        chk = requests.get(f"{BASE_URL}/api/documents/{img_doc_id}", headers=headers).json()
        img_final_status = chk.get("status")
        print(f"    Polling Image status: {img_final_status}")
        if img_final_status in ["completed", "processed", "failed"]:
            break
            
    print(f"[11] Image Processing Final Status: {img_final_status}")
    extracted_img_txt = chk.get("extracted_text") or ""
    print(f"    Image Extracted Text Length: {len(extracted_img_txt)} chars")
    assert img_final_status in ["completed", "processed"], f"Image OCR failed: {chk}"
    assert len(extracted_img_txt) > 30, f"Image extracted text too short: {extracted_img_txt}"

    # 9. Verify Downstream APIs (Medications, Timeline, Insights, Documents)
    meds_resp = requests.get(f"{BASE_URL}/api/patients/medications/{patient_id}", headers=headers)
    assert meds_resp.status_code == 200, f"Get medications failed: {meds_resp.text}"
    meds = meds_resp.json()
    print(f"[12] GET Medications API Count: {len(meds)}")
    assert len(meds) > 0, f"Expected medications to be created, got 0: {meds}"

    timeline_resp = requests.get(f"{BASE_URL}/api/patients/timeline/{patient_id}", headers=headers)
    assert timeline_resp.status_code == 200, f"Get timeline failed: {timeline_resp.text}"
    timeline = timeline_resp.json()
    print(f"[13] GET Timeline API Event Count: {len(timeline)}")
    assert len(timeline) > 0, f"Expected timeline events to be created, got 0: {timeline}"

    insights_resp = requests.get(f"{BASE_URL}/api/ai/insights/{patient_id}", headers=headers)
    assert insights_resp.status_code == 200, f"Get insights failed: {insights_resp.text}"
    insights = insights_resp.json()
    print(f"[14] GET AI Insights API Count: {len(insights)}")

    docs_resp = requests.get(f"{BASE_URL}/api/documents/?patient_id={patient_id}", headers=headers)
    assert docs_resp.status_code == 200, f"Get documents failed: {docs_resp.text}"
    docs = docs_resp.json()
    print(f"[15] GET Documents API Count: {len(docs)}")
    assert len(docs) >= 2, f"Expected at least 2 documents, got {len(docs)}"

    # 10. Test Intentionally Unreadable Image File
    bad_path = "e:/hackin time/scratch/corrupt_unreadable.png"
    with open(bad_path, "wb") as f:
        f.write(b"X")  # unreadable 1-byte image
        
    with open(bad_path, "rb") as f:
        files = {"file": ("corrupt_unreadable.png", f, "image/png")}
        data = {"patient_id": str(patient_id), "document_type": "Other"}
        bad_upload_resp = requests.post(f"{BASE_URL}/api/documents/upload", files=files, data=data, headers=headers)
        
    assert bad_upload_resp.status_code == 200, f"Upload unreadable file failed: {bad_upload_resp.text}"
    bad_doc_id = bad_upload_resp.json()["id"]
    requests.post(f"{BASE_URL}/api/ai/process-document?document_id={bad_doc_id}", headers=headers)
    
    time.sleep(2)
    bad_chk = requests.get(f"{BASE_URL}/api/documents/{bad_doc_id}", headers=headers).json()
    print(f"[16] Unreadable File Status: {bad_chk.get('status')} (Error: '{bad_chk.get('error_message')}')")
    assert bad_chk.get("status") == "failed" or len(bad_chk.get("extracted_text", "")) < 10, "Unreadable file handled properly"
    
    print("\n=== ALL E2E MEDICAL INTELLIGENCE PIPELINE VERIFICATION TESTS PASSED SUCCESSFULLY! ===")

if __name__ == "__main__":
    run_test()
