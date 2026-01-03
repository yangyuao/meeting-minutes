"""Backend entrypoint using the refactored application."""

from dotenv import load_dotenv
import uvicorn

from backend.app.main import app
from backend.app.settings import Settings


if __name__ == "__main__":
    load_dotenv()
    settings = Settings.from_env()
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
