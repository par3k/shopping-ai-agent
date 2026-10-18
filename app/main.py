from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI  # noqa: E402

app = FastAPI(title="Shopping AI Agent")


@app.get("/health")
def health():
    return {"status": "ok"}
