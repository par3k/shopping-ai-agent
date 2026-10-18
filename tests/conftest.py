import os

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "test-secret"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    # get_db / get_redis 오버라이드와 테이블 생성은 Task 3에서 dependencies.py가 생긴 뒤 연결한다.
    with TestClient(app) as test_client:
        yield test_client
