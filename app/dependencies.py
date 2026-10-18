from collections.abc import Iterator

import redis
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Member
from app.redis_client import get_redis_client
from app.services.auth import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_redis() -> redis.Redis:
    return get_redis_client()


def logout_key(jti: str) -> str:
    return f"logout:{jti}"


def get_token_payload(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    redis_client: redis.Redis = Depends(get_redis),
) -> dict:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    try:
        payload = decode_access_token(credentials.credentials)
    except JWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")

    jti = payload.get("jti")
    if not jti:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")
    try:
        revoked = redis_client.exists(logout_key(jti))
    except redis.exceptions.RedisError:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Service unavailable")
    if revoked:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token revoked")
    return payload


def get_current_member(
    payload: dict = Depends(get_token_payload),
    db: Session = Depends(get_db),
) -> Member:
    try:
        member_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")
    member = db.get(Member, member_id)
    if member is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Member not found")
    return member
