"""ExportAgent: generates PDF and DOCX from quote state and offers download links."""

from __future__ import annotations

import os
from typing import AsyncGenerator

from google.genai import types
from typing_extensions import override

from google.adk.agents import BaseAgent
from google.adk.agents import InvocationContext
from google.adk.events import Event
from google.adk.events import EventActions

from export.temp_store import save_quote_files_to_temp
from tools import QUOTE_ANALYSIS_KEY
from tools import QUOTE_REQUEST_KEY

# Base URL of the API so in-browser download links hit the backend (not the frontend origin)
DOWNLOAD_BASE_URL_ENV = "DOCKIE_API_BASE_URL"
DEFAULT_DOWNLOAD_BASE_URL = "http://localhost:8000"


def _download_base_url() -> str:
    url = os.environ.get(DOWNLOAD_BASE_URL_ENV, DEFAULT_DOWNLOAD_BASE_URL).rstrip("/")
    return url


class ExportAgent(BaseAgent):
    """Custom agent: reads quote state, saves PDF/DOCX to temp dir, yields download links for the UI."""

    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        state = ctx.session.state
        quote_request = state.get(QUOTE_REQUEST_KEY)
        quote_analysis = state.get(QUOTE_ANALYSIS_KEY)

        session_id = ctx.session.id

        # Save files to quote_exports folder; return download links for the UI
        pdf_path, docx_path = save_quote_files_to_temp(session_id, quote_request, quote_analysis)

        lines = ["Your quote is ready. Click to download:"]
        if pdf_path or docx_path:
            base_url = _download_base_url()
            download_base = f"{base_url}/quote/download/{session_id}"
            if pdf_path:
                lines.append(f"- [Download PDF]({download_base}.pdf)")
            if docx_path:
                lines.append(f"- [Download DOCX]({download_base}.docx)")
        else:
            lines.append("(Quote files could not be generated.)")
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
    description="Generates PDF and DOCX quote documents and provides download links.",
    sub_agents=[],
)
