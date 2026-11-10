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
uv run python -m tusumba_common.testing dev-keys   # тестовая пара ключей, впишите public.pem в JWT_PUBLIC_KEY
docker compose up -d postgres rabbitmq
uv run alembic upgrade head
uv run --env-file .env uvicorn app.main:create_app --factory --reload
```

`JWT_PUBLIC_KEY` и `SERVICE_TOKEN` читает tusumba-common из окружения процесса, а не из `Settings`,
поэтому сервис запускается с `--env-file .env`.

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
| `RABBITMQ_URL` | обязательна | адрес RabbitMQ, например `amqp://guest:guest@localhost:5672/` |
| `OUTBOX_POLL_SECONDS` | `1.0` | интервал отправки событий из outbox в секундах |
| `SERVICE_NAME` | имя сервиса | попадает в логи |
| `LOG_LEVEL` | `INFO` | уровень логов |
| `LOG_JSON` | `true` | `false` — читаемые логи для отладки |
| `DATABASE_POOL_SIZE` | `5` | размер пула соединений |
| `DATABASE_ECHO` | `false` | печатать SQL-запросы |
| `JWT_PUBLIC_KEY` | обязательна для путей со входом | публичный ключ Identity в PEM, проверка access-токенов (tusumba-common) |
| `SERVICE_TOKEN` | обязательна для `/internal` | общий сервисный токен для заголовка `X-Service-Token` (tusumba-common) |

## Авторизация и ошибки

Шаблон подключает [tusumba-common](https://github.com/tusumba/tusumba-common) по тегу версии
(`pyproject.toml`), как требует #18886:

- `install_error_handlers` в `create_app()`: любая ошибка, включая валидацию и 404, приходит в формате
  `{"error": {"code": "...", "message": "...", "details": [...]}}`, как в OpenAPI сервисов;
- `Depends(get_current_user)` - путь только со входом (access-токен JWT RS256), `Depends(optional_user)` -
  можно без входа, но испорченный токен даёт 401; пример - `app/api/v1/example.py`;
- `/internal` - роутер с `dependencies=[Depends(require_service)]`: без верного `X-Service-Token` ответ 403;
  пример - `app/api/internal.py`. Вызовы других сервисов - через `InternalClient`.

Примеры `/v1/example/...` и `/internal/example/ping` замените своими роутерами. Тесты на токены и формат
ошибок - `tests/test_auth.py`, токены выпускает `tusumba_common.testing.make_token`.

## События

`app.events.enqueue_event(session, event)` создаёт конверт контракта и добавляет запись в outbox.
Вызывайте его с той же `AsyncSession`, в которой меняются данные сервиса, до общего `commit`.
После коммита встроенный APScheduler отправляет ожидающие записи в RabbitMQ через FastStream и помечает
их отправленными после подтверждения публикации. Если отправка прервётся, запись останется в outbox
для следующей попытки с тем же `event_id`.

Для приёма зарегистрируйте обработчик через `subscribe_event(broker, sessions, queue=...,
routing_key=..., handler=...)` **до** `broker.start()` в `app/main.py`. Обработчик получает `AsyncSession`
и разобранный `EventEnvelope`; его изменения и ID обработанного события фиксируются одной транзакцией.
При ошибке транзакция откатывается, а сообщение возвращается в очередь. Используйте отдельное имя
очереди для каждого сервиса и routing key из `tusumba-contracts`.

## Структура

```
app/
  main.py          create_app()
  settings.py      настройки окружения
  logging.py       JSON-логи
  middleware.py    request_id и лог запросов
  db.py            сессии
  api/health.py    /health
  api/v1/          публичные роутеры (example.py - пример со входом)
  api/internal.py  пути /internal по сервисному токену
  models/          модели SQLAlchemy, схема сервиса
migrations/        Alembic
tests/             pytest + testcontainers
scripts/           new_service.py — переименование шаблона
```

## Документация

Wiki проекта: https://ai.nsu.ru/projects/tusumba/wiki/Архитектура.

Задачи ведутся в Redmine: https://ai.nsu.ru/projects/tusumba.

## Правила работы

Описаны в [CONTRIBUTING.md](https://github.com/tusumba/.github/blob/main/CONTRIBUTING.md).
