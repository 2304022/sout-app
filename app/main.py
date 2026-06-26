from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database import init_db
from app.calculations.summary import kut_display
from app.routers import orgs, workplaces, factors

app = FastAPI(title="СОУТ — оценка условий труда")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(orgs.router)
app.include_router(workplaces.router)
app.include_router(factors.router)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return RedirectResponse("/orgs/")
