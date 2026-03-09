from fastapi import FastAPI
from fastapi.responses import Response

from ag_ui_adk import ADKAgent
from ag_ui_adk import add_adk_fastapi_endpoint
from dotenv import load_dotenv

from agents import dockie_quote_agent
from export.temp_store import fetch_blob_file

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
async def quote_download(session_id: str, format: str):
    """Proxy a quote PDF or DOCX from Vercel Blob to the browser."""
    if format not in ("pdf", "docx"):
        return Response(status_code=400, content="Format must be pdf or docx")

    import asyncio
    body = await asyncio.to_thread(fetch_blob_file, session_id, format)
    if not body:
        return Response(status_code=404, content="Quote not found")

    filename = PDF_FILENAME if format == "pdf" else DOCX_FILENAME
    media_type = PDF_MEDIA_TYPE if format == "pdf" else DOCX_MEDIA_TYPE
    return Response(
        content=body,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
