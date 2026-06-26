from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Organization, Summary, Workplace
from app.calculations.summary import classify_summary, kut_display

router = APIRouter(prefix="/rm", tags=["workplaces"])
templates = Jinja2Templates(directory="app/templates")


def _recalc_summary(rm: Workplace, db: Session):
    """Пересчитывает итоговый класс по всем факторам РМ."""
    s = rm.summary
    if s is None:
        s = Summary(rm_id=rm.id)
        db.add(s)
        rm.summary = s

    factor_kuts = [
        s.kut_chemical, s.kut_apfd, s.kut_noise,
        s.kut_vibr_local, s.kut_vibr_general,
        s.kut_infrasound, s.kut_ultrasound,
        s.kut_microclimate, s.kut_lighting,
        s.kut_emf, s.kut_radiation,
        s.kut_heaviness, s.kut_intensity,
    ]
    s.kut_final = classify_summary(factor_kuts)
    db.commit()


@router.get("/new/{org_id}", response_class=HTMLResponse)
def new_rm_form(org_id: int, request: Request, db: Session = Depends(get_db)):
    org = db.get(Organization, org_id)
    if not org:
        raise HTTPException(404)
    return templates.TemplateResponse("rm/form.html", {"request": request, "org": org, "rm": None})


@router.post("/new/{org_id}")
def create_rm(
    org_id: int,
    name: str = Form(...),
    podr: str = Form(""),
    profession: str = Form(""),
    num_workers: int = Form(1),
    shift_hours: float = Form(8.0),
    db: Session = Depends(get_db),
):
    org = db.get(Organization, org_id)
    if not org:
        raise HTTPException(404)
    rm = Workplace(
        org_id=org_id, name=name,
        podr=podr or None, profession=profession or None,
        num_workers=num_workers, shift_hours=shift_hours,
    )
    db.add(rm)
    db.commit()
    return RedirectResponse(f"/rm/{rm.id}", status_code=303)


@router.get("/{rm_id}", response_class=HTMLResponse)
def rm_detail(rm_id: int, request: Request, db: Session = Depends(get_db)):
    rm = db.get(Workplace, rm_id)
    if not rm:
        raise HTTPException(404)
    _recalc_summary(rm, db)
    return templates.TemplateResponse(
        "rm/detail.html",
        {"request": request, "rm": rm, "kut_display": kut_display},
    )


@router.get("/{rm_id}/edit", response_class=HTMLResponse)
def edit_rm_form(rm_id: int, request: Request, db: Session = Depends(get_db)):
    rm = db.get(Workplace, rm_id)
    if not rm:
        raise HTTPException(404)
    return templates.TemplateResponse("rm/form.html", {"request": request, "org": rm.org, "rm": rm})


@router.post("/{rm_id}/edit")
def update_rm(
    rm_id: int,
    name: str = Form(...),
    podr: str = Form(""),
    profession: str = Form(""),
    num_workers: int = Form(1),
    shift_hours: float = Form(8.0),
    db: Session = Depends(get_db),
):
    rm = db.get(Workplace, rm_id)
    if not rm:
        raise HTTPException(404)
    rm.name = name
    rm.podr = podr or None
    rm.profession = profession or None
    rm.num_workers = num_workers
    rm.shift_hours = shift_hours
    db.commit()
    return RedirectResponse(f"/rm/{rm_id}", status_code=303)


@router.post("/{rm_id}/delete")
def delete_rm(rm_id: int, db: Session = Depends(get_db)):
    rm = db.get(Workplace, rm_id)
    if not rm:
        raise HTTPException(404)
    org_id = rm.org_id
    db.delete(rm)
    db.commit()
    return RedirectResponse(f"/orgs/{org_id}", status_code=303)
