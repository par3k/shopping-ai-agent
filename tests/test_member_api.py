from datetime import timedelta

import pytest

from app.services.auth import create_access_token, decode_access_token


def signup(client, email="a@example.com", password="password1", **extra):
    return client.post(
        "/members/signup", json={"email": email, "password": password, **extra}
    )


def login_token(client, email="a@example.com", password="password1"):
    response = client.post("/members/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_signup_returns_member_without_password(client):
    response = signup(client, name="Kim", age=30)

    assert response.status_code == 201
    body = response.json()
    assert {"id", "email", "name", "age", "created_at"} <= body.keys()
    assert "password" not in body


def test_signup_duplicate_email_400(client):
    signup(client)

    response = signup(client)

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_signup_email_is_case_insensitive(client):
    assert signup(client, email="Kim@Example.com").status_code == 201

    login = client.post(
        "/members/login", json={"email": "kim@example.com", "password": "password1"}
    )
    assert login.status_code == 200
    assert signup(client, email="kim@example.com").status_code == 400


@pytest.mark.parametrize(
    "email, password",
    [
        ("a@example.com", "short"),
        ("not-an-email", "password1"),
        ("a@example.com", "가" * 25),  # 75바이트: bcrypt 한도(72바이트) 초과
    ],
)
def test_signup_validation_422(client, email, password):
    assert signup(client, email=email, password=password).status_code == 422


def test_login_success_returns_token(client):
    signup(client)

    response = client.post(
        "/members/login", json={"email": "a@example.com", "password": "password1"}
    )

    assert response.status_code == 200
    assert response.json()["access_token"]


def test_login_wrong_password_and_unknown_email_same_401(client):
    signup(client)

    wrong_password = client.post(
        "/members/login", json={"email": "a@example.com", "password": "wrongpass1"}
    )
    unknown_email = client.post(
        "/members/login", json={"email": "nobody@example.com", "password": "password1"}
    )

    for response in (wrong_password, unknown_email):
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid email or password"


def test_me_with_token(client):
    signup(client)

    response = client.get("/members/me", headers=auth(login_token(client)))

    assert response.status_code == 200
    assert response.json()["email"] == "a@example.com"


@pytest.mark.parametrize(
    "headers",
    [
        {},
        {"Authorization": "Bearer garbage"},
        auth(create_access_token({"sub": "1"}, timedelta(seconds=-1))),
        auth(create_access_token({"sub": "999"})),
        auth(create_access_token({"sub": "abc"})),
    ],
    ids=["no-header", "garbage", "expired", "unknown-member", "non-numeric-sub"],
)
def test_me_rejects_bad_auth(client, headers):
    signup(client)

    assert client.get("/members/me", headers=headers).status_code == 401


def test_logout_revokes_token_immediately(client):
    signup(client)
    token = login_token(client)

    logout = client.post("/members/logout", headers=auth(token))
    me = client.get("/members/me", headers=auth(token))

    assert logout.status_code == 204
    assert me.status_code == 401
    assert me.json()["detail"] == "Token revoked"


def test_logout_does_not_affect_other_tokens(client):
    signup(client)
    signup(client, email="b@example.com")
    token_a = login_token(client)
    token_b = login_token(client)
    other_member = login_token(client, email="b@example.com")

    client.post("/members/logout", headers=auth(token_a))

    assert client.get("/members/me", headers=auth(token_a)).status_code == 401
    assert client.get("/members/me", headers=auth(token_b)).status_code == 200
    assert client.get("/members/me", headers=auth(other_member)).status_code == 200


def test_logout_twice_401(client):
    signup(client)
    token = login_token(client)
    client.post("/members/logout", headers=auth(token))

    assert client.post("/members/logout", headers=auth(token)).status_code == 401


def test_logout_key_has_ttl(client, redis_client):
    signup(client)
    token = login_token(client)
    jti = decode_access_token(token)["jti"]

    client.post("/members/logout", headers=auth(token))

    ttl = redis_client.ttl(f"logout:{jti}")
    assert 0 < ttl <= 30 * 60


def test_redis_down_returns_503(client, redis_server):
    signup(client)
    token = login_token(client)
    redis_server.connected = False

    me = client.get("/members/me", headers=auth(token))
    logout = client.post("/members/logout", headers=auth(token))

    for response in (me, logout):
        assert response.status_code == 503
        assert response.json()["detail"] == "Service unavailable"
