from fastapi import FastAPI

from app.api import v1
from app.settings import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    app = FastAPI(title=settings.service_name)
    app.state.settings = settings
    app.include_router(v1.router)
    return app
