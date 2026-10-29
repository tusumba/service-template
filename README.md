# service-template

Шаблон сервиса бэкенда Tusumba. От него стартуют новые сервисы, чтобы все они имели одинаковую структуру.

**Ответственный:** Глеб Эстраих (задача #18887).

## Что внутри

- FastAPI-приложение со структурой каталогов;
- SQLAlchemy 2 (async) и Alembic для миграций;
- настройка логирования;
- healthcheck-эндпоинт;
- тесты на pytest + testcontainers (реальный PostgreSQL в тестах);
- подключение `tusumba-common`.

## Как использовать

Описание появится после готовности шаблона (#18887).

## Стек

Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2 (async), Alembic, pytest + testcontainers, ruff, mypy.

## Документация

Wiki проекта: https://ai.nsu.ru/projects/tusumba/wiki/Архитектура. Задачи ведутся в Redmine: https://ai.nsu.ru/projects/tusumba. Issues и Wiki GitHub выключены.

## Правила работы

Ветки, коммиты, pull request и code review описаны в [CONTRIBUTING.md](https://github.com/tusumba/.github/blob/main/CONTRIBUTING.md). Коротко:

- ветка называется `feature/<номер задачи Redmine>-<пара слов>`, например `feature/18901-login`;
- номер задачи указывается в каждом коммите и в названии PR;
- в `main` изменения попадают только через PR с одним одобрением и зелёным CI, прямой push и force push запрещены.
