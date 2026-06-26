# -*- coding: utf-8 -*-
"""Populate reference tables from JSON fixtures on first run."""
import json
import logging
from pathlib import Path

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import RefBioAgent, RefChemical, RefDanger

log = logging.getLogger(__name__)
FIXTURES = Path(__file__).parent / "fixtures"


def _load(filename: str) -> list[dict]:
    p = FIXTURES / filename
    if not p.exists():
        log.warning("Fixture not found: %s", p)
        return []
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def seed_chemicals(db: Session) -> int:
    if db.query(RefChemical).limit(1).count():
        return 0
    data = _load("chemicals.json")
    batch = 500
    inserted = 0
    for i in range(0, len(data), batch):
        db.bulk_insert_mappings(RefChemical, data[i : i + batch])
        db.commit()
        inserted += len(data[i : i + batch])
    log.info("Seeded %d chemicals", inserted)
    return inserted


def seed_bio_agents(db: Session) -> int:
    if db.query(RefBioAgent).limit(1).count():
        return 0
    data = _load("bio_agents.json")
    db.bulk_insert_mappings(RefBioAgent, data)
    db.commit()
    log.info("Seeded %d bio agents", len(data))
    return len(data)


def seed_dangers(db: Session) -> int:
    if db.query(RefDanger).limit(1).count():
        return 0
    data = _load("dangers.json")
    db.bulk_insert_mappings(RefDanger, data)
    db.commit()
    log.info("Seeded %d dangers", len(data))
    return len(data)


def run_all():
    db = SessionLocal()
    try:
        n_chem = seed_chemicals(db)
        n_bio  = seed_bio_agents(db)
        n_dan  = seed_dangers(db)
        if any([n_chem, n_bio, n_dan]):
            log.info(
                "Seed complete: chemicals=%d bio_agents=%d dangers=%d",
                n_chem, n_bio, n_dan,
            )
    finally:
        db.close()
