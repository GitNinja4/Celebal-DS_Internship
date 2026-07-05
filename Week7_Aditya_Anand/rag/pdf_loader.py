"""
rag/pdf_loader.py
Phase 3: PDF upload and storage only.
Text extraction, chunking, and embeddings are NOT implemented here.
Developer: Aditya Anand
"""

from pathlib import Path


# Root of the project (one level up from this file)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
UPLOADS_DIR = PROJECT_ROOT / "uploads"


class PDFLoader:
    """
    Handles saving uploaded PDF files to disk and reading basic file metadata.
    Does NOT perform any text extraction or processing.
    """

    def __init__(self, upload_dir: Path = UPLOADS_DIR) -> None:
        """
        Args:
            upload_dir: Directory where uploaded PDFs will be stored.
                        Defaults to the project-level uploads/ folder.
        """
        self.upload_dir = upload_dir

    # ─────────────────────────────────────────────
    # PUBLIC METHODS
    # ─────────────────────────────────────────────

    def save_uploaded_file(self, uploaded_file) -> tuple[Path, str]:
        """
        Persist a Streamlit UploadedFile object to the uploads/ directory.

        - Creates uploads/ if it does not exist.
        - If a file with the same name already exists, returns the
          existing path without overwriting it.

        Args:
            uploaded_file: A Streamlit UploadedFile object.

        Returns:
            Tuple of (file_path: Path, filename: str).

        Raises:
            ValueError: If the uploaded file is not a PDF.
            IOError:    If the file cannot be written to disk.
        """
        self._ensure_upload_dir()
        self._validate_pdf(uploaded_file)

        filename: str = uploaded_file.name
        file_path: Path = self.upload_dir / filename

        # Return existing file without overwriting
        if file_path.exists():
            return file_path, filename

        # Write the bytes to disk
        try:
            file_path.write_bytes(uploaded_file.getvalue())
        except OSError as exc:
            raise IOError(f"Failed to save '{filename}': {exc}") from exc

        return file_path, filename

    def get_pdf_metadata(self, file_path: Path) -> dict:
        """
        Return basic metadata for a saved PDF file.
        Page count is intentionally omitted — will be added in Phase 4
        when text extraction (PyMuPDF) is introduced.

        Args:
            file_path: Absolute Path to the PDF on disk.

        Returns:
            dict with keys: filename, size_mb, status.

        Raises:
            FileNotFoundError: If file_path does not exist.
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        size_bytes: int = file_path.stat().st_size
        size_mb: float = round(size_bytes / (1024 * 1024), 3)

        return {
            "filename": file_path.name,
            "size_mb": size_mb,
            "status": "Uploaded",
        }

    # ─────────────────────────────────────────────
    # PRIVATE HELPERS
    # ─────────────────────────────────────────────

    def _ensure_upload_dir(self) -> None:
        """Create the uploads directory if it does not already exist."""
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _validate_pdf(uploaded_file) -> None:
        """
        Raise ValueError if the uploaded file is not a PDF.
        Checks both the file extension and the MIME type reported by Streamlit.

        Args:
            uploaded_file: A Streamlit UploadedFile object.
        """
        name: str = uploaded_file.name.lower()
        mime: str = getattr(uploaded_file, "type", "")

        is_pdf_ext: bool = name.endswith(".pdf")
        is_pdf_mime: bool = mime == "application/pdf"

        if not (is_pdf_ext or is_pdf_mime):
            raise ValueError(
                f"Invalid file type: '{uploaded_file.name}'. Only PDF files are accepted."
            )
