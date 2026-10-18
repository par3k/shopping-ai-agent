import time

import redis
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.dependencies import (
    get_current_member,
    get_db,
    get_redis,
    get_token_payload,
    logout_key,
)
from app.models import Member
from app.schemas import LoginRequest, MemberCreate, MemberResponse, TokenResponse
from app.services.auth import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/members", tags=["members"])


def find_by_email(db: Session, email: str) -> Member | None:
    return db.scalar(select(Member).where(Member.email == email.lower()))


@router.post("/signup", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
def signup(body: MemberCreate, db: Session = Depends(get_db)):
    if find_by_email(db, body.email) is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email already registered")
    member = Member(
        email=body.email.lower(),
        password=hash_password(body.password),
        name=body.name,
        age=body.age,
    )
    db.add(member)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email already registered")
    db.refresh(member)
    return member


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    member = find_by_email(db, body.email)
    if member is None or not verify_password(body.password, member.password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")
    return TokenResponse(access_token=create_access_token({"sub": str(member.id)}))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    payload: dict = Depends(get_token_payload),
    _member: Member = Depends(get_current_member),
    redis_client: redis.Redis = Depends(get_redis),
):
    ttl = max(int(payload["exp"] - time.time()), 1)
    try:
        redis_client.set(logout_key(payload["jti"]), "1", ex=ttl)
    except redis.exceptions.RedisError:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Service unavailable")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=MemberResponse)
def me(member: Member = Depends(get_current_member)):
    return member
