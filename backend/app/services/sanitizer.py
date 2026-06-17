import re
import bleach
from pathlib import Path

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5MB
MAX_TEXT_LENGTH = 50_000  # 50k chars max extracted text
MAX_STRING_FIELD = 255


def sanitize_string(value: str, max_length: int = MAX_STRING_FIELD) -> str:
    """Strip HTML tags, normalize whitespace, enforce length."""
    cleaned = bleach.clean(value, tags=[], strip=True)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if len(cleaned) > max_length:
        raise ValueError(f"Input exceeds maximum length of {max_length} characters")
    return cleaned


def sanitize_email(value: str) -> str:
    """Validate email format strictly."""
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    cleaned = value.strip().lower()
    if not re.match(pattern, cleaned):
        raise ValueError("Invalid email format")
    if len(cleaned) > 255:
        raise ValueError("Email too long")
    return cleaned


def sanitize_phone(value: str) -> str:
    """Allow only digits, spaces, hyphens, parentheses, plus sign."""
    cleaned = re.sub(r"[^\d\s\-\(\)\+]", "", value).strip()
    if len(cleaned) > 20:
        raise ValueError("Phone number too long")
    return cleaned


def sanitize_extracted_text(text: str) -> str:
    """Clean extracted resume text before AI processing."""
    # Remove null bytes (SQL injection vector in some DBs)
    text = text.replace("\x00", "")
    # Remove potential prompt injection patterns
    text = re.sub(
        r"(ignore previous instructions?|you are now|system prompt)",
        "[REDACTED]",
        text,
        flags=re.IGNORECASE,
    )
    # Normalize whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {3,}", " ", text)
    return text[:MAX_TEXT_LENGTH]


def validate_safe_filename(filename: str) -> str:
    """
    Prevent path traversal attacks (A03).
    Returns ONLY the sanitized basename — never the full path from user input.
    """
    # Extract basename only — strips any ../ or / directory components
    safe = Path(filename).name
    # Whitelist: alphanumeric, hyphens, underscores, single dot for extension
    safe = re.sub(r"[^\w\-\.]", "_", safe)
    # Prevent double extensions (e.g., malware.pdf.exe)
    parts = safe.split(".")
    if len(parts) > 2:
        safe = parts[0] + "." + parts[-1]
    return safe
