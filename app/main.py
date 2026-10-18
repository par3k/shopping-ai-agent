from dotenv import load_dotenv

load_dotenv()

from contextlib import asynccontextmanager  # noqa: E402

from fastapi import FastAPI  # noqa: E402

import app.models  # noqa: E402,F401  Base.metadata에 모델을 등록한다
from app.database import Base, engine  # noqa: E402
from app.routers import member  # noqa: E402


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Shopping AI Agent", lifespan=lifespan)
app.include_router(member.router)


@app.get("/health")
def health():
    return {"status": "ok"}
