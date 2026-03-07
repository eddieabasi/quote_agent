from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.responses import Response

from ag_ui_adk import ADKAgent
from ag_ui_adk import add_adk_fastapi_endpoint
from dotenv import load_dotenv

from agents import dockie_quote_agent
from export.builders import build_docx_bytes
from export.builders import build_pdf_bytes
from export.temp_store import get_quote_file_path
from tools import QUOTE_ANALYSIS_KEY
from tools import QUOTE_REQUEST_KEY

load_dotenv()

adk_agent = ADKAgent(
    adk_agent=dockie_quote_agent,
    app_name="quote_agent",
    user_id="demo_user",
    session_timeout_seconds=3600,
    use_in_memory_services=True,
)

app = FastAPI()
add_adk_fastapi_endpoint(app, adk_agent, path="/")

PDF_MEDIA_TYPE = "application/pdf"
DOCX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
PDF_FILENAME = "dockie_quote.pdf"
DOCX_FILENAME = "dockie_quote.docx"


@app.get("/quote/download/{session_id}.{format}")
async def quote_download(
    session_id: str,
    format: str,
    app_name: str = "quote_agent",
    user_id: str = "demo_user",
):
    """Serve quote PDF or DOCX: from temp dir if present, else generate from session state. Triggers download in the browser."""
    if format not in ("pdf", "docx"):
        return Response(status_code=400, content="Format must be pdf or docx")

    filename = PDF_FILENAME if format == "pdf" else DOCX_FILENAME
    media_type = PDF_MEDIA_TYPE if format == "pdf" else DOCX_MEDIA_TYPE

    # Prefer file saved to temp dir by Export agent (click-to-download)
    path = get_quote_file_path(session_id, format)
    if path is not None:
        return FileResponse(
            path=str(path),
            media_type=media_type,
            filename=filename,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    # Fallback: generate from session state (e.g. old session or direct link)
    state = await adk_agent._session_manager.get_session_state(
        session_id=session_id,
        app_name=app_name,
        user_id=user_id,
    )
    if not state:
        return Response(status_code=404, content="Session not found")

    quote_request = state.get(QUOTE_REQUEST_KEY)
    quote_analysis = state.get(QUOTE_ANALYSIS_KEY)

    if format == "pdf":
        body = build_pdf_bytes(quote_request, quote_analysis)
    else:
        body = build_docx_bytes(quote_request, quote_analysis)

    return Response(
        content=body,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
