"""Save quote PDF/DOCX to a folder for download links."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from export.builders import build_docx_bytes
from export.builders import build_pdf_bytes

# Base dir for quote files: env DOCKIE_QUOTE_EXPORTS_DIR or project folder quote_exports
QUOTE_EXPORTS_DIR_ENV = "DOCKIE_QUOTE_EXPORTS_DIR"
DEFAULT_FOLDER_NAME = "quote_exports"

PDF_FILENAME = "dockie_quote.pdf"
DOCX_FILENAME = "dockie_quote.docx"


def get_quote_temp_base() -> Path:
    """Return the base directory for storing quote files (actual folder on disk)."""
    path = os.environ.get(QUOTE_EXPORTS_DIR_ENV)
    if path:
        return Path(path).resolve()
    # Default: quote_exports in current working directory (project folder when running the app)
    return Path.cwd() / DEFAULT_FOLDER_NAME


def get_session_dir(session_id: str) -> Path:
    """Return the directory for a given session's quote files."""
    return get_quote_temp_base() / _safe_session_id(session_id)


def _safe_session_id(session_id: str) -> str:
    """Sanitize session_id for use as a path segment."""
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in session_id) or "session"


def save_quote_files_to_temp(
    session_id: str,
    quote_request: Any,
    quote_analysis: Any,
) -> tuple[Path | None, Path | None]:
    """Build PDF and DOCX, save to the quote exports folder (one subdir per session_id). Create dirs as needed.

    Returns:
        (path_to_pdf, path_to_docx); either can be None on failure.
    """
    base = get_session_dir(session_id)
    base.mkdir(parents=True, exist_ok=True)

    pdf_path = base / PDF_FILENAME
    docx_path = base / DOCX_FILENAME

    try:
        pdf_bytes = build_pdf_bytes(quote_request, quote_analysis)
        pdf_path.write_bytes(pdf_bytes)
    except Exception:
        pdf_path = None

    try:
        docx_bytes = build_docx_bytes(quote_request, quote_analysis)
        docx_path.write_bytes(docx_bytes)
    except Exception:
        docx_path = None

    return (pdf_path, docx_path)


def get_quote_file_path(session_id: str, format: str) -> Path | None:
    """Return path to the saved quote file if it exists. format is 'pdf' or 'docx'."""
    if format not in ("pdf", "docx"):
        return None
    name = PDF_FILENAME if format == "pdf" else DOCX_FILENAME
    path = get_session_dir(session_id) / name
    return path if path.is_file() else None
