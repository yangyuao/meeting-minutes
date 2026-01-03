import logging

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from ..db import save_meeting_record
from ..schemas import SummaryRequest
from ..services.asr import clean_speech
from ..services.llm import unified_streamer
from ..settings import Settings
from ..utils import get_client_ip

logger = logging.getLogger(__name__)

router = APIRouter()


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


@router.post("/generate_summary")
async def generate_summary(request: Request, payload: SummaryRequest):
    settings = get_settings(request)
    client_ip = get_client_ip(request)
    logger.info("进入 generate_summary 接口，客户端IP: %s", client_ip)

    full_text = payload.transcript
    prompt = payload.prompt

    cleaned_text = clean_speech(full_text)
    logger.info("文本清洗完成")
    logger.debug("文本清洗结果: %s", cleaned_text)

    system_prompt = prompt.strip() or settings.prompt_template
    final_prompt = f"{system_prompt}\n\n{cleaned_text}"
    logger.info("构建最终提示词完成")

    is_production = client_ip == settings.production_ip
    logger.info("正在返回 StreamingResponse (生产环境: %s)", is_production)

    generated_summary = ""

    def summary_streamer():
        nonlocal generated_summary
        for chunk in unified_streamer(
            settings=settings,
            system_prompt=system_prompt,
            user_prompt=cleaned_text,
            is_production=is_production,
        ):
            generated_summary += chunk
            yield chunk

        try:
            save_meeting_record(
                settings.db,
                client_ip,
                payload.username,
                full_text,
                final_prompt,
                generated_summary,
            )
            logger.info("会议记录已保存到数据库")
        except Exception as exc:
            logger.error("保存会议记录到数据库失败: %s", exc)

    return StreamingResponse(
        summary_streamer(),
        media_type="text/plain",
        headers={
            "Content-Type": "text/plain; charset=utf-8",
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
