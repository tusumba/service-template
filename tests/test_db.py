import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import SCHEMA


async def test_session_works_in_service_schema(session: AsyncSession) -> None:
    assert await session.scalar(text("SELECT current_schema()")) == SCHEMA


async def test_alembic_version_lives_in_service_schema(session: AsyncSession) -> None:
    table = await session.scalar(
        text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = :schema AND table_name = 'alembic_version'"
        ),
        {"schema": SCHEMA},
    )
    assert table == "alembic_version"


async def test_changes_are_rolled_back_after_test(session: AsyncSession) -> None:
    await session.execute(text("CREATE TABLE rollback_check (id int)"))
    await session.execute(text("INSERT INTO rollback_check VALUES (1)"))
    assert await session.scalar(text("SELECT count(*) FROM rollback_check")) == 1


async def test_previous_test_left_nothing(session: AsyncSession) -> None:
    found = await session.scalar(text("SELECT to_regclass('rollback_check')"))
    assert found is None


@pytest.mark.usefixtures("migrated")
def test_migrations_downgrade_and_upgrade(alembic_config: Config) -> None:
    command.downgrade(alembic_config, "base")
    command.upgrade(alembic_config, "head")
