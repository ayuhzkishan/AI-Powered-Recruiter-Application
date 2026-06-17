import uuid
import os
from pathlib import Path
from app.core.config import settings
from app.services.sanitizer import validate_safe_filename


class StorageService:
    def __init__(self):
        self.base_path = Path(settings.UPLOAD_DIR)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def get_candidate_dir(self, candidate_id: str) -> Path:
        """
        Store files in candidate-specific subdirectory.
        Path is UUID-based — NO user input ever enters the file path.
        """
        candidate_dir = self.base_path / str(candidate_id)
        candidate_dir.mkdir(parents=True, exist_ok=True)
        return candidate_dir

    def save_file(
        self, candidate_id: str, content: bytes, original_filename: str
    ) -> str:
        """
        Saves file with a UUID-based name.
        The original filename is sanitized and stored only for display — never used in paths.
        Returns a safe relative path string.
        """
        # Extension from sanitized filename only
        safe_name = validate_safe_filename(original_filename)
        extension = Path(safe_name).suffix.lower()

        # Generate a UUID filename — attacker controls nothing in the path (A03)
        stored_name = f"{uuid.uuid4()}{extension}"
        candidate_dir = self.get_candidate_dir(candidate_id)
        file_path = candidate_dir / stored_name

        with open(file_path, "wb") as f:
            f.write(content)

        return f"local://{candidate_id}/{stored_name}"

    def get_file_bytes(self, file_path_uri: str) -> bytes:
        """Resolve a stored URI back to bytes. Validates path stays within upload dir."""
        relative = file_path_uri.replace("local://", "")
        resolved = (self.base_path / relative).resolve()

        # Ensure resolved path is still within upload directory (traversal guard)
        if not str(resolved).startswith(str(self.base_path.resolve())):
            raise PermissionError("Path traversal attempt detected")

        with open(resolved, "rb") as f:
            return f.read()


storage_service = StorageService()
