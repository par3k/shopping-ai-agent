import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
SQL_MAX_LENGTH = 1500
FILE_MAX_BYTES = 10 * 1024 * 1024
FILE_BACKUP_COUNT = 5
DEFAULT_LOG_DIR = Path(__file__).resolve().parent.parent / "log"

_configured = False


class AppFormatter(logging.Formatter):
    """SQL 로그는 한 건이 길면 잘라서 기록한다."""

    def __init__(self):
        super().__init__(LOG_FORMAT)

    def format(self, record: logging.LogRecord) -> str:
        text = super().format(record)
        if record.name.startswith("sqlalchemy.engine") and len(text) > SQL_MAX_LENGTH:
            return text[:SQL_MAX_LENGTH] + "...(생략)"
        return text


class StreamToLogger:
    """print() 출력을 원래 stdout과 로거에 함께 보낸다."""

    def __init__(self, stream, logger: logging.Logger):
        self.stream = stream
        self.logger = logger

    def write(self, text: str) -> int:
        self.stream.write(text)
        if text.strip():
            self.logger.info(text.rstrip())
        return len(text)

    def flush(self) -> None:
        self.stream.flush()

    def __getattr__(self, name):
        return getattr(self.stream, name)


def _env_flag(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None or value == "":
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


def sql_log_params() -> bool:
    return _env_flag("SQL_LOG_PARAMS", False)


def setup_logging() -> None:
    global _configured
    if _configured:
        return
    _configured = True

    log_dir = Path(os.environ.get("LOG_DIR") or DEFAULT_LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=FILE_MAX_BYTES,
        backupCount=FILE_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(AppFormatter())

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(file_handler)

    # uvicorn 로거는 propagate=False라 root 핸들러가 닿지 않는다.
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logging.getLogger(name).addHandler(file_handler)

    # 실행되는 SQL은 파일에만 기록한다. (콘솔 출력 없음)
    if _env_flag("SQL_LOG", True):
        sql_logger = logging.getLogger("sqlalchemy.engine")
        sql_logger.setLevel(logging.INFO)
        sql_logger.propagate = False
        sql_logger.addHandler(file_handler)

    if sys.stdout is sys.__stdout__:
        sys.stdout = StreamToLogger(sys.stdout, logging.getLogger("stdout"))
