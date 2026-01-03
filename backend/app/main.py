from __future__ import annotations

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .db import init_database
from .logging_setup import configure_logging
from .services.asr import ASRConfig, ModelManager
from .settings import Settings
from .routers import core, docx, summary, test, transcript, upload

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    load_dotenv()
    settings = Settings.from_env()
    configure_logging(settings.log_level)

    app = FastAPI()
    app.state.settings = settings
    app.state.model_manager = ModelManager(
        ASRConfig(
            asr_model=settings.asr_model,
            vad_model=settings.vad_model,
            punc_model=settings.punc_model,
            spk_model=settings.spk_model,
            device=settings.device,
        )
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(core.router)
    app.include_router(test.router)
    app.include_router(transcript.router)
    app.include_router(summary.router)
    app.include_router(upload.router)
    app.include_router(docx.router)

    @app.on_event("startup")
    async def on_startup() -> None:
        init_database(settings.db)
        logger.info("应用启动完成")

    return app


app = create_app()
