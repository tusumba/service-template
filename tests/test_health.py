import json

import pytest
from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert len(response.headers["X-Request-ID"]) == 32


def test_request_id_is_taken_from_header(client: TestClient) -> None:
    response = client.get("/health", headers={"X-Request-ID": "abc-123"})
    assert response.headers["X-Request-ID"] == "abc-123"


def test_unsafe_request_id_is_replaced(client: TestClient) -> None:
    response = client.get("/health", headers={"X-Request-ID": "bad\nvalue"})
    assert response.headers["X-Request-ID"] != "bad\nvalue"


def test_access_log_is_json(capsys: pytest.CaptureFixture[str], client: TestClient) -> None:
    capsys.readouterr()
    response = client.get("/health", headers={"X-Request-ID": "trace-1"})
    lines = [json.loads(line) for line in capsys.readouterr().out.splitlines() if line]
    access = [entry for entry in lines if entry["logger"] == "app.access"]
    assert access, lines
    assert access[-1]["service"] == "service_template"
    assert access[-1]["request_id"] == "trace-1"
    assert access[-1]["path"] == "/health"
    assert access[-1]["status"] == response.status_code
    assert access[-1]["level"] == "INFO"


def test_v1_prefix_exists(client: TestClient) -> None:
    assert client.get("/v1/unknown").status_code == 404
