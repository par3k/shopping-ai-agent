# CLAUDE.md

이 파일은 Claude Code가 세션마다 자동으로 읽는 프로젝트 지침입니다.
사용자가 요청한 작업 방식과 규칙을 여기에 누적해서 기록합니다. 새 규칙이 생기면 이 파일에 추가하세요.
(이전 프로젝트 `asiana-ai-workflow`의 CLAUDE.md에 쌓인 사용자 지시를 이 프로젝트 기준으로 옮겨 정리했습니다.)

## 프로젝트 개요
- FastAPI 기반 쇼핑몰 백엔드 + AI 챗봇을 단계별로 만들어 가는 프로젝트. 만드는 과정을 블로그 글로 남기는 것이 목적이다.
- 원격 저장소: https://github.com/par3k/shopping-ai-agent.git (origin, 기본 브랜치 `main`)
- 설계와 단계 구조는 [설계 문서](docs/superpowers/specs/2026-10-18-shopping-ai-agent-design.md), 단계별 계획은 `docs/superpowers/plans/` 참고
- 단계는 사용자가 "이 정도면 됐어"라고 말해야 끝난다. 먼저 종료를 선언하지 않는다.

## 기술 스택
- 웹/DB: FastAPI, SQLAlchemy, PostgreSQL(pgvector), Redis(redis-py), JWT(python-jose, bcrypt), Pydantic
- Redis 용도: 로그아웃 시 JWT 즉시 무효화(`logout:{jti}` 키, TTL=토큰 남은 시간), 챗 응답 캐시. 장애 시 인증은 503으로 거부하고 캐시는 건너뛴다.
- AI(후속 단계): OpenAI(gpt-4.1-mini, 임베딩 text-embedding-3-large), LangChain, LangGraph

## 작업 규칙 (사용자 지시)

### 언어
- 모든 응답과 설명은 한국어로 작성한다. 코드 식별자와 기술 용어는 원문 그대로 둔다.
- 사용자 전역 설정(`~/.claude/settings.json`)에 `"language": "korean"`이 설정되어 있다.

### Git 작업 방식
- 소스나 설정을 수정할 때는 `main`에 직접 커밋하지 않는다.
  1. 작업마다 새 브랜치를 만든다 (`feature/<작업>`, `docs/<작업>`, `chore/<작업>` 등).
  2. 브랜치에서 수정하고 커밋한다.
  3. 로컬 `main`에 `--no-ff`로 머지한다.
- 커밋과 push는 사용자에게 허락을 구하지 않고 알아서 처리한다. 작업이 끝나면 브랜치 작업 → 커밋 → 로컬 `main` 머지 → `git push origin main`까지 진행하고, 마지막에 처리 결과(커밋/머지/push 내역)를 사용자에게 알려준다. "깃에 올려줘"도 push까지 포함한 요청이다.
- 사용자가 직접 수정한 커밋되지 않은 파일이 있으면 내용을 확인하고 함께 커밋한다.
- 변경 전에 매번 허락을 구하지 않고 알아서 진행한다. 단 삭제, force push(`--force`), 원격 브랜치 삭제 같은 되돌리기 어려운 작업은 예외로 먼저 확인한다.
- 커밋 메시지는 한국어로 쓰고, 끝에 Co-Authored-By 줄을 붙인다.
- 이 레포의 git 작성자는 레포 로컬 설정이다 (`user.email=hoijae0194@gmail.com`, `user.name=par3k`).
- 머지 후에는 작업 폴더의 `.env`가 남아 있는지 확인한다. (이전 프로젝트에서 머지 중 `.env`가 삭제된 적이 있다.)

### Docker
- 사용자가 따로 요청하지 않으면 Docker(컨테이너, 이미지)를 조작하지 않는다. (`docker run/exec/stop/rm` 모두 포함) Redis 컨테이너도 마찬가지로 사용자가 직접 띄운다.
- 컨테이너 안에서 해야 하는 작업은 명령어만 안내한다.
- 서버를 종료할 때는 이 프로젝트에서 직접 띄운 프로세스만 대상으로 한다. 포트(8000) 점유 프로세스를 PID 확인 없이 종료하지 않는다(이전 프로젝트에서 사용자가 직접 띄운 서버를 끈 적이 있다). 서버 테스트는 사용자 서버와 겹치지 않게 다른 포트(예: 8001)로 띄우고, 자기가 띄운 PID만 종료한다.

### 보안
- `.env`의 값(API 키, DB 비밀번호)을 출력하거나 문서에 적지 않는다. 키 이름만 언급한다.
- `.env`는 `.gitignore`에 포함되어 있다. 커밋하지 않는다.
- 키 재발급 여부는 사용자가 판단한다.

### 로깅 (이전 프로젝트에서 요청한 방식, 해당 단계에서 동일하게 적용)
- 로그 파일은 롤링한다: `log/app.log`(워크스페이스 루트, 10MB x 5개 보관), `print()`·uvicorn·root 로거를 함께 기록. 위치는 `LOG_DIR`로 변경 가능. `log/`는 `.gitignore` 대상이다.
- 모든 API 요청을 `api.access` 로그로 기록한다(요청ID, method, path+query, member_id, client, 상태코드, 소요시간). 비밀번호 등이 있을 수 있어 요청 body와 토큰 값은 기록하지 않는다. 응답 헤더에 `X-Request-ID`를 붙인다.
- 라우터별 업무 로그(`api.member/order/product/document/chat`)를 남긴다: 가입·로그인 성공/실패, 주문 생성/취소, 상품 등록/수정/조회, 문서 추가/수정, 챗 질문(100자)·분류·응답길이.
- 실행되는 SQL(`sqlalchemy.engine`)은 파일에만 기록한다. 바인딩 파라미터는 `hide_parameters`로 숨기고(`SQL_LOG_PARAMS=true`면 표시), 한 건이 1500자를 넘으면 잘라서 기록한다. `SQL_LOG=false`로 끌 수 있다.
- LLM 직접 호출은 요청·응답·토큰·소요시간·오류를 `api.llm` 로그로 기록한다(질문/응답은 200자까지).
- 로그 파일은 UTF-8로 읽는다(그냥 열면 한글이 깨져 보일 수 있다).

### AI 단계 (후속 단계에서 요청한 내용)
- 이전 프로젝트의 챗 파이프라인 순서: 캐시 → 1차 분류 → get_api(QUERY/ACTION/GENERAL)/profile/policy/general → 캐시 저장. ACTION은 실행 전 `interrupt()`로 사용자 확인("예/아니오", HITL)을 받는다.
- LLM은 OpenAI(gpt-4.1-mini)를 쓴다. Anthropic Claude로 전환했다가 사용자 판단으로 OpenAI로 원복한 이력이 있으니 임의로 바꾸지 않는다.
- LangSmith/Langfuse로 관측하며 키는 `.env`에만 둔다.

### 블로그 포스팅 (`~/Downloads/workspace/par3k.github.io`)
- 별도 규칙 문서는 없다. 기존 `_posts` 글의 관례를 따른다: 파일명 `YYYY-MM-DD-slug.md`, front matter(`layout: post`, `title`, `date`, `categories: [테크]`, `tags`), "이번 포스팅에서는 …" 도입부, `---` 구분, "마치며", 합니다체. 커밋은 `post/<주제>` 브랜치에서 `post: …`로 하고 `main`에 `--no-ff` 머지 후 push한다.
- 글에는 "미리 전체를 설계해 두고 단계별로 하나씩 만들어 간다"는 뉘앙스를 넣지 않는다. 전체 단계 계획, 앞으로 만들 기능 예고, "N단계" 같은 표현을 쓰지 않고, 지금 만든 것과 그 과정에서의 결정만 쓴다. (설계 문서의 단계 구조는 내부 작업용이다.)
- 이메일, 비밀번호, 키 값은 글에 쓰지 않는다.

## 개발 환경
- Python 3.13 가상환경: `.venv` (3.14는 일부 패키지 wheel이 없어 사용하지 않음)
- 실행: `uvicorn app.main:app --reload` (기본 포트 8000, 문서 `/docs`)
- DB: 사용자가 Docker로 직접 띄운 PostgreSQL(pgvector) 컨테이너. 이전 프로젝트는 호스트 포트 5433을 썼다. 포트와 DB 이름은 `.env`의 `DATABASE_URL`을 따른다.
- Redis: 사용자가 Docker로 직접 띄운다. 주소는 `.env`의 `REDIS_URL`을 따른다. 테스트는 fakeredis로 돌려서 Redis 없이 실행된다.
- 마이그레이션 도구는 쓰지 않고 앱 시작 시 `Base.metadata.create_all`로 테이블을 만든다.

## 진행 현황 (세션이 바뀌어도 이어가기 위한 기록, 단계가 진행될 때마다 갱신)

### 1단계: 서버 뼈대 + 회원가입/로그인 — 완료 (2026-10-18, 사용자가 "이 정도면 됐어"로 종료 선언)
- git 태그 `step-1-login`을 달아 push했다. 이후 단계는 사용자가 시작을 말해야 진행한다. 다음은 2단계(상품·주문)이며 [설계 문서](docs/superpowers/specs/2026-10-18-shopping-ai-agent-design.md)의 단계 구조 표를 따른다. 새 단계는 계획 문서를 `docs/superpowers/plans/`에 만든다.
- 구현된 API: `POST /members/signup`, `POST /members/login`, `POST /members/logout`(Redis `logout:{jti}`), `GET /members/me`, `GET /health`
- 인증 정책: 이메일은 소문자로 저장, 비밀번호는 bcrypt, JWT는 HS256에 `jti` 포함. Redis 오류 시 인증은 503으로 거부.
- 로깅 구현 완료(`app/logging_config.py`, `app/middleware.py`, `api.member` 업무 로그). 로그 디렉토리는 사용자 요청으로 워크스페이스 루트의 `log/`다(`logs/` 아님). 이후 단계의 라우터에도 `api.<이름>` 업무 로그를 같은 방식으로 추가한다.
- 테스트 31개 통과(`.venv/bin/python -m pytest -q`). DB는 SQLite 인메모리, Redis는 fakeredis, 로그 디렉토리는 임시 폴더(`tests/conftest.py`).
- 실서버 `curl` 흐름(가입→중복→로그인→me→로그아웃→같은 토큰 401) 확인 완료. 테스트로 만든 회원 행은 삭제했다. `members`에는 사용자 본인 계정(id=1)이 있으니 건드리지 않는다.
- 블로그 글 작성·게시 완료: `par3k.github.io/_posts/2026-10-18-fastapi-shopping-mall-signup-login-redis-logout.md`. 사용자 요청으로 "트러블슈팅(psycopg)"과 "테스트" 섹션을 뺐고, 사전 설계/단계별 제작 뉘앙스도 뺐다. 글에 남은 "테스트로도 고정해 두었습니다", "테스트가 통과해도…" 문장을 다듬을지는 사용자 답변 대기 중.

### 환경 메모 (값은 적지 않는다)
- PostgreSQL은 `localhost:5433`, DB 이름 `shopping-ai-agent`(스키마가 아니라 DB 이름이다), 스키마 `public`, 테이블 `members`. 같은 서버에 `postgres`, `myuser`, `ai_agent_db`(이전 프로젝트) DB도 있다. DBeaver에서 안 보이면 연결의 PostgreSQL 탭에서 Show all databases를 켠다.
- Redis는 `localhost:6379/0`.
- `DATABASE_URL`은 `postgresql+psycopg2://` 접두사를 써야 한다. SQLAlchemy 2.1은 `postgresql://`이면 psycopg v3를 찾아서 `No module named 'psycopg'`가 난다.
- `.env.example`은 사용자 요청으로 삭제했다. 다시 만들지 않는다. 환경변수 키 목록은 README의 환경변수 표가 기준이다.
- 서버 실행은 `.venv/bin/uvicorn app.main:app --reload --port 8000`. 세션이 끝나면 내가 띄운 서버도 같이 끝났다고 보고, 포트 점유 프로세스는 PID 확인 없이 건드리지 않는다.

## 변경 이력
- 2026-10-18: Redis 도입(로그아웃 시 토큰 즉시 무효화, 챗 응답 캐시). 1단계 계획에 Redis 연결과 로그아웃 반영
- 2026-10-18: 로깅 도입(`log/app.log` 롤링, 접근 로그, 업무 로그, SQL 로그). 로그 디렉토리는 사용자 요청으로 `log/`로 정했다
- 2026-10-18: `.env.example` 삭제(사용자 요청), README 환경변수 표로 대체
- 2026-10-18: 1단계 종료(태그 `step-1-login`)와 진행 현황 섹션 추가
- 2026-10-18: 블로그 포스팅 규칙 추가(사전 설계/단계별 제작 뉘앙스 제외)
- 2026-10-18: 이전 프로젝트(`asiana-ai-workflow`)에서 사용자가 요청해 온 작업 규칙(언어, Git 방식, Docker, 보안, 로깅, AI 단계)을 이 프로젝트 CLAUDE.md로 옮겨 기록
