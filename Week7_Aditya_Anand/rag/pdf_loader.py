"""
rag/pdf_loader.py
Phase 3 (upgraded): Multi-PDF upload and storage.
Text extraction, chunking, and embeddings are NOT implemented here.
Developer: Aditya Anand
"""

from dataclasses import dataclass, field
from pathlib import Path


# ── Project-level paths ────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
UPLOADS_DIR  = PROJECT_ROOT / "uploads"


# ── Result dataclass returned per file ────────────────────────────────────
@dataclass
class UploadResult:
    """Outcome of a single file-save attempt."""
    filename:   str
    file_path:  Path | None = None
    status:     str  = "pending"   # "uploaded" | "duplicate" | "error"
    message:    str  = ""
    size_mb:    float = 0.0


class PDFLoader:
    """
    Handles saving one or many uploaded PDF files to disk and reading
    basic file metadata.  Does NOT perform text extraction or processing.
    """

    def __init__(self, upload_dir: Path = UPLOADS_DIR) -> None:
        """
        Args:
            upload_dir: Directory where uploaded PDFs will be stored.
                        Defaults to the project-level uploads/ folder.
        """
        self.upload_dir: Path = upload_dir

    # ──────────────────────────────────────────────────────────────────────
    # PUBLIC — single file
    # ──────────────────────────────────────────────────────────────────────

    def save_uploaded_file(self, uploaded_file) -> tuple[Path, str]:
        """
        Persist a single Streamlit UploadedFile to uploads/.

        - Creates the directory if it does not exist.
        - If a file with the same name already exists, returns the
          existing path WITHOUT overwriting it.

        Args:
            uploaded_file: A Streamlit UploadedFile object.

        Returns:
            Tuple (file_path: Path, filename: str).

        Raises:
            ValueError: If the file is not a PDF.
            IOError:    If the file cannot be written.
        """
        self._ensure_upload_dir()
        self._validate_pdf(uploaded_file)

        filename:  str  = uploaded_file.name
        file_path: Path = self.upload_dir / filename

        # Skip write if already present
        if file_path.exists():
            return file_path, filename

        try:
            file_path.write_bytes(uploaded_file.getvalue())
        except OSError as exc:
            raise IOError(f"Failed to save '{filename}': {exc}") from exc

        return file_path, filename

    def get_pdf_metadata(self, file_path: Path) -> dict:
        """
        Return basic metadata for a saved PDF.
        Page count is intentionally omitted — added in Phase 4 (PyMuPDF).

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

        size_mb: float = round(file_path.stat().st_size / (1024 * 1024), 3)

        return {
            "filename": file_path.name,
            "size_mb":  size_mb,
            "status":   "Uploaded",
        }

    # ──────────────────────────────────────────────────────────────────────
    # PUBLIC — multiple files
    # ──────────────────────────────────────────────────────────────────────

    def save_multiple_files(self, uploaded_files: list) -> list[UploadResult]:
        """
        Process a list of Streamlit UploadedFile objects.

        For each file:
          - Validates it is a PDF.
          - Checks for a duplicate before writing.
          - Saves it to disk if new.
          - Returns an UploadResult capturing the outcome.

        Args:
            uploaded_files: List of Streamlit UploadedFile objects.

        Returns:
            List of UploadResult, one per input file.
        """
        results: list[UploadResult] = []

        for uf in uploaded_files:
            result = self._process_single(uf)
            results.append(result)

        return results

    def get_all_uploaded_docs(self) -> list[dict]:
        """
        Scan the uploads/ directory and return metadata for every PDF found.
        Useful for rebuilding session state after a page refresh.

        Returns:
            List of dicts, each with: filename, size_mb, status, path.
        """
        self._ensure_upload_dir()
        docs: list[dict] = []

        for pdf_file in sorted(self.upload_dir.glob("*.pdf")):
            meta = self.get_pdf_metadata(pdf_file)
            meta["path"] = str(pdf_file)
            docs.append(meta)

        return docs

    # ──────────────────────────────────────────────────────────────────────
    # PRIVATE HELPERS
    # ──────────────────────────────────────────────────────────────────────

    def _process_single(self, uploaded_file) -> UploadResult:
        """
        Save one file and return a populated UploadResult.
        All exceptions are caught here so a batch loop never aborts early.
        """
        result = UploadResult(filename=uploaded_file.name)

        try:
            self._validate_pdf(uploaded_file)
        except ValueError as exc:
            result.status  = "error"
            result.message = str(exc)
            return result

        dest_path: Path = self.upload_dir / uploaded_file.name

        # Duplicate check before writing
        if dest_path.exists():
            result.status    = "duplicate"
            result.message   = "File already exists — not overwritten."
            result.file_path = dest_path
            result.size_mb   = round(dest_path.stat().st_size / (1024 * 1024), 3)
            return result

        # Write to disk
        try:
            self._ensure_upload_dir()
            dest_path.write_bytes(uploaded_file.getvalue())
            result.status    = "uploaded"
            result.message   = "Saved successfully."
            result.file_path = dest_path
            result.size_mb   = round(dest_path.stat().st_size / (1024 * 1024), 3)
        except OSError as exc:
            result.status  = "error"
            result.message = f"Disk write failed: {exc}"

        return result

    def _ensure_upload_dir(self) -> None:
        """Create uploads/ if it does not already exist."""
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _validate_pdf(uploaded_file) -> None:
        """
        Raise ValueError if the file is not a PDF.
        Checks both extension and MIME type.
        """
        name: str = uploaded_file.name.lower()
        mime: str = getattr(uploaded_file, "type", "")

        if not (name.endswith(".pdf") or mime == "application/pdf"):
            raise ValueError(
                f"Invalid file type: '{uploaded_file.name}'. Only PDFs are accepted."
            )
