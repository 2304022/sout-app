import logging
import os

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database import get_db, init_db
from app.routers import factors, orgs, workplaces

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="СОУТ — оценка условий труда")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(orgs.router)
app.include_router(workplaces.router)
app.include_router(factors.router)


def _demo_enabled() -> bool:
    return os.getenv("SEED_DEMO_DATA", "").strip().lower() in ("1", "true", "yes", "on")


@app.on_event("startup")
def on_startup():
    init_db()
    from app.seed import run_all
    run_all()
    # Опциональная загрузка демо-данных (организация + РМ + замеры)
    if _demo_enabled():
        from app.database import SessionLocal
        from app.demo import load_demo
        db = SessionLocal()
        try:
            if load_demo(db):
                logging.info("SEED_DEMO_DATA=true → демо-данные загружены")
            else:
                logging.info("SEED_DEMO_DATA=true → демо-данные уже присутствуют")
        finally:
            db.close()


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return RedirectResponse("/orgs/")


# ── Справочные API ────────────────────────────────────────────────────────

@app.get("/api/chemicals")
def api_chemicals(q: str = "", limit: int = 30):
    """Поиск веществ по названию для автодополнения."""
    from app.models import RefChemical
    db = next(get_db())
    try:
        query = db.query(RefChemical)
        if q:
            query = query.filter(RefChemical.name.ilike(f"%{q}%"))
        items = query.order_by(RefChemical.name).limit(limit).all()
        return JSONResponse([{
            "id":            c.id,
            "name":          c.name,
            "cas":           c.cas,
            "pdk_ss":        c.pdk_ss,
            "pdk_max":       c.pdk_max,
            "danger_class":  c.danger_class,
            "is_carcinogen": c.is_carcinogen,
            "is_allergen":   c.is_allergen,
            "is_irritant":   c.is_irritant,
            "is_directed":   c.is_directed,
        } for c in items])
    finally:
        db.close()


@app.get("/api/bio_agents")
def api_bio_agents(q: str = "", limit: int = 30):
    """Поиск биологических агентов."""
    from app.models import RefBioAgent
    db = next(get_db())
    try:
        query = db.query(RefBioAgent)
        if q:
            query = query.filter(RefBioAgent.name.ilike(f"%{q}%"))
        items = query.order_by(RefBioAgent.name).limit(limit).all()
        return JSONResponse([{
            "id":                  a.id,
            "name":                a.name,
            "pathogenicity_group": a.pathogenicity_group,
        } for a in items])
    finally:
        db.close()


@app.get("/api/bio_producers")
def api_bio_producers(q: str = "", limit: int = 30):
    """Поиск микроорганизмов-продуцентов по ГН 2.2.6.3686-21."""
    from app.models import RefBioProducer
    db = next(get_db())
    try:
        query = db.query(RefBioProducer)
        if q:
            query = query.filter(RefBioProducer.name.ilike(f"%{q}%"))
        items = query.order_by(RefBioProducer.name).limit(limit).all()
        return JSONResponse([{
            "id":           p.id,
            "name":         p.name,
            "purpose":      p.purpose,
            "pdk_ss":       p.pdk_ss,
            "pdk_max":      None,
            "danger_class": p.danger_class,
            "is_carcinogen": False,
            "is_allergen":  p.is_allergen,
            "is_irritant":  p.is_irritant,
            "is_directed":  p.is_directed,
            "is_fibrogenic": False,
            "doc":          p.doc,
            "source":       "bio_producer",
        } for p in items])
    finally:
        db.close()


@app.get("/api/eff_sum")
def api_eff_sum(chem_id: int):
    """Вернуть все группы суммирования, в которые входит данное вещество."""
    import json as _json
    from app.models import RefEffSum
    db = next(get_db())
    try:
        groups = db.query(RefEffSum).all()
        result = []
        for g in groups:
            ids = _json.loads(g.chem_ids or "[]")
            if chem_id in ids:
                result.append({
                    "id":       g.id,
                    "src":      g.src,
                    "punkt":    g.punkt,
                    "chem_ids": ids,
                })
        return JSONResponse(result)
    finally:
        db.close()


@app.get("/ref/chemicals", response_class=HTMLResponse)
def ref_chemicals_page(request: Request, q: str = ""):
    """Страница справочника химических веществ."""
    from app.models import RefChemical
    db = next(get_db())
    try:
        query = db.query(RefChemical)
        if q:
            query = query.filter(RefChemical.name.ilike(f"%{q}%"))
        total = query.count()
        items = query.order_by(RefChemical.name).limit(200).all()
        return templates.TemplateResponse(
            "ref/chemicals.html",
            {"request": request, "items": items, "q": q, "total": total},
        )
    finally:
        db.close()


@app.get("/ref/bio_producers", response_class=HTMLResponse)
def ref_bio_producers_page(request: Request, q: str = ""):
    """Справочник микроорганизмов-продуцентов (ГН 2.2.6.3686-21)."""
    from app.models import RefBioProducer
    db = next(get_db())
    try:
        query = db.query(RefBioProducer)
        if q:
            query = query.filter(RefBioProducer.name.ilike(f"%{q}%"))
        total = query.count()
        items = query.order_by(RefBioProducer.name).limit(200).all()
        return templates.TemplateResponse(
            "ref/bio_producers.html",
            {"request": request, "items": items, "q": q, "total": total},
        )
    finally:
        db.close()


@app.get("/ref/eff_sum", response_class=HTMLResponse)
def ref_eff_sum_page(request: Request):
    """Справочник групп суммирования веществ (СанПиН 1.2.3685-21)."""
    import json as _json
    from app.models import RefChemical, RefEffSum
    db = next(get_db())
    try:
        groups = db.query(RefEffSum).order_by(RefEffSum.id).all()
        # Resolve chemical names for display
        all_ids = set()
        for g in groups:
            all_ids.update(_json.loads(g.chem_ids or "[]"))
        chem_map = {}
        if all_ids:
            chems = db.query(RefChemical.id, RefChemical.name).filter(
                RefChemical.id.in_(list(all_ids))
            ).all()
            chem_map = {c.id: c.name for c in chems}
        rows = []
        for g in groups:
            ids = _json.loads(g.chem_ids or "[]")
            rows.append({
                "id": g.id, "src": g.src, "punkt": g.punkt,
                "names": [chem_map.get(i, f"id={i}") for i in ids],
            })
        return templates.TemplateResponse(
            "ref/eff_sum.html",
            {"request": request, "rows": rows},
        )
    finally:
        db.close()
