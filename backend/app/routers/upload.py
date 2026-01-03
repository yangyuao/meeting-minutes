from datetime import datetime
import logging
from pathlib import Path

from fastapi import APIRouter, File, Form, Request, UploadFile

from ..db import save_transcript_record
from ..settings import Settings
from ..utils import get_client_ip

logger = logging.getLogger(__name__)

router = APIRouter()


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def build_save_dir(base_dir: Path, username: str, client_ip: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    ip_dir = client_ip.replace(".", "_").replace(":", "_")
    return base_dir / username / ip_dir / timestamp


@router.post("/upload")
async def upload_audio(
    request: Request, file: UploadFile = File(...), username: str = Form("unknown")
):
    settings = get_settings(request)
    client_ip = get_client_ip(request)
    logger.info("进入 upload 接口，客户端IP: %s", client_ip)

    save_dir = build_save_dir(settings.audio_dir, username, client_ip)
    save_dir.mkdir(parents=True, exist_ok=True)

    file_path = save_dir / file.filename
    content = await file.read()
    logger.info("文件大小: %d 字节", len(content))
    file_path.write_bytes(content)

    logger.info("文件已保存到: %s", file_path)

    save_transcript_record(settings.db, client_ip, username, str(file_path), "")

    return {
        "message": "文件上传成功",
        "file_path": str(file_path),
        "client_ip": client_ip,
        "username": username,
    }
