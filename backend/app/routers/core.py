import logging

from fastapi import APIRouter, Request

from ..settings import Settings

logger = logging.getLogger(__name__)

router = APIRouter()


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


@router.get("/")
async def read_root(request: Request):
    logger.info("访问根路径，服务运行正常")
    return {"message": "Backend is running"}


@router.get("/prompt/default")
async def get_default_prompt(request: Request):
    settings = get_settings(request)
    logger.info("获取默认提示词模板")
    return {"prompt": settings.prompt_template}
