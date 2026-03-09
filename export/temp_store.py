"""Upload quote PDF/DOCX to Vercel Blob and return download URLs."""

from __future__ import annotations

import logging
import os
from typing import Any
from urllib.parse import quote

import requests

from export.builders import build_docx_bytes
from export.builders import build_pdf_bytes

PDF_FILENAME = "dockie_quote.pdf"
DOCX_FILENAME = "dockie_quote.docx"
_PDF_CONTENT_TYPE = "application/pdf"
_DOCX_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
_BLOB_API_BASE = "https://blob.vercel-storage.com"
_BLOB_API_VERSION = "10"
_BLOB_ACCESS_ENV = "DOCKIE_BLOB_ACCESS"
_BLOB_ACCESS_DEFAULT = "private"

# Deterministic path + explicit overwrite keeps one file per session.
_LOGGER = logging.getLogger(__name__)


def _blob_options() -> dict[str, str]:
    token = os.environ.get("BLOB_READ_WRITE_TOKEN")
    if not token:
        raise RuntimeError("BLOB_READ_WRITE_TOKEN is not set")
    return {
        "token": token,
        "access": os.environ.get(_BLOB_ACCESS_ENV, _BLOB_ACCESS_DEFAULT),
    }


def _upload_blob(pathname: str, data: bytes, content_type: str) -> str:
    opts = _blob_options()
    encoded_path = quote(pathname, safe="/")
    url = f"{_BLOB_API_BASE}/?pathname={encoded_path}"
    headers = {
        "authorization": f"Bearer {opts['token']}",
        "x-api-version": _BLOB_API_VERSION,
        # Correct header name per @vercel/blob put-helpers.ts putOptionHeaderMap
        "x-vercel-blob-access": opts["access"],
        "x-content-type": content_type,
        "x-add-random-suffix": "0",
        "x-allow-overwrite": "1",
    }
    response = requests.put(url, headers=headers, data=data, timeout=30)
    if response.status_code != 200:
        raise RuntimeError(f"Blob upload failed ({response.status_code}): {response.text}")
    payload = response.json()
    # For private stores the blob URL requires auth; return downloadUrl which is pre-signed.
    return payload.get("downloadUrl") or payload["url"]


def _safe_session_id(session_id: str) -> str:
    """Sanitize session_id for use as a Blob pathname segment."""
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in session_id) or "session"


def _blob_store_host() -> str | None:
    """Derive the private blob store hostname from BLOB_READ_WRITE_TOKEN.

    Token format: vercel_blob_rw_{storeId}_{secret}
    Hostname:     {storeId_lowercase}.private.blob.vercel-storage.com
    """
    token = os.environ.get("BLOB_READ_WRITE_TOKEN", "")
    parts = token.split("_")
    # Expected: ['vercel', 'blob', 'rw', '{storeId}', '{secret}']
    if len(parts) >= 5 and parts[0] == "vercel" and parts[1] == "blob" and parts[2] == "rw":
        store_id = parts[3].lower()
        return f"{store_id}.private.blob.vercel-storage.com"
    return None


def fetch_blob_file(session_id: str, format: str) -> bytes | None:
    """Fetch a quote file directly from Vercel Blob using the deterministic path.

    Returns the raw bytes, or None if the file is not found or Blob is unavailable.
    This works on serverless environments where in-memory session state is lost.
    """
    if format not in ("pdf", "docx"):
        return None
    host = _blob_store_host()
    if not host:
        return None
    token = os.environ.get("BLOB_READ_WRITE_TOKEN")
    if not token:
        return None

    safe_id = _safe_session_id(session_id)
    filename = PDF_FILENAME if format == "pdf" else DOCX_FILENAME
    blob_url = f"https://{host}/quote_exports/{safe_id}/{filename}"

    try:
        resp = requests.get(
            blob_url,
            headers={"Authorization": f"Bearer {token}"},
            timeout=15,
        )
        if resp.status_code == 200:
            return resp.content
    except Exception:
        _LOGGER.exception("Failed fetching blob file for session %s format %s", safe_id, format)
    return None


def save_quote_files_to_blob(
    session_id: str,
    quote_request: Any,
    quote_analysis: Any,
) -> tuple[str | None, str | None]:
    """Build PDF and DOCX bytes and upload them to Vercel Blob.

    Reads BLOB_READ_WRITE_TOKEN from the environment automatically.

    Returns:
        (pdf_url, docx_url) — Blob download URLs; either can be None on failure.
    """
    safe_id = _safe_session_id(session_id)

    pdf_url: str | None = None
    docx_url: str | None = None

    try:
        pdf_bytes = build_pdf_bytes(quote_request, quote_analysis)
        pdf_url = _upload_blob(
            f"quote_exports/{safe_id}/{PDF_FILENAME}",
            pdf_bytes,
            _PDF_CONTENT_TYPE,
        )
    except Exception:
        _LOGGER.exception("Failed uploading PDF quote to Vercel Blob for session %s", safe_id)

    try:
        docx_bytes = build_docx_bytes(quote_request, quote_analysis)
        docx_url = _upload_blob(
            f"quote_exports/{safe_id}/{DOCX_FILENAME}",
            docx_bytes,
            _DOCX_CONTENT_TYPE,
        )
    except Exception:
        _LOGGER.exception("Failed uploading DOCX quote to Vercel Blob for session %s", safe_id)

    return pdf_url, docx_url
