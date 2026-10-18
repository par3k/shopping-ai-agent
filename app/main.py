from dotenv import load_dotenv

load_dotenv()

from app.logging_config import setup_logging  # noqa: E402

setup_logging()  # 엔진 생성 전에 설정해야 SQL 로그가 켜진다

from contextlib import asynccontextmanager  # noqa: E402

from fastapi import FastAPI  # noqa: E402

import app.models  # noqa: E402,F401  Base.metadata에 모델을 등록한다
from app.database import Base, engine  # noqa: E402
from app.middleware import add_access_log  # noqa: E402
from app.routers import member  # noqa: E402


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Shopping AI Agent", lifespan=lifespan)
add_access_log(app)
app.include_router(member.router)


@app.get("/health")
def health():
    return {"status": "ok"}
