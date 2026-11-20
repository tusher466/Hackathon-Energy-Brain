from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import get_settings

settings = get_settings()
engine = create_engine(
    settings.database_url, connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    try:
        from app.services import ledger_service  # noqa
        from app.ml import models_meta  # noqa
        Base.metadata.create_all(bind=engine)
        print("DB tables created")
    except Exception as e:
        print(f"init_db failed: {e}, trying fallback in-memory")
        # Fallback: try at least create without errors
        try:
            Base.metadata.create_all(bind=engine, checkfirst=True)
        except Exception as ee:
            print(f"Fallback DB also failed non-fatal: {ee}")
