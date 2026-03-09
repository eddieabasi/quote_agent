"""ExportAgent: uploads PDF/DOCX to Vercel Blob, then serves download links via the local API."""

from __future__ import annotations

import asyncio
import logging
import os
from typing import AsyncGenerator

from google.genai import types
from typing_extensions import override

from google.adk.agents import BaseAgent
from google.adk.agents import InvocationContext
from google.adk.events import Event
from google.adk.events import EventActions

from export.temp_store import save_quote_files_to_blob
from tools import QUOTE_ANALYSIS_KEY
from tools import QUOTE_REQUEST_KEY

DOWNLOAD_BASE_URL_ENV = "DOCKIE_API_BASE_URL"
DEFAULT_DOWNLOAD_BASE_URL = "http://localhost:8000"

_LOGGER = logging.getLogger(__name__)


def _download_base_url() -> str:
    return os.environ.get(DOWNLOAD_BASE_URL_ENV, DEFAULT_DOWNLOAD_BASE_URL).rstrip("/")


class ExportAgent(BaseAgent):
    """Custom agent: uploads PDF/DOCX to Vercel Blob, then yields download links."""

    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        state = ctx.session.state
        quote_request = state.get(QUOTE_REQUEST_KEY)
        quote_analysis = state.get(QUOTE_ANALYSIS_KEY)

        session_id = ctx.session.id
        download_base = f"{_download_base_url()}/quote/download/{session_id}"

        # Upload synchronously so files exist in Blob before download links are shown.
        # asyncio.to_thread keeps the event loop unblocked while requests runs.
        try:
            await asyncio.to_thread(
                save_quote_files_to_blob, session_id, quote_request, quote_analysis
            )
        except Exception:
            _LOGGER.exception("Blob upload failed for session %s", session_id)

        lines = ["Your quote is ready. Click to download:"]
        lines.append(f"- [Download PDF]({download_base}.pdf)")
        lines.append(f"- [Download DOCX]({download_base}.docx)")
        message = "\n".join(lines)

        event = Event(
            invocation_id=ctx.invocation_id,
            author=self.name,
            content=types.Content(role="model", parts=[types.Part(text=message)]),
            actions=EventActions(),
        )
        yield event


export_agent = ExportAgent(
    name="ExportAgent",
    description="Uploads PDF and DOCX quote documents to Vercel Blob and provides download links.",
    sub_agents=[],
)
