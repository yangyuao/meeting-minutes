from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from ..services.llm import generate_vllm_stream
from ..settings import Settings

router = APIRouter()


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


@router.get("/test-vllm")
async def test_vllm(request: Request):
    settings = get_settings(request)
    return StreamingResponse(
        generate_vllm_stream(settings, system_prompt=settings.prompt_template, user_prompt="请介绍你自己"),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
