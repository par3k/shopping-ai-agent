import pytest

from app.config import load_settings


def test_load_settings_defaults():
    settings = load_settings({"DATABASE_URL": "x", "SECRET_KEY": "s", "REDIS_URL": "r"})

    assert settings.algorithm == "HS256"
    assert settings.access_token_expire_minutes == 30


def test_load_settings_reports_all_missing_keys():
    with pytest.raises(RuntimeError, match="DATABASE_URL") as exc_info:
        load_settings({})

    assert "SECRET_KEY" in str(exc_info.value)
    assert "REDIS_URL" in str(exc_info.value)
