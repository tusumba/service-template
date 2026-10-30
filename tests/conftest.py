from collections.abc import AsyncIterator, Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from testcontainers.community.postgres import PostgresContainer

from app.db import create_engine
from app.main import create_app
from app.settings import Settings

SERVICE_DIR = Path(__file__).resolve().parents[1]
POSTGRES_IMAGE = "postgres:16-alpine"


@pytest.fixture(scope="session")
def database_url() -> Iterator[str]:
    with PostgresContainer(POSTGRES_IMAGE, driver="asyncpg") as postgres:
        yield postgres.get_connection_url()


@pytest.fixture(scope="session")
def alembic_config(database_url: str) -> Config:
    config = Config(SERVICE_DIR / "alembic.ini")
    config.set_main_option("script_location", str(SERVICE_DIR / "migrations"))
    config.set_main_option("sqlalchemy.url", database_url)
    config.attributes["configure_logger"] = False
    return config


@pytest.fixture(scope="session")
def migrated(alembic_config: Config) -> None:
    command.upgrade(alembic_config, "head")


@pytest.fixture
def settings(database_url: str, migrated: None) -> Settings:
    return Settings(
        service_name="service_template",
        environment="test",
        database_url=database_url,
    )


@pytest.fixture
def client(settings: Settings) -> Iterator[TestClient]:
    with TestClient(create_app(settings)) as test_client:
        yield test_client


@pytest.fixture
async def session(settings: Settings) -> AsyncIterator[AsyncSession]:
    engine = create_engine(settings)
    async with engine.connect() as connection:
        transaction = await connection.begin()
        async with AsyncSession(
            bind=connection, join_transaction_mode="create_savepoint", expire_on_commit=False
        ) as db_session:
            yield db_session
        await transaction.rollback()
    await engine.dispose()
