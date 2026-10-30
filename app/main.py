from fastapi import FastAPI

from app.api import health, v1
from app.logging import configure_logging
from app.middleware import RequestIdMiddleware
from app.settings import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    configure_logging(settings.service_name, settings.log_level, settings.log_json)
    app = FastAPI(title=settings.service_name)
    app.state.settings = settings
    app.add_middleware(RequestIdMiddleware)
    app.include_router(health.router)
    app.include_router(v1.router)
    return app
