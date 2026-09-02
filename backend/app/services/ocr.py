import os
import logging

logger = logging.getLogger("carebridge")

def extract_text_from_file(file_path: str) -> str:
    """
    Extracts real text from a given file (PDF or image).
    Returns extracted text or raises ValueError if text cannot be extracted.
    NEVER generates mock or fake medical data.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    extracted_text = ""
    file_lower = file_path.lower()
    
    if file_lower.endswith(".pdf"):
        # Try PyMuPDF (fitz)
        try:
            import fitz
            doc = fitz.open(file_path)
            for page in doc:
                extracted_text += page.get_text()
            doc.close()
        except ImportError:
            # Fallback to pypdf or PyPDF2 if fitz is not installed
            try:
                from pypdf import PdfReader
                reader = PdfReader(file_path)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        extracted_text += text
            except Exception as pypdf_err:
                logger.warning(f"PyPDF extraction error: {pypdf_err}")
        except Exception as fitz_err:
            logger.warning(f"fitz extraction error: {fitz_err}")
            
    elif file_lower.endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff")):
        # Try pytesseract OCR for images
        try:
            from PIL import Image
            import pytesseract
            img = Image.open(file_path)
            extracted_text = pytesseract.image_to_string(img)
        except Exception as ocr_err:
            logger.warning(f"Image OCR extraction error: {ocr_err}")
    elif file_lower.endswith((".txt", ".md", ".json")):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            extracted_text = f.read()

    extracted_text = extracted_text.strip()
    
    if not extracted_text:
        raise ValueError("Text could not be reliably extracted. Manual review required.")
        
    return extracted_text

