import magic
import io
from app.core.config import settings
from app.services.sanitizer import (
    sanitize_extracted_text,
    ALLOWED_MIME_TYPES,
    MAX_FILE_SIZE_BYTES,
)

GIBBERISH_THRESHOLD = 0.3  # Minimum alphanumeric ratio
MIN_CONTENT_LENGTH = 200  # Minimum characters to consider a valid resume


class FileValidationError(Exception):
    pass


def validate_file(content: bytes, filename: str) -> str:
    """
    Validate file security and return true MIME type.
    Uses libmagic — not the filename extension — to detect file type (A04).
    """
    # Size check
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise FileValidationError(
            f"File exceeds {settings.MAX_FILE_SIZE_MB}MB limit"
        )

    # True MIME type detection (not extension — extensions are trivially spoofed)
    detected_mime = magic.from_buffer(content, mime=True)
    if detected_mime not in ALLOWED_MIME_TYPES:
        raise FileValidationError(
            f"Unsupported file type: {detected_mime}. Only PDF and DOCX are accepted."
        )

    return detected_mime


def extract_text(content: bytes, mime_type: str) -> str:
    """Route to correct extractor based on validated MIME type."""
    if mime_type == "application/pdf":
        return _extract_from_pdf(content)
    elif (
        mime_type
        == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ):
        return _extract_from_docx(content)
    raise FileValidationError(f"No extractor for MIME type: {mime_type}")


def _extract_from_pdf(content: bytes) -> str:
    import pymupdf4llm
    import tempfile
    import os

    # Write to temp file (pymupdf4llm requires a file path)
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    try:
        text = pymupdf4llm.to_markdown(tmp_path)
    finally:
        os.unlink(tmp_path)  # Always clean up temp files

    return text


def _extract_from_docx(content: bytes) -> str:
    from docx import Document

    doc = Document(io.BytesIO(content))
    lines = []
    for para in doc.paragraphs:
        if para.text.strip():
            lines.append(para.text.strip())
    return "\n".join(lines)


def quality_check(text: str) -> str:
    """
    Validate extracted text quality before sending to AI (saves cost, prevents garbage).
    Returns sanitized text or raises FileValidationError.
    """
    if len(text.strip()) < MIN_CONTENT_LENGTH:
        raise FileValidationError(
            "Could not extract meaningful text. File may be a scanned image or corrupt. "
            "Please upload a text-based PDF or DOCX."
        )

    # Gibberish check: alphanumeric chars / total chars
    alnum_count = sum(1 for c in text if c.isalnum())
    ratio = alnum_count / len(text) if len(text) > 0 else 0
    if ratio < GIBBERISH_THRESHOLD:
        raise FileValidationError(
            "Extracted text appears corrupted or uses unsupported encoding."
        )

    return sanitize_extracted_text(text)
