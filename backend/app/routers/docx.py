import logging
import os
import tempfile
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse

from ..schemas import DocxRequest
from ..services.docx_export import generate_docx_file
from ..settings import Settings

logger = logging.getLogger(__name__)

router = APIRouter()


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


@router.post("/generate_docx")
async def generate_docx(request: Request, payload: DocxRequest):
    settings = get_settings(request)
    markdown_text = payload.markdown

    if not markdown_text:
        raise HTTPException(status_code=400, detail="Missing markdown content")

    fd, temp_path = tempfile.mkstemp(suffix=".docx")
    os.close(fd)
    output_path = Path(temp_path)

    try:
        generate_docx_file(
            markdown_text=markdown_text,
            template_path=settings.template_path,
            output_path=output_path,
        )
    except FileNotFoundError as exc:
        logger.error("Template file missing: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("Failed to generate DOCX: %s", exc)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate DOCX. Error: {exc}",
        ) from exc

    filename = f"meeting_minutes_{output_path.stem}.docx"
    return FileResponse(
        path=str(output_path),
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
