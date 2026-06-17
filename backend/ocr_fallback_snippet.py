"""
Tesseract OCR Fallback Script (Future Use)

This script provides a fallback mechanism for extracting text from PDFs and images 
when standard text extraction (e.g., PyMuPDF, pdfplumber) fails or returns 
empty/unreadable text (which often happens with scanned documents or image-based PDFs).

Prerequisites:
--------------
1. System Dependencies:
   - Tesseract OCR engine (e.g., `sudo apt-get install tesseract-ocr` or Windows installer)
   - Poppler (required for pdf2image) (e.g., `sudo apt-get install poppler-utils` or Windows binaries)

2. Python Packages:
   pip install pytesseract pdf2image Pillow

Note: This file is kept separate and is NOT integrated into the current project pipeline.
"""

import io
from typing import Optional
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image

def extract_text_with_ocr(file_content: bytes, mime_type: str = "application/pdf") -> Optional[str]:
    """
    Attempts to extract text using Tesseract OCR.
    Designed to be used as a fallback when standard text extraction fails.
    
    Args:
        file_content (bytes): The raw bytes of the file.
        mime_type (str): The mime type of the file.
        
    Returns:
        str: The extracted text, or None if extraction fails.
    """
    try:
        extracted_text = []
        
        if mime_type == "application/pdf":
            # Convert PDF pages to images
            # Note: poppler must be installed on the system and in PATH
            pages = convert_from_bytes(file_content)
            
            for i, page_image in enumerate(pages):
                # Perform OCR on each page image
                text = pytesseract.image_to_string(page_image)
                extracted_text.append(text)
                
            return "\n\n".join(extracted_text)
            
        elif mime_type.startswith("image/"):
            # If it's already an image (e.g., png, jpeg)
            image = Image.open(io.BytesIO(file_content))
            text = pytesseract.image_to_string(image)
            return text
            
        else:
            print(f"OCR fallback not supported for mime type: {mime_type}")
            return None
            
    except Exception as e:
        print(f"OCR Extraction failed: {str(e)}")
        return None

# ==============================================================================
# HOW TO INTEGRATE IN THE FUTURE
# ==============================================================================
# In your app/services/extractor.py, you would update the extract_text function:
#
# def extract_text(content: bytes, mime_type: str) -> str:
#     # 1. Try standard fast extraction first
#     text = ""
#     try:
#         if mime_type == "application/pdf":
#             text = _extract_pdf(content)
#         elif mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
#             text = _extract_docx(content)
#     except Exception as e:
#         print(f"Standard extraction failed: {e}")
#
#     # 2. Check if text is valid/sufficient
#     if text and len(text.strip()) > 50:
#         return text.strip()
#
#     # 3. Fallback to OCR if standard extraction gave nothing (e.g. scanned PDF)
#     print("Falling back to OCR extraction...")
#     ocr_text = extract_text_with_ocr(content, mime_type)
#     
#     if ocr_text and len(ocr_text.strip()) > 50:
#         return ocr_text.strip()
#
#     raise FileValidationError("Could not extract readable text from the file.")
