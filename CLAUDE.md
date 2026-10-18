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
- 웹/DB: FastAPI, SQLAlchemy, PostgreSQL(pgvector), JWT(python-jose, bcrypt), Pydantic
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
- 사용자가 따로 요청하지 않으면 Docker(컨테이너, 이미지)를 조작하지 않는다. (`docker run/exec/stop/rm` 모두 포함)
- 컨테이너 안에서 해야 하는 작업은 명령어만 안내한다.
- 서버를 종료할 때는 이 프로젝트에서 직접 띄운 프로세스만 대상으로 한다. 포트(8000) 점유 프로세스를 PID 확인 없이 종료하지 않는다(이전 프로젝트에서 사용자가 직접 띄운 서버를 끈 적이 있다). 서버 테스트는 사용자 서버와 겹치지 않게 다른 포트(예: 8001)로 띄우고, 자기가 띄운 PID만 종료한다.

### 보안
- `.env`의 값(API 키, DB 비밀번호)을 출력하거나 문서에 적지 않는다. 키 이름만 언급한다.
- `.env`는 `.gitignore`에 포함되어 있다. 커밋하지 않는다.
- 키 재발급 여부는 사용자가 판단한다.

### 로깅 (이전 프로젝트에서 요청한 방식, 해당 단계에서 동일하게 적용)
- 로그 파일은 롤링한다: `logs/app.log`(10MB x 5개 보관), `print()`·uvicorn·root 로거를 함께 기록. 위치는 `LOG_DIR`로 변경 가능. `logs/`는 `.gitignore` 대상이다.
- 모든 API 요청을 `api.access` 로그로 기록한다(요청ID, method, path+query, member_id, client, 상태코드, 소요시간). 비밀번호 등이 있을 수 있어 요청 body와 토큰 값은 기록하지 않는다. 응답 헤더에 `X-Request-ID`를 붙인다.
- 라우터별 업무 로그(`api.member/order/product/document/chat`)를 남긴다: 가입·로그인 성공/실패, 주문 생성/취소, 상품 등록/수정/조회, 문서 추가/수정, 챗 질문(100자)·분류·응답길이.
- 실행되는 SQL(`sqlalchemy.engine`)은 파일에만 기록한다. 바인딩 파라미터는 `hide_parameters`로 숨기고(`SQL_LOG_PARAMS=true`면 표시), 한 건이 1500자를 넘으면 잘라서 기록한다. `SQL_LOG=false`로 끌 수 있다.
- LLM 직접 호출은 요청·응답·토큰·소요시간·오류를 `api.llm` 로그로 기록한다(질문/응답은 200자까지).
- 로그 파일은 UTF-8로 읽는다(그냥 열면 한글이 깨져 보일 수 있다).

### AI 단계 (후속 단계에서 요청한 내용)
- 이전 프로젝트의 챗 파이프라인 순서: 캐시 → 1차 분류 → get_api(QUERY/ACTION/GENERAL)/profile/policy/general → 캐시 저장. ACTION은 실행 전 `interrupt()`로 사용자 확인("예/아니오", HITL)을 받는다.
- LLM은 OpenAI(gpt-4.1-mini)를 쓴다. Anthropic Claude로 전환했다가 사용자 판단으로 OpenAI로 원복한 이력이 있으니 임의로 바꾸지 않는다.
- LangSmith/Langfuse로 관측하며 키는 `.env`에만 둔다.

## 개발 환경
- Python 3.13 가상환경: `.venv` (3.14는 일부 패키지 wheel이 없어 사용하지 않음)
- 실행: `uvicorn app.main:app --reload` (기본 포트 8000, 문서 `/docs`)
- DB: 사용자가 Docker로 직접 띄운 PostgreSQL(pgvector) 컨테이너. 이전 프로젝트는 호스트 포트 5433을 썼다. 포트와 DB 이름은 `.env`의 `DATABASE_URL`을 따른다.
- 마이그레이션 도구는 쓰지 않고 앱 시작 시 `Base.metadata.create_all`로 테이블을 만든다.

## 변경 이력
- 2026-10-18: 이전 프로젝트(`asiana-ai-workflow`)에서 사용자가 요청해 온 작업 규칙(언어, Git 방식, Docker, 보안, 로깅, AI 단계)을 이 프로젝트 CLAUDE.md로 옮겨 기록
