import os
from collections.abc import Mapping
from dataclasses import dataclass

REQUIRED_KEYS = ("DATABASE_URL", "SECRET_KEY", "REDIS_URL")


@dataclass(frozen=True)
class Settings:
    database_url: str
    secret_key: str
    redis_url: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30


def load_settings(env: Mapping[str, str] | None = None) -> Settings:
    env = os.environ if env is None else env
    missing = [key for key in REQUIRED_KEYS if not env.get(key)]
    if missing:
        raise RuntimeError(f"필수 환경변수가 없습니다: {', '.join(missing)}")
    return Settings(
        database_url=env["DATABASE_URL"],
        secret_key=env["SECRET_KEY"],
        redis_url=env["REDIS_URL"],
        algorithm=env.get("ALGORITHM") or "HS256",
        access_token_expire_minutes=int(env.get("ACCESS_TOKEN_EXPIRE_MINUTES") or 30),
    )
