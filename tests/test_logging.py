import logging
import os
from pathlib import Path

from app.logging_config import AppFormatter


def flush_handlers():
    for handler in logging.getLogger().handlers:
        handler.flush()


def read_log() -> str:
    flush_handlers()
    return (Path(os.environ["LOG_DIR"]) / "app.log").read_text(encoding="utf-8")


def test_응답에_request_id_헤더가_붙는다(client):
    response = client.get("/health")
    assert len(response.headers["X-Request-ID"]) == 12


def test_access_로그에_요청정보가_남고_토큰은_남지_않는다(client):
    client.post(
        "/members/signup",
        json={"email": "a@test.com", "password": "pw123456", "name": "가", "age": 20},
    )
    token = client.post(
        "/members/login", json={"email": "a@test.com", "password": "pw123456"}
    ).json()["access_token"]
    response = client.get("/members/me?x=1", headers={"Authorization": f"Bearer {token}"})

    log = read_log()
    assert f"rid={response.headers['X-Request-ID']} GET /members/me?x=1 member=1" in log
    assert "status=200" in log
    assert token not in log
    assert "pw123456" not in log


def test_업무로그에_가입_로그인_실패가_남는다(client):
    client.post(
        "/members/login", json={"email": "none@test.com", "password": "pw123456"}
    )
    assert "[api.member] 로그인 실패: email=none@test.com" in read_log()


def test_sql_로그는_길면_잘린다():
    record = logging.LogRecord("sqlalchemy.engine.Engine", logging.INFO, "", 0, "x" * 3000, None, None)
    assert len(AppFormatter().format(record)) < 1600
