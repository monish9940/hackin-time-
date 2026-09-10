import os
import shutil
import mimetypes
import logging
import traceback
from PIL import Image
from app.config import settings

logger = logging.getLogger("carebridge")

def get_pytesseract():
    try:
        import pytesseract
        
        # 1. TESSERACT_CMD env var override
        if settings.TESSERACT_CMD and os.path.exists(settings.TESSERACT_CMD):
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD
            return pytesseract
            
        # 2. PATH resolution via shutil.which
        which_path = shutil.which("tesseract") or shutil.which("tesseract.exe")
        if which_path:
            pytesseract.pytesseract.tesseract_cmd = which_path
            return pytesseract
            
        # 3. Windows auto-discovery locations
        if os.name == 'nt':
            candidates = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"),
                os.path.expanduser(r"~\AppData\Local\Tesseract-OCR\tesseract.exe"),
            ]
            for cand in candidates:
                if cand and os.path.exists(cand):
                    pytesseract.pytesseract.tesseract_cmd = cand
                    return pytesseract
                    
        return pytesseract
    except Exception as err:
        logger.warning(f"pytesseract import failed: {err}")
        return None

def ocr_pil_image(image: Image.Image) -> str:
    """Runs OCR on a PIL Image using pytesseract with image preprocessing."""
    extracted = ""
    # Convert RGBA/P/L to RGB
    if image.mode not in ("RGB", "L"):
        image = image.convert("RGB")
        
    pytess = get_pytesseract()
    if pytess:
        try:
            # First attempt: direct image OCR
            text = pytess.image_to_string(image)
            if text and len(text.strip()) > 0:
                logger.info(f"pytesseract OCR succeeded: {len(text.strip())} chars extracted")
                return text.strip()
                
            # Second attempt: grayscale conversion for low contrast screenshots
            gray_img = image.convert("L")
            text_gray = pytess.image_to_string(gray_img)
            if text_gray and len(text_gray.strip()) > 0:
                logger.info(f"pytesseract grayscale OCR succeeded: {len(text_gray.strip())} chars extracted")
                return text_gray.strip()
        except Exception as tess_err:
            logger.warning(f"pytesseract OCR failed: {tess_err}")
            
    return extracted.strip()

def extract_text_from_file(file_path: str) -> str:
    """
    Extracts text from a given file (PDF or image).
    Logs technical details safely without outputting patient medical text.
    """
    if not os.path.exists(file_path):
        error_msg = f"File not found: {file_path}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)
        
    file_size = os.path.getsize(file_path)
    file_lower = file_path.lower()
    
    extracted_text = ""
    extraction_method = "unknown"
    
    if file_lower.endswith(".pdf"):
        extraction_method = "PyMuPDF_native"
        try:
            try:
                import pymupdf as fitz
            except ImportError:
                import fitz
            doc = fitz.open(file_path)
            page_count = len(doc)
            
            for page_num in range(page_count):
                page = doc[page_num]
                text = page.get_text()
                if text:
                    extracted_text += text + "\n"
                    
            if len(extracted_text.strip()) < 15:
                extraction_method = "PyMuPDF_rendered_page_OCR"
                ocr_text_accum = ""
                for page_num in range(page_count):
                    page = doc[page_num]
                    pix = page.get_pixmap(dpi=150)
                    page_img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    page_ocr = ocr_pil_image(page_img)
                    if page_ocr:
                        ocr_text_accum += page_ocr + "\n"
                
                if ocr_text_accum.strip():
                    extracted_text = ocr_text_accum
            doc.close()
            
        except Exception as fitz_err:
            logger.error(f"PyMuPDF extraction error: {fitz_err}")
            
    elif file_lower.endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff")):
        extraction_method = "Image_OCR"
        try:
            img = Image.open(file_path)
            extracted_text = ocr_pil_image(img)
            logger.info(f"Image OCR extracted {len(extracted_text or '')} chars")
        except Exception as img_err:
            logger.error(f"Image OCR exception: {img_err}")
            raise
            
    elif file_lower.endswith((".txt", ".md", ".json")):
        extraction_method = "plain_text"
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                extracted_text = f.read()
        except Exception as txt_err:
            logger.error(f"Plain text reading exception: {txt_err}")
            raise

    extracted_text = extracted_text.strip()
    logger.info(f"OCR total extracted characters: {len(extracted_text)}")
    
    if not extracted_text:
        error_details = f"Text could not be reliably extracted from {os.path.basename(file_path)} using method '{extraction_method}'. File size: {file_size} bytes."
        logger.error(error_details)
        raise ValueError("Text could not be reliably extracted. Manual review required.")
        
    return extracted_text
