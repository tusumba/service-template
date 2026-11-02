# service-template

Шаблон сервиса бэкенда Tusumba.

**Ответственный:** Глеб Эстраих (задача #18887).

## Что внутри

смотрите в pyproject.toml 

## Как создать сервис

1. На GitHub нажмите **Use this template** и создайте репозиторий, например `events-service`.
   Если репозиторий уже есть, скопируйте в него файлы шаблона.
2. Переименуйте шаблон под сервис:

   ```bash
   python3 scripts/new_service.py events
   uv sync
   uv run pytest
   ```

   Скрипт заменит имя шаблона в настройках, схеме PostgreSQL, Docker и CI, а затем удалит себя.
3. Закоммитьте результат.

## Локальный запуск

Нужны [uv](https://docs.astral.sh/uv/) и Docker.

```bash
uv sync
cp .env.example .env
docker compose up -d postgres
uv run alembic upgrade head
uv run uvicorn app.main:create_app --factory --reload
```

Сервис: http://127.0.0.1:8000/health, документация API: http://127.0.0.1:8000/docs.

Всё в Docker:

```bash
docker compose up --build
```

## Проверки

```bash
uv run ruff format .
uv run ruff check .
uv run mypy app tests migrations
uv run pytest
```

## Переменные окружения

| Переменная | По умолчанию | Что это |
|---|---|---|
| `DATABASE_URL` | обязательна | `postgresql+asyncpg://user:password@host:5432/db` |
| `SERVICE_NAME` | имя сервиса | попадает в логи |
| `LOG_LEVEL` | `INFO` | уровень логов |
| `LOG_JSON` | `true` | `false` — читаемые логи для отладки |
| `DATABASE_POOL_SIZE` | `5` | размер пула соединений |
| `DATABASE_ECHO` | `false` | печатать SQL-запросы |

## Структура

```
app/
  main.py          create_app()
  settings.py      настройки окружения
  logging.py       JSON-логи
  middleware.py    request_id и лог запросов
  db.py            сессии
  api/health.py    /health
  api/v1/          публичные роутеры
  models/          модели SQLAlchemy, схема сервиса
migrations/        Alembic
tests/             pytest + testcontainers
scripts/           new_service.py — переименование шаблона
```

## Документация

Wiki проекта: https://ai.nsu.ru/projects/tusumba/wiki/Архитектура.

Задачи ведутся в Redmine: https://ai.nsu.ru/projects/tusumba.
