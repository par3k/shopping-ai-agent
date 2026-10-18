import logging
import time
import uuid

from fastapi import FastAPI, Request
from jose import JWTError

from app.services.auth import decode_access_token

access_logger = logging.getLogger("api.access")


def _member_id(request: Request) -> str:
    """토큰 값은 기록하지 않고 sub(회원 ID)만 꺼낸다. 검증 실패 시 '-'."""
    scheme, _, token = request.headers.get("authorization", "").partition(" ")
    if scheme.lower() != "bearer" or not token:
        return "-"
    try:
        return str(decode_access_token(token).get("sub", "-"))
    except JWTError:
        return "-"


def add_access_log(app: FastAPI) -> None:
    @app.middleware("http")
    async def access_log(request: Request, call_next):
        request_id = uuid.uuid4().hex[:12]
        started = time.perf_counter()
        path = request.url.path + (f"?{request.url.query}" if request.url.query else "")
        client = request.client.host if request.client else "-"
        member_id = _member_id(request)
        try:
            response = await call_next(request)
        except Exception:
            elapsed = (time.perf_counter() - started) * 1000
            access_logger.exception(
                "rid=%s %s %s member=%s client=%s status=500 %.1fms",
                request_id, request.method, path, member_id, client, elapsed,
            )
            raise
        elapsed = (time.perf_counter() - started) * 1000
        response.headers["X-Request-ID"] = request_id
        access_logger.info(
            "rid=%s %s %s member=%s client=%s status=%d %.1fms",
            request_id, request.method, path, member_id, client,
            response.status_code, elapsed,
        )
        return response
