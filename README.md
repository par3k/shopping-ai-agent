# shopping-ai-agent

FastAPI 기반 쇼핑몰 백엔드와 AI 챗봇을 단계별로 만들어 가는 프로젝트입니다. 만드는 과정을 블로그 글로 남기는 것이 목적이라, 각 단계가 끝난 시점의 코드를 그대로 열어볼 수 있도록 태그(`step-N-<주제>`)를 남깁니다.

## 단계 구조

| 단계 | 내용 |
|---|---|
| 1 | 서버 뼈대, DB·Redis 연결, 회원가입/로그인(JWT)/로그아웃(Redis로 즉시 무효화) |
| 2 | 기본 쇼핑몰 API: 상품·주문 조회, 구매 등 |
| 3 | RAG: 벡터 DB에 문서 수집·검색, `/chats` 도입 |
| 4 이후 | QUERY/ACTION 연결, LangGraph, 실행 전 사용자 확인(HITL), 시맨틱 캐시 등 |

설계와 근거는 [설계 문서](docs/superpowers/specs/2026-10-18-shopping-ai-agent-design.md), 단계별 계획은 `docs/superpowers/plans/`에 있습니다.

## 실행 방법

PostgreSQL(pgvector)과 Redis는 Docker 등으로 미리 띄워 둡니다. 예시:

```bash
docker run -d --name shopping-redis -p 6379:6379 redis:7
```

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # 값을 채웁니다
uvicorn app.main:app --reload --port 8001
```

API 문서는 `http://localhost:8001/docs`에서 볼 수 있습니다.

## 환경변수 (`.env`)

| 키 | 설명 |
|---|---|
| `DATABASE_URL` | PostgreSQL 접속 주소 (필수) |
| `SECRET_KEY` | JWT 서명 키 (필수) |
| `REDIS_URL` | Redis 접속 주소 (필수) |
| `ALGORITHM` | JWT 알고리즘 (기본 `HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 토큰 만료 분 (기본 30) |

필수 키가 없으면 서버가 시작할 때 빠진 키 이름을 알려 주며 실패합니다. `.env`는 커밋하지 않습니다.

## 테스트

```bash
pytest
```

SQLite 인메모리 DB와 fakeredis를 쓰므로 PostgreSQL이나 Redis 없이 실행됩니다.
