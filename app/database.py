from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import load_settings
from app.logging_config import sql_log_params

settings = load_settings()

engine = create_engine(settings.database_url, hide_parameters=not sql_log_params())
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    pass
