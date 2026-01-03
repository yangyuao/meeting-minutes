from datetime import datetime
import logging
from pathlib import Path

from fastapi import APIRouter, File, Form, Request, UploadFile

from ..db import save_transcript_record
from ..services.asr import run_asr
from ..settings import Settings
from ..utils import get_client_ip

logger = logging.getLogger(__name__)

router = APIRouter()


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_model_manager(request: Request):
    return request.app.state.model_manager


def build_save_dir(base_dir: Path, username: str, client_ip: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    ip_dir = client_ip.replace(".", "_").replace(":", "_")
    return base_dir / username / ip_dir / timestamp


@router.post("/get_transcript")
async def get_transcript(
    request: Request, file: UploadFile = File(...), username: str = Form("unknown")
):
    settings = get_settings(request)
    client_ip = get_client_ip(request)
    logger.info("进入 get_transcript 接口，客户端IP: %s", client_ip)

    save_dir = build_save_dir(settings.audio_dir, username, client_ip)
    save_dir.mkdir(parents=True, exist_ok=True)

    audio_path = save_dir / file.filename
    content = await file.read()
    logger.info("文件大小: %d 字节", len(content))
    audio_path.write_bytes(content)
    logger.info("文件已保存到: %s", audio_path)

    try:
        model_manager = get_model_manager(request)
        full_text, audio_path, transcript_path = run_asr(
            model_manager,
            audio_path=audio_path,
            hotwords_path=settings.hotwords_path,
            output_dir=save_dir,
        )

        save_transcript_record(
            settings.db,
            client_ip,
            username,
            str(audio_path),
            str(transcript_path),
        )

        return {
            "transcript": full_text,
            "audio_file_path": str(audio_path),
            "transcript_file_path": str(transcript_path),
        }
    except Exception as exc:
        logger.error("语音识别失败: %s", exc)
        return {"error": str(exc)}
