import logging

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


@app.on_event("startup")
def on_startup():
    init_db()
    from app.seed import run_all
    run_all()


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
