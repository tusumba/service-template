from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.settings import Settings


@pytest.fixture
def settings() -> Settings:
    return Settings(
        service_name="service_template",
        environment="test",
        database_url="postgresql+asyncpg://test:test@localhost:5432/test",
    )


@pytest.fixture
def client(settings: Settings) -> Iterator[TestClient]:
    with TestClient(create_app(settings)) as test_client:
        yield test_client
