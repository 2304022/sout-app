from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Organization

router = APIRouter(prefix="/orgs", tags=["organizations"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def list_orgs(request: Request, db: Session = Depends(get_db)):
    orgs = db.query(Organization).order_by(Organization.name).all()
    return templates.TemplateResponse("orgs/list.html", {"request": request, "orgs": orgs})


@router.get("/new", response_class=HTMLResponse)
def new_org_form(request: Request):
    return templates.TemplateResponse("orgs/form.html", {"request": request, "org": None})


@router.post("/new")
def create_org(
    name: str = Form(...),
    inn: str = Form(""),
    address: str = Form(""),
    db: Session = Depends(get_db),
):
    org = Organization(name=name, inn=inn or None, address=address or None)
    db.add(org)
    db.commit()
    return RedirectResponse(f"/orgs/{org.id}", status_code=303)


@router.get("/{org_id}", response_class=HTMLResponse)
def org_detail(org_id: int, request: Request, db: Session = Depends(get_db)):
    org = db.get(Organization, org_id)
    if not org:
        raise HTTPException(404)
    return templates.TemplateResponse("orgs/detail.html", {"request": request, "org": org})


@router.get("/{org_id}/edit", response_class=HTMLResponse)
def edit_org_form(org_id: int, request: Request, db: Session = Depends(get_db)):
    org = db.get(Organization, org_id)
    if not org:
        raise HTTPException(404)
    return templates.TemplateResponse("orgs/form.html", {"request": request, "org": org})


@router.post("/{org_id}/edit")
def update_org(
    org_id: int,
    name: str = Form(...),
    inn: str = Form(""),
    address: str = Form(""),
    db: Session = Depends(get_db),
):
    org = db.get(Organization, org_id)
    if not org:
        raise HTTPException(404)
    org.name = name
    org.inn = inn or None
    org.address = address or None
    db.commit()
    return RedirectResponse(f"/orgs/{org_id}", status_code=303)


@router.post("/{org_id}/delete")
def delete_org(org_id: int, db: Session = Depends(get_db)):
    org = db.get(Organization, org_id)
    if not org:
        raise HTTPException(404)
    db.delete(org)
    db.commit()
    return RedirectResponse("/orgs/", status_code=303)
