import os
import mimetypes
import logging
import traceback
from PIL import Image

logger = logging.getLogger("carebridge")

_easyocr_reader = None

def get_easyocr_reader():
    global _easyocr_reader
    if _easyocr_reader is None:
        try:
            import easyocr
            logger.info("Initializing EasyOCR reader (English)...")
            _easyocr_reader = easyocr.Reader(['en'], gpu=False, verbose=False)
            logger.info("EasyOCR initialized successfully.")
        except Exception as err:
            logger.warning(f"EasyOCR initialization failed: {err}")
            _easyocr_reader = False
    return _easyocr_reader if _easyocr_reader is not False else None

def ocr_pil_image(image: Image.Image) -> str:
    """Runs OCR on a PIL Image using pytesseract or easyocr."""
    extracted = ""
    # Ensure RGB conversion
    if image.mode not in ("RGB", "L"):
        image = image.convert("RGB")
        
    # 1. Try pytesseract first
    try:
        import pytesseract
        text = pytesseract.image_to_string(image)
        if text and len(text.strip()) > 0:
            print("OCR DEBUG - pytesseract succeeded:", len(text.strip()), "chars")
            return text.strip()
    except Exception as tess_err:
        print("OCR DEBUG - pytesseract unavailable or failed:", repr(tess_err))
        
    # 2. Try EasyOCR fallback
    reader = get_easyocr_reader()
    if reader:
        try:
            import numpy as np
            img_np = np.array(image)
            results = reader.readtext(img_np, detail=0)
            extracted = " ".join(results).strip()
            print("OCR DEBUG - EasyOCR succeeded:", len(extracted), "chars")
            return extracted
        except Exception as easy_err:
            print("OCR DEBUG - EasyOCR failed:", repr(easy_err))
            import traceback
            traceback.print_exc()
            
    return extracted.strip()

def extract_text_from_file(file_path: str) -> str:
    """
    Extracts real text from a given file (PDF or image).
    Logs complete diagnostic details.
    """
    file_extension = os.path.splitext(file_path)[1]
    print("OCR DEBUG - file:", file_path)
    print("OCR DEBUG - extension:", file_extension)
    print("OCR DEBUG - exists:", os.path.exists(file_path))
    
    if not os.path.exists(file_path):
        error_msg = f"File not found: {file_path}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)
        
    file_size = os.path.getsize(file_path)
    print("OCR DEBUG - size:", file_size)
    mime_type, _ = mimetypes.guess_type(file_path)
    file_lower = file_path.lower()
    
    extracted_text = ""
    extraction_method = "unknown"
    
    if file_lower.endswith(".pdf"):
        extraction_method = "PyMuPDF_native"
        print("OCR DEBUG - OCR engine: PyMuPDF")
        try:
            try:
                import pymupdf as fitz
            except ImportError:
                import fitz
            doc = fitz.open(file_path)
            page_count = len(doc)
            print(f"OCR DEBUG - PyMuPDF opened PDF: {page_count} page(s)")
            
            for page_num in range(page_count):
                page = doc[page_num]
                text = page.get_text()
                if text:
                    extracted_text += text + "\n"
                    
            print("OCR DEBUG - PyMuPDF native text length:", len(extracted_text))
            
            if len(extracted_text.strip()) < 15:
                print("OCR DEBUG - PDF text layer empty. Falling back to PDF Page Image OCR...")
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
            print("OCR DEBUG - PyMuPDF extraction error:", repr(fitz_err))
            import traceback
            traceback.print_exc()
            
    elif file_lower.endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff")):
        extraction_method = "Image_OCR"
        print("OCR DEBUG - OCR engine: Image_OCR (pytesseract/EasyOCR)")
        try:
            img = Image.open(file_path)
            print(f"OCR DEBUG - PIL opened image: format={img.format}, size={img.size}, mode={img.mode}")
            extracted_text = ocr_pil_image(img)
            print("OCR RESULT LENGTH:", len(extracted_text or ""))
            print("OCR RESULT PREVIEW:", (extracted_text or "")[:500])
        except Exception as img_err:
            print("OCR EXCEPTION:", repr(img_err))
            import traceback
            traceback.print_exc()
            raise
            
    elif file_lower.endswith((".txt", ".md", ".json")):
        extraction_method = "plain_text"
        print("OCR DEBUG - OCR engine: plain_text")
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                extracted_text = f.read()
        except Exception as txt_err:
            print("OCR EXCEPTION:", repr(txt_err))
            raise

    extracted_text = extracted_text.strip()
    print("OCR DEBUG - extracted characters:", len(extracted_text))
    
    if not extracted_text:
        error_details = f"Text could not be reliably extracted from {os.path.basename(file_path)} using method '{extraction_method}'. File size: {file_size} bytes."
        logger.error(error_details)
        raise ValueError("Text could not be reliably extracted. Manual review required.")
        
    return extracted_text
