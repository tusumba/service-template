import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PLACEHOLDER = "service_template"
REPO_PLACEHOLDER = "service-template"
SKIP_DIRS = {".git", ".venv", ".mypy_cache", ".ruff_cache", ".pytest_cache", "__pycache__"}
NAME = re.compile(r"^[a-z][a-z0-9_]{1,30}$")


def text_files() -> list[Path]:
    files = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or SKIP_DIRS & set(path.relative_to(ROOT).parts):
            continue
        if path == Path(__file__).resolve():
            continue
        try:
            path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        files.append(path)
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description="Создать сервис из шаблона: переименовать его.")
    parser.add_argument("name", help="имя сервиса латиницей, например events")
    name = parser.parse_args().name
    if not NAME.match(name):
        print("Имя: строчные латинские буквы, цифры и _, начинается с буквы", file=sys.stderr)
        return 2
    repo_name = f"{name.replace('_', '-')}-service"
    changed = []
    for path in text_files():
        text = path.read_text(encoding="utf-8")
        updated = text.replace(REPO_PLACEHOLDER, repo_name).replace(SCHEMA_PLACEHOLDER, name)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed.append(path.relative_to(ROOT))
    if not changed:
        print("Шаблон уже переименован: ничего не изменено", file=sys.stderr)
        return 1
    for path in sorted(changed):
        print(f"изменён {path}")
    Path(__file__).unlink()
    print(f"Готово: сервис {name}, схема PostgreSQL {name}, пакет {repo_name}.")
    print("Дальше: uv sync && uv run pytest")
    return 0


if __name__ == "__main__":
    sys.exit(main())
