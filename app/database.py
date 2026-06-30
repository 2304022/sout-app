import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sout.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from app import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    _migrate_add_columns()


def _migrate_add_columns():
    """Добавляет новые колонки в существующие таблицы (идемпотентно)."""
    from sqlalchemy import text
    migrations = {
        "meas_heaviness": [
            ("moves_vertical_km", "REAL"),
            ("static_local",      "REAL"),
            ("static_regional",   "REAL"),
            ("static_one_hand",   "REAL"),
            ("static_two_hands",  "REAL"),
            ("static_body_legs",  "REAL"),
        ],
        "meas_intensity": [
            ("perception_load",      "INTEGER DEFAULT 1"),
            ("work_distribution",    "INTEGER DEFAULT 1"),
            ("work_nature",          "INTEGER DEFAULT 1"),
            ("concentration_pct",    "REAL"),
            ("voice_hours_week",     "REAL"),
            ("life_risk",            "INTEGER DEFAULT 0"),
            ("others_safety",        "INTEGER DEFAULT 0"),
            ("conflicts_per_shift",  "INTEGER"),
            ("operation_duration_sec", "INTEGER"),
            ("active_actions_pct",   "REAL"),
            ("shift_duration_hours", "REAL"),
            ("shift_type",           "INTEGER DEFAULT 1"),
            ("break_adequacy",       "INTEGER DEFAULT 1"),
        ],
        "summary": [
            ("kut_bio",     "INTEGER"),
            ("kut_laser",   "INTEGER"),
            ("kut_uv",      "INTEGER"),
            ("kut_aeroion", "INTEGER"),
        ],
    }
    with engine.connect() as conn:
        for table, cols in migrations.items():
            result = conn.execute(text(f"PRAGMA table_info({table})"))
            existing = {row[1] for row in result}
            for col_name, col_type in cols:
                if col_name not in existing:
                    conn.execute(text(
                        f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}"
                    ))
        conn.commit()
