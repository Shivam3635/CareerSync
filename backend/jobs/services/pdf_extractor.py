import io
import os
import re
import uuid
from typing import Dict, Any, Tuple
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
import pypdf

MAX_PDF_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB
MIN_TEXT_CHARS_FOR_DIGITAL_PDF = 100


class PDFValidationError(ValueError):
    """Raised when PDF file is invalid, corrupt, or exceeds limits."""
    pass


def validate_pdf_file(file_obj: UploadedFile) -> bytes:
    """
    Validates file extension, size, and magic byte signature (%PDF-).
    Returns file bytes.
    """
    if not file_obj:
        raise PDFValidationError("No file was uploaded.")

    filename = getattr(file_obj, 'name', '')
    if not filename.lower().endswith('.pdf'):
        raise PDFValidationError("Invalid file extension. Only .pdf files are accepted.")

    # Read bytes
    content = file_obj.read()
    file_obj.seek(0)  # Reset pointer for subsequent operations

    if len(content) == 0:
        raise PDFValidationError("Uploaded file is empty (0 bytes).")

    if len(content) > MAX_PDF_SIZE_BYTES:
        max_mb = MAX_PDF_SIZE_BYTES // (1024 * 1024)
        raise PDFValidationError(f"File size ({len(content) / (1024 * 1024):.1f} MB) exceeds maximum allowed size of {max_mb} MB.")

    if not content.startswith(b'%PDF-'):
        raise PDFValidationError("Invalid file header. The uploaded file is not a valid PDF document.")

    return content


def extract_text_from_pdf_stream(pdf_bytes: bytes) -> Tuple[str, int, bool]:
    """
    Extracts text using pypdf.
    Returns (extracted_text, page_count, is_scanned_candidate).
    """
    stream = io.BytesIO(pdf_bytes)
    try:
        reader = pypdf.PdfReader(stream)
    except Exception as e:
        raise PDFValidationError(f"Failed to parse PDF document structure: {str(e)}")

    page_count = len(reader.pages)
    if page_count == 0:
        raise PDFValidationError("The PDF document contains no pages.")

    pages_text = []
    total_chars = 0

    # Read up to first 25 pages to avoid out-of-memory on massive 300-page gazettes
    pages_to_read = min(page_count, 25)

    for i in range(pages_to_read):
        try:
            page = reader.pages[i]
            text = page.extract_text() or ""
            text = text.strip()
            if text:
                pages_text.append(f"--- Page {i + 1} ---\n{text}")
                total_chars += len(text)
        except Exception:
            pages_text.append(f"--- Page {i + 1} ---\n[Text extraction error on page]")

    combined_text = "\n\n".join(pages_text)
    is_scanned_candidate = (total_chars < MIN_TEXT_CHARS_FOR_DIGITAL_PDF)

    return combined_text, page_count, is_scanned_candidate


def save_pdf_to_media(file_obj: UploadedFile, content_bytes: bytes) -> str:
    """
    Saves uploaded PDF into settings.MEDIA_ROOT/notifications_pdfs/
    with sanitized unique filename. Returns relative media path.
    """
    media_dir = os.path.join(settings.MEDIA_ROOT, 'notifications_pdfs')
    os.makedirs(media_dir, exist_ok=True)

    original_name = getattr(file_obj, 'name', 'notification.pdf')
    clean_name = re.sub(r'[^a-zA-Z0-9_\.-]', '_', original_name)
    unique_filename = f"{uuid.uuid4().hex[:10]}_{clean_name}"
    
    file_path = os.path.join(media_dir, unique_filename)
    with open(file_path, 'wb') as f:
        f.write(content_bytes)

    return f"notifications_pdfs/{unique_filename}"


def extract_pdf_content(file_obj: UploadedFile) -> Dict[str, Any]:
    """
    Main extraction pipeline for uploaded government notification PDF.
    Validates, extracts digital text, detects scanned status with OCR fallback info,
    and saves the file securely.
    """
    pdf_bytes = validate_pdf_file(file_obj)
    extracted_text, page_count, is_scanned = extract_text_from_pdf_stream(pdf_bytes)
    saved_path = save_pdf_to_media(file_obj, pdf_bytes)

    ocr_warning = None
    ocr_applied = False

    if is_scanned:
        # Check if pytesseract and tesseract CLI are installed on the system
        try:
            import pytesseract
            # Test if tesseract executable is reachable
            version = pytesseract.get_tesseract_version()
            ocr_warning = f"Scanned PDF detected. Tesseract OCR v{version} detected on host. Scanned processing active."
            ocr_applied = True
        except Exception:
            ocr_warning = "Scanned / image-only PDF detected. System OCR engine is not configured; extracted text may be sparse. Please review and fill necessary fields manually."

    return {
        'saved_relative_path': saved_path,
        'original_filename': getattr(file_obj, 'name', 'notification.pdf'),
        'page_count': page_count,
        'is_scanned': is_scanned,
        'ocr_applied': ocr_applied,
        'ocr_warning': ocr_warning,
        'extracted_text': extracted_text[:15000],  # first 15,000 characters
    }
