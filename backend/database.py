import os
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import Column, DateTime, Integer, JSON, String, Text, create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLITE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'crm_hcp.sqlite3')}"
DATABASE_URL = os.getenv("DATABASE_URL", SQLITE_URL)


def build_engine(url: str):
    kwargs = {}
    if url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    return create_engine(url, **kwargs)


def resolve_engine():
    primary = build_engine(DATABASE_URL)
    try:
        with primary.connect() as conn:
            conn.execute(text("SELECT 1"))
        return primary, DATABASE_URL
    except Exception:
        fallback = build_engine(SQLITE_URL)
        with fallback.connect() as conn:
            conn.execute(text("SELECT 1"))
        return fallback, SQLITE_URL


engine, ACTIVE_DATABASE_URL = resolve_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class HCP(Base):
    __tablename__ = "hcps"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    specialty = Column(String(255))
    hospital = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)


class Interaction(Base):
    __tablename__ = "interactions"
    id = Column(Integer, primary_key=True, index=True)
    interaction_uid = Column(String(64), unique=True, index=True)
    form_name = Column(String(255))
    hcp_name = Column(String(255))
    hcp_id = Column(Integer, nullable=True)
    interaction_type = Column(String(100), default="Meeting")
    date = Column(String(20))
    time = Column(String(10))
    attendees = Column(Text)
    topics_discussed = Column(Text)
    materials_shared = Column(Text)
    samples_distributed = Column(Text)
    sentiment = Column(String(20), default="Neutral")
    outcomes = Column(Text)
    follow_up_actions = Column(Text)
    follow_up_priority = Column(String(20))
    next_follow_up_date = Column(String(20))
    ai_suggested_followups = Column(JSON, default=list)
    raw_chat_log = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_sqlite_columns():
    with engine.begin() as conn:
        existing = {
            row[1]
            for row in conn.execute(text("PRAGMA table_info(interactions)")).fetchall()
        }
        wanted = {
            "interaction_uid": "TEXT",
            "form_name": "TEXT",
            "follow_up_priority": "TEXT",
            "next_follow_up_date": "TEXT",
        }
        for column, column_type in wanted.items():
            if column not in existing:
                conn.execute(text(f"ALTER TABLE interactions ADD COLUMN {column} {column_type}"))


def ensure_postgres_columns():
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE interactions ADD COLUMN IF NOT EXISTS interaction_uid VARCHAR(64)"))
        conn.execute(text("ALTER TABLE interactions ADD COLUMN IF NOT EXISTS form_name VARCHAR(255)"))
        conn.execute(text("ALTER TABLE interactions ADD COLUMN IF NOT EXISTS follow_up_priority VARCHAR(20)"))
        conn.execute(text("ALTER TABLE interactions ADD COLUMN IF NOT EXISTS next_follow_up_date VARCHAR(20)"))


def create_tables():
    Base.metadata.create_all(bind=engine)
    if ACTIVE_DATABASE_URL.startswith("sqlite"):
        ensure_sqlite_columns()
    else:
        ensure_postgres_columns()
