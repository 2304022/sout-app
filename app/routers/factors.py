"""
CRUD и расчёт по каждому фактору СОУТ.
Каждый endpoint принимает данные формы, сохраняет в БД и пересчитывает kut.
"""
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    MeasAeroion, MeasAPFD, MeasBio, MeasChemical, MeasEMF, MeasHeaviness,
    MeasInfrasound, MeasIntensity, MeasLaser, MeasLighting,
    MeasMicroclimate, MeasNoise, MeasRadiation, MeasUV,
    MeasUltrasound, MeasVibrGeneral, MeasVibrLocal,
    Summary, Workplace,
)
from app.calculations import (
    aeroion as calc_aeroion,
    apfd as calc_apfd,
    bio as calc_bio,
    chemical as calc_chem,
    emf as calc_emf,
    heaviness as calc_heavy,
    intensity as calc_intens,
    laser as calc_laser,
    lighting as calc_light,
    microclimate as calc_micro,
    noise_vibration as calc_nv,
    radiation as calc_rad,
)
from app.calculations.summary import classify_summary
from app.calculations.utils import kut_max

router = APIRouter(prefix="/factor", tags=["factors"])
templates = Jinja2Templates(directory="app/templates")

FACTOR_ATTR = {
    "chemical":     "kut_chemical",
    "apfd":         "kut_apfd",
    "noise":        "kut_noise",
    "vibr_local":   "kut_vibr_local",
    "vibr_general": "kut_vibr_general",
    "infrasound":   "kut_infrasound",
    "ultrasound":   "kut_ultrasound",
    "microclimate": "kut_microclimate",
    "lighting":     "kut_lighting",
    "emf":          "kut_emf",
    "radiation":    "kut_radiation",
    "heaviness":    "kut_heaviness",
    "intensity":    "kut_intensity",
    "bio":          "kut_bio",
    "laser":        "kut_laser",
    "uv":           "kut_uv",
    "aeroion":      "kut_aeroion",
}


def _ensure_summary(rm: Workplace, db: Session) -> Summary:
    if rm.summary is None:
        s = Summary(rm_id=rm.id)
        db.add(s)
        db.flush()
    return rm.summary


def _update_summary_kut(rm: Workplace, factor: str, kut: int, db: Session):
    s = _ensure_summary(rm, db)
    setattr(s, FACTOR_ATTR[factor], kut)
    factor_kuts = [getattr(s, a) for a in FACTOR_ATTR.values()]
    s.kut_final = classify_summary(factor_kuts)
    db.commit()


# ── ХИМИЧЕСКИЙ ────────────────────────────────────────────────────────────────

@router.get("/chemical/{rm_id}", response_class=HTMLResponse)
def chemical_form(rm_id: int, request: Request, db: Session = Depends(get_db)):
    rm = db.get(Workplace, rm_id)
    if not rm: raise HTTPException(404)
    return templates.TemplateResponse(
        "factors/chemical.html", {"request": request, "rm": rm, "items": rm.chemicals}
    )


@router.post("/chemical/{rm_id}/add")
def add_chemical(
    rm_id: int,
    substance_name: str = Form(...),
    danger_class: int = Form(3),
    pdk_ss: float = Form(None),
    pdk_max: float = Form(None),
    c_ss: float = Form(None),
    c_max: float = Form(None),
    is_carcinogen: bool = Form(False),
    is_allergen_high: bool = Form(False),
    is_allergen_mod: bool = Form(False),
    is_irritant: bool = Form(False),
    is_directed: bool = Form(False),
    is_repro: bool = Form(False),
    is_antitumor: bool = Form(False),
    db: Session = Depends(get_db),
):
    rm = db.get(Workplace, rm_id)
    if not rm: raise HTTPException(404)
    kut = calc_chem.classify_chemical(
        danger_class=danger_class,
        is_carcinogen=is_carcinogen,
        is_allergen_high=is_allergen_high,
        is_allergen_mod=is_allergen_mod,
        is_irritant=is_irritant,
        is_directed=is_directed,
        is_repro=is_repro,
        is_antitumor=is_antitumor,
        c_ss=c_ss, c_max=c_max,
        pdk_ss=pdk_ss, pdk_max=pdk_max,
    )
    m = MeasChemical(
        rm_id=rm_id, substance_name=substance_name,
        danger_class=danger_class,
        pdk_ss=pdk_ss, pdk_max=pdk_max,
        c_ss=c_ss, c_max=c_max,
        is_carcinogen=is_carcinogen,
        is_allergen_high=is_allergen_high,
        is_allergen_mod=is_allergen_mod,
        is_irritant=is_irritant,
        is_directed=is_directed,
        is_repro=is_repro,
        is_antitumor=is_antitumor,
        kut=kut,
    )
    db.add(m)
    # Итоговый класс по химии = max среди всех веществ на РМ
    db.flush()
    all_kuts = [x.kut for x in rm.chemicals if x.kut is not None]
    _update_summary_kut(rm, "chemical", (kut_max(all_kuts) or 2), db)
    return RedirectResponse(f"/factor/chemical/{rm_id}", status_code=303)


@router.post("/chemical/{rm_id}/delete/{item_id}")
def delete_chemical(rm_id: int, item_id: int, db: Session = Depends(get_db)):
    m = db.get(MeasChemical, item_id)
    if m: db.delete(m)
    db.flush()
    rm = db.get(Workplace, rm_id)
    all_kuts = [x.kut for x in rm.chemicals if x.kut is not None]
    _update_summary_kut(rm, "chemical", (kut_max(all_kuts) or 2), db)
    return RedirectResponse(f"/factor/chemical/{rm_id}", status_code=303)


# ── АПФД ──────────────────────────────────────────────────────────────────────

@router.get("/apfd/{rm_id}", response_class=HTMLResponse)
def apfd_form(rm_id: int, request: Request, db: Session = Depends(get_db)):
    rm = db.get(Workplace, rm_id)
    if not rm: raise HTTPException(404)
    return templates.TemplateResponse("factors/apfd.html", {"request": request, "rm": rm, "items": rm.apfds})


@router.post("/apfd/{rm_id}/add")
def add_apfd(
    rm_id: int,
    substance_name: str = Form(...),
    pdk_ss: float = Form(...),
    fibrogenicity: str = Form("high"),
    c_fact: float = Form(...),
    work_years: float = Form(25.0),
    shifts_per_year: int = Form(247),
    db: Session = Depends(get_db),
):
    rm = db.get(Workplace, rm_id)
    if not rm: raise HTTPException(404)
    kut, pn, kpn = calc_apfd.classify_apfd(pdk_ss, fibrogenicity, c_fact, shifts_per_year, work_years)
    m = MeasAPFD(
        rm_id=rm_id, substance_name=substance_name,
        pdk_ss=pdk_ss, fibrogenicity=fibrogenicity,
        c_fact=c_fact, work_years=work_years,
        shifts_per_year=shifts_per_year,
        pn_fact=pn, kpn=kpn, kut=kut,
    )
    db.add(m)
    db.flush()
    all_kuts = [x.kut for x in rm.apfds if x.kut is not None]
    _update_summary_kut(rm, "apfd", (kut_max(all_kuts) or 2), db)
    return RedirectResponse(f"/factor/apfd/{rm_id}", status_code=303)


@router.post("/apfd/{rm_id}/delete/{item_id}")
def delete_apfd(rm_id: int, item_id: int, db: Session = Depends(get_db)):
    m = db.get(MeasAPFD, item_id)
    if m: db.delete(m)
    db.flush()
    rm = db.get(Workplace, rm_id)
    all_kuts = [x.kut for x in rm.apfds if x.kut is not None]
    _update_summary_kut(rm, "apfd", (kut_max(all_kuts) or 2), db)
    return RedirectResponse(f"/factor/apfd/{rm_id}", status_code=303)


# ── ШУМ ───────────────────────────────────────────────────────────────────────

@router.get("/noise/{rm_id}", response_class=HTMLResponse)
def noise_form(rm_id: int, request: Request, db: Session = Depends(get_db)):
    rm = db.get(Workplace, rm_id)
    if not rm: raise HTTPException(404)
    return templates.TemplateResponse("factors/noise.html", {"request": request, "rm": rm, "items": rm.noises})


@router.post("/noise/{rm_id}/add")
def add_noise(
    rm_id: int,
    leq_dba: float = Form(...),
    lpeak_dbc: float = Form(None),
    db: Session = Depends(get_db),
):
    rm = db.get(Workplace, rm_id)
    if not rm: raise HTTPException(404)
    kut = calc_nv.classify_noise(leq_dba)
    m = MeasNoise(rm_id=rm_id, leq_dba=leq_dba, lpeak_dbc=lpeak_dbc, kut=kut)
    db.add(m)
    db.flush()
    all_kuts = [x.kut for x in rm.noises if x.kut is not None]
    _update_summary_kut(rm, "noise", (kut_max(all_kuts) or 2), db)
    return RedirectResponse(f"/factor/noise/{rm_id}", status_code=303)


@router.post("/noise/{rm_id}/delete/{item_id}")
def delete_noise(rm_id: int, item_id: int, db: Session = Depends(get_db)):
    m = db.get(MeasNoise, item_id)
    if m: db.delete(m)
    db.flush()
    rm = db.get(Workplace, rm_id)
    all_kuts = [x.kut for x in rm.noises if x.kut is not None]
    _update_summary_kut(rm, "noise", (kut_max(all_kuts) or 2), db)
    return RedirectResponse(f"/factor/noise/{rm_id}", status_code=303)


# ── ВИБРАЦИЯ ЛОКАЛЬНАЯ ────────────────────────────────────────────────────────

@router.get("/vibr_local/{rm_id}", response_class=HTMLResponse)
def vibr_local_form(rm_id: int, request: Request, db: Session = Depends(get_db)):
    rm = db.get(Workplace, rm_id)
    if not rm: raise HTTPException(404)
    return templates.TemplateResponse("factors/vibr_local.html", {"request": request, "rm": rm, "items": rm.vibr_locals})


@router.post("/vibr_local/{rm_id}/add")
def add_vibr_local(
    rm_id: int,
    corr_level_db: float = Form(...),
    db: Session = Depends(get_db),
):
    rm = db.get(Workplace, rm_id)
    if not rm: raise HTTPException(404)
    kut = calc_nv.classify_vibr_local(corr_level_db)
    m = MeasVibrLocal(rm_id=rm_id, corr_level_db=corr_level_db, kut=kut)
    db.add(m)
    db.flush()
    all_kuts = [x.kut for x in rm.vibr_locals if x.kut is not None]
    _update_summary_kut(rm, "vibr_local", (kut_max(all_kuts) or 2), db)
    return RedirectResponse(f"/factor/vibr_local/{rm_id}", status_code=303)


@router.post("/vibr_local/{rm_id}/delete/{item_id}")
def delete_vibr_local(rm_id: int, item_id: int, db: Session = Depends(get_db)):
    m = db.get(MeasVibrLocal, item_id)
    if m: db.delete(m)
    db.flush()
    rm = db.get(Workplace, rm_id)
    all_kuts = [x.kut for x in rm.vibr_locals if x.kut is not None]
    _update_summary_kut(rm, "vibr_local", (kut_max(all_kuts) or 2), db)
    return RedirectResponse(f"/factor/vibr_local/{rm_id}", status_code=303)


# ── ВИБРАЦИЯ ОБЩАЯ ────────────────────────────────────────────────────────────

@router.get("/vibr_general/{rm_id}", response_class=HTMLResponse)
def vibr_general_form(rm_id: int, request: Request, db: Session = Depends(get_db)):
    rm = db.get(Workplace, rm_id)
    if not rm: raise HTTPException(404)
    return templates.TemplateResponse("factors/vibr_general.html", {"request": request, "rm": rm, "items": rm.vibr_generals})


@router.post("/vibr_general/{rm_id}/add")
def add_vibr_general(
    rm_id: int,
    axis: str = Form("Z"),
    corr_level_db: float = Form(...),
    db: Session = Depends(get_db),
):
    rm = db.get(Workplace, rm_id)
    if not rm: raise HTTPException(404)
    kut = calc_nv.classify_vibr_general(corr_level_db, axis)
    m = MeasVibrGeneral(rm_id=rm_id, axis=axis, corr_level_db=corr_level_db, kut=kut)
    db.add(m)
    db.flush()
    all_kuts = [x.kut for x in rm.vibr_generals if x.kut is not None]
    _update_summary_kut(rm, "vibr_general", (kut_max(all_kuts) or 2), db)
    return RedirectResponse(f"/factor/vibr_general/{rm_id}", status_code=303)


@router.post("/vibr_general/{rm_id}/delete/{item_id}")
def delete_vibr_general(rm_id: int, item_id: int, db: Session = Depends(get_db)):
    m = db.get(MeasVibrGeneral, item_id)
    if m: db.delete(m)
    db.flush()
    rm = db.get(Workplace, rm_id)
    all_kuts = [x.kut for x in rm.vibr_generals if x.kut is not None]
    _update_summary_kut(rm, "vibr_general", (kut_max(all_kuts) or 2), db)
    return RedirectResponse(f"/factor/vibr_general/{rm_id}", status_code=303)


# ── ИНФРАЗВУК ─────────────────────────────────────────────────────────────────

@router.get("/infrasound/{rm_id}", response_class=HTMLResponse)
def infrasound_form(rm_id: int, request: Request, db: Session = Depends(get_db)):
    rm = db.get(Workplace, rm_id)
    if not rm: raise HTTPException(404)
    return templates.TemplateResponse("factors/infrasound.html", {"request": request, "rm": rm, "items": rm.infrasounds})


@router.post("/infrasound/{rm_id}/add")
def add_infrasound(rm_id: int, level_db_lin: float = Form(...), db: Session = Depends(get_db)):
    rm = db.get(Workplace, rm_id)
    if not rm: raise HTTPException(404)
    kut = calc_nv.classify_infrasound(level_db_lin)
    m = MeasInfrasound(rm_id=rm_id, level_db_lin=level_db_lin, kut=kut)
    db.add(m)
    db.flush()
    all_kuts = [x.kut for x in rm.infrasounds if x.kut is not None]
    _update_summary_kut(rm, "infrasound", (kut_max(all_kuts) or 2), db)
    return RedirectResponse(f"/factor/infrasound/{rm_id}", status_code=303)


@router.post("/infrasound/{rm_id}/delete/{item_id}")
def delete_infrasound(rm_id: int, item_id: int, db: Session = Depends(get_db)):
    m = db.get(MeasInfrasound, item_id)
    if m: db.delete(m)
    db.flush()
    rm = db.get(Workplace, rm_id)
    all_kuts = [x.kut for x in rm.infrasounds if x.kut is not None]
    _update_summary_kut(rm, "infrasound", (kut_max(all_kuts) or 2), db)
    return RedirectResponse(f"/factor/infrasound/{rm_id}", status_code=303)


# ── УЛЬТРАЗВУК ────────────────────────────────────────────────────────────────

@router.get("/ultrasound/{rm_id}", response_class=HTMLResponse)
def ultrasound_form(rm_id: int, request: Request, db: Session = Depends(get_db)):
    rm = db.get(Workplace, rm_id)
    if not rm: raise HTTPException(404)
    return templates.TemplateResponse("factors/ultrasound.html", {"request": request, "rm": rm, "items": rm.ultrasounds})


@router.post("/ultrasound/{rm_id}/add")
def add_ultrasound(rm_id: int, excess_db: float = Form(...), db: Session = Depends(get_db)):
    rm = db.get(Workplace, rm_id)
    if not rm: raise HTTPException(404)
    kut = calc_nv.classify_ultrasound(excess_db)
    m = MeasUltrasound(rm_id=rm_id, excess_db=excess_db, kut=kut)
    db.add(m)
    db.flush()
    all_kuts = [x.kut for x in rm.ultrasounds if x.kut is not None]
    _update_summary_kut(rm, "ultrasound", (kut_max(all_kuts) or 2), db)
    return RedirectResponse(f"/factor/ultrasound/{rm_id}", status_code=303)


@router.post("/ultrasound/{rm_id}/delete/{item_id}")
def delete_ultrasound(rm_id: int, item_id: int, db: Session = Depends(get_db)):
    m = db.get(MeasUltrasound, item_id)
    if m: db.delete(m)
    db.flush()
    rm = db.get(Workplace, rm_id)
    all_kuts = [x.kut for x in rm.ultrasounds if x.kut is not None]
    _update_summary_kut(rm, "ultrasound", (kut_max(all_kuts) or 2), db)
    return RedirectResponse(f"/factor/ultrasound/{rm_id}", status_code=303)


# ── МИКРОКЛИМАТ ───────────────────────────────────────────────────────────────

@router.get("/microclimate/{rm_id}", response_class=HTMLResponse)
def microclimate_form(rm_id: int, request: Request, db: Session = Depends(get_db)):
    rm = db.get(Workplace, rm_id)
    if not rm: raise HTTPException(404)
    return templates.TemplateResponse("factors/microclimate.html", {"request": request, "rm": rm, "items": rm.microclimates})


@router.post("/microclimate/{rm_id}/add")
def add_microclimate(
    rm_id: int,
    season: str = Form("warm"),
    mode: str = Form("heating"),
    work_category: str = Form("IIa"),
    tns_index: float = Form(None),
    air_temp: float = Form(None),
    air_speed: float = Form(None),
    humidity: float = Form(None),
    radiant_heat: float = Form(None),
    db: Session = Depends(get_db),
):
    rm = db.get(Workplace, rm_id)
    if not rm: raise HTTPException(404)
    if mode == "heating" and tns_index is not None:
        kut = calc_micro.classify_microclimate_heating(work_category, tns_index)
    elif mode == "cooling" and air_temp is not None:
        kut = calc_micro.classify_microclimate_cooling(work_category, air_temp, air_speed, humidity, radiant_heat)
    else:
        kut = 2
    m = MeasMicroclimate(
        rm_id=rm_id, season=season, mode=mode,
        work_category=work_category,
        tns_index=tns_index, air_temp=air_temp,
        air_speed=air_speed, humidity=humidity,
        radiant_heat=radiant_heat, kut=kut,
    )
    db.add(m)
    db.flush()
    all_kuts = [x.kut for x in rm.microclimates if x.kut is not None]
    _update_summary_kut(rm, "microclimate", (kut_max(all_kuts) or 2), db)
    return RedirectResponse(f"/factor/microclimate/{rm_id}", status_code=303)


@router.post("/microclimate/{rm_id}/delete/{item_id}")
def delete_microclimate(rm_id: int, item_id: int, db: Session = Depends(get_db)):
    m = db.get(MeasMicroclimate, item_id)
    if m: db.delete(m)
    db.flush()
    rm = db.get(Workplace, rm_id)
    all_kuts = [x.kut for x in rm.microclimates if x.kut is not None]
    _update_summary_kut(rm, "microclimate", (kut_max(all_kuts) or 2), db)
    return RedirectResponse(f"/factor/microclimate/{rm_id}", status_code=303)


# ── ОСВЕЩЕНИЕ ─────────────────────────────────────────────────────────────────

@router.get("/lighting/{rm_id}", response_class=HTMLResponse)
def lighting_form(rm_id: int, request: Request, db: Session = Depends(get_db)):
    rm = db.get(Workplace, rm_id)
    if not rm: raise HTTPException(404)
    return templates.TemplateResponse("factors/lighting.html", {"request": request, "rm": rm, "items": rm.lightings})


@router.post("/lighting/{rm_id}/add")
def add_lighting(
    rm_id: int,
    e_fact: float = Form(...),
    e_norm: float = Form(...),
    db: Session = Depends(get_db),
):
    rm = db.get(Workplace, rm_id)
    if not rm: raise HTTPException(404)
    kut = calc_light.classify_lighting(e_fact, e_norm)
    m = MeasLighting(rm_id=rm_id, e_fact=e_fact, e_norm=e_norm, kut=kut)
    db.add(m)
    db.flush()
    all_kuts = [x.kut for x in rm.lightings if x.kut is not None]
    _update_summary_kut(rm, "lighting", (kut_max(all_kuts) or 2), db)
    return RedirectResponse(f"/factor/lighting/{rm_id}", status_code=303)


@router.post("/lighting/{rm_id}/delete/{item_id}")
def delete_lighting(rm_id: int, item_id: int, db: Session = Depends(get_db)):
    m = db.get(MeasLighting, item_id)
    if m: db.delete(m)
    db.flush()
    rm = db.get(Workplace, rm_id)
    all_kuts = [x.kut for x in rm.lightings if x.kut is not None]
    _update_summary_kut(rm, "lighting", (kut_max(all_kuts) or 2), db)
    return RedirectResponse(f"/factor/lighting/{rm_id}", status_code=303)


# ── ЭМП ───────────────────────────────────────────────────────────────────────

@router.get("/emf/{rm_id}", response_class=HTMLResponse)
def emf_form(rm_id: int, request: Request, db: Session = Depends(get_db)):
    rm = db.get(Workplace, rm_id)
    if not rm: raise HTTPException(404)
    return templates.TemplateResponse("factors/emf.html", {"request": request, "rm": rm, "items": rm.emfs})


@router.post("/emf/{rm_id}/add")
def add_emf(
    rm_id: int,
    emf_type: str = Form(...),
    fact_value: float = Form(...),
    pdu_value: float = Form(...),
    db: Session = Depends(get_db),
):
    rm = db.get(Workplace, rm_id)
    if not rm: raise HTTPException(404)
    kut = calc_emf.classify_emf(emf_type, fact_value, pdu_value)
    m = MeasEMF(rm_id=rm_id, emf_type=emf_type, fact_value=fact_value, pdu_value=pdu_value, kut=kut)
    db.add(m)
    db.flush()
    all_kuts = [x.kut for x in rm.emfs if x.kut is not None]
    _update_summary_kut(rm, "emf", (kut_max(all_kuts) or 2), db)
    return RedirectResponse(f"/factor/emf/{rm_id}", status_code=303)


@router.post("/emf/{rm_id}/delete/{item_id}")
def delete_emf(rm_id: int, item_id: int, db: Session = Depends(get_db)):
    m = db.get(MeasEMF, item_id)
    if m: db.delete(m)
    db.flush()
    rm = db.get(Workplace, rm_id)
    all_kuts = [x.kut for x in rm.emfs if x.kut is not None]
    _update_summary_kut(rm, "emf", (kut_max(all_kuts) or 2), db)
    return RedirectResponse(f"/factor/emf/{rm_id}", status_code=303)


# ── РАДИАЦИЯ ──────────────────────────────────────────────────────────────────

@router.get("/radiation/{rm_id}", response_class=HTMLResponse)
def radiation_form(rm_id: int, request: Request, db: Session = Depends(get_db)):
    rm = db.get(Workplace, rm_id)
    if not rm: raise HTTPException(404)
    return templates.TemplateResponse("factors/radiation.html", {"request": request, "rm": rm, "items": rm.radiations})


@router.post("/radiation/{rm_id}/add")
def add_radiation(
    rm_id: int,
    eff_dose_msv: float = Form(...),
    lens_dose_msv: float = Form(None),
    skin_dose_msv: float = Form(None),
    db: Session = Depends(get_db),
):
    rm = db.get(Workplace, rm_id)
    if not rm: raise HTTPException(404)
    kut = calc_rad.classify_radiation(eff_dose_msv, lens_dose_msv, skin_dose_msv)
    m = MeasRadiation(rm_id=rm_id, eff_dose_msv=eff_dose_msv,
                      lens_dose_msv=lens_dose_msv, skin_dose_msv=skin_dose_msv, kut=kut)
    db.add(m)
    db.flush()
    all_kuts = [x.kut for x in rm.radiations if x.kut is not None]
    _update_summary_kut(rm, "radiation", (kut_max(all_kuts) or 2), db)
    return RedirectResponse(f"/factor/radiation/{rm_id}", status_code=303)


@router.post("/radiation/{rm_id}/delete/{item_id}")
def delete_radiation(rm_id: int, item_id: int, db: Session = Depends(get_db)):
    m = db.get(MeasRadiation, item_id)
    if m: db.delete(m)
    db.flush()
    rm = db.get(Workplace, rm_id)
    all_kuts = [x.kut for x in rm.radiations if x.kut is not None]
    _update_summary_kut(rm, "radiation", (kut_max(all_kuts) or 2), db)
    return RedirectResponse(f"/factor/radiation/{rm_id}", status_code=303)


# ── ТЯЖЕСТЬ ───────────────────────────────────────────────────────────────────

@router.get("/heaviness/{rm_id}", response_class=HTMLResponse)
def heaviness_form(rm_id: int, request: Request, db: Session = Depends(get_db)):
    rm = db.get(Workplace, rm_id)
    if not rm: raise HTTPException(404)
    item = rm.heavinesses[0] if rm.heavinesses else None
    return templates.TemplateResponse("factors/heaviness.html", {"request": request, "rm": rm, "item": item})


@router.post("/heaviness/{rm_id}/save")
def save_heaviness(
    rm_id: int,
    sex: str = Form("m"),
    load_regional_1m: float = Form(None),
    load_general_1_5m: float = Form(None),
    load_general_5m: float = Form(None),
    mass_rare: float = Form(None),
    mass_frequent: float = Form(None),
    mass_total_floor: float = Form(None),
    mass_total_bench: float = Form(None),
    pose_standing_pct: float = Form(None),
    pose_awkward_pct: float = Form(None),
    bends_count: int = Form(None),
    moves_horizontal_km: float = Form(None),
    moves_vertical_km: float = Form(None),
    static_local: float = Form(None),
    static_regional: float = Form(None),
    static_one_hand: float = Form(None),
    static_two_hands: float = Form(None),
    static_body_legs: float = Form(None),
    db: Session = Depends(get_db),
):
    rm = db.get(Workplace, rm_id)
    if not rm: raise HTTPException(404)
    kut = calc_heavy.classify_heaviness(
        sex=sex,
        load_regional_1m=load_regional_1m,
        load_general_1_5m=load_general_1_5m,
        load_general_5m=load_general_5m,
        mass_rare=mass_rare,
        mass_frequent=mass_frequent,
        mass_total_floor=mass_total_floor,
        mass_total_bench=mass_total_bench,
        pose_standing_pct=pose_standing_pct,
        pose_awkward_pct=pose_awkward_pct,
        bends_count=bends_count,
        moves_horizontal_km=moves_horizontal_km,
        moves_vertical_km=moves_vertical_km,
        static_local=static_local,
        static_regional=static_regional,
        static_one_hand=static_one_hand,
        static_two_hands=static_two_hands,
        static_body_legs=static_body_legs,
    )
    if rm.heavinesses:
        m = rm.heavinesses[0]
    else:
        m = MeasHeaviness(rm_id=rm_id)
        db.add(m)
    m.sex = sex
    m.load_regional_1m = load_regional_1m
    m.load_general_1_5m = load_general_1_5m
    m.load_general_5m = load_general_5m
    m.mass_rare = mass_rare
    m.mass_frequent = mass_frequent
    m.mass_total_floor = mass_total_floor
    m.mass_total_bench = mass_total_bench
    m.pose_standing_pct = pose_standing_pct
    m.pose_awkward_pct = pose_awkward_pct
    m.bends_count = bends_count
    m.moves_horizontal_km = moves_horizontal_km
    m.moves_vertical_km = moves_vertical_km
    m.static_local = static_local
    m.static_regional = static_regional
    m.static_one_hand = static_one_hand
    m.static_two_hands = static_two_hands
    m.static_body_legs = static_body_legs
    m.kut = kut
    _update_summary_kut(rm, "heaviness", kut, db)
    return RedirectResponse(f"/factor/heaviness/{rm_id}", status_code=303)


# ── НАПРЯЖЁННОСТЬ ─────────────────────────────────────────────────────────────

@router.get("/intensity/{rm_id}", response_class=HTMLResponse)
def intensity_form(rm_id: int, request: Request, db: Session = Depends(get_db)):
    rm = db.get(Workplace, rm_id)
    if not rm: raise HTTPException(404)
    item = rm.intensities[0] if rm.intensities else None
    return templates.TemplateResponse("factors/intensity.html", {"request": request, "rm": rm, "item": item})


@router.post("/intensity/{rm_id}/save")
def save_intensity(
    rm_id: int,
    intellectual_load: int = Form(1),
    perception_load: int = Form(1),
    work_distribution: int = Form(1),
    work_nature: int = Form(1),
    concentration_pct: float = Form(None),
    signal_density: int = Form(None),
    watch_objects: int = Form(None),
    optic_pct: float = Form(None),
    voice_hours_week: float = Form(None),
    emotional_load: int = Form(1),
    life_risk: bool = Form(False),
    others_safety: bool = Form(False),
    conflicts_per_shift: int = Form(None),
    mono_elements: int = Form(None),
    operation_duration_sec: int = Form(None),
    active_actions_pct: float = Form(None),
    passive_watch_pct: float = Form(None),
    shift_duration_hours: float = Form(None),
    shift_type: int = Form(1),
    break_adequacy: int = Form(1),
    db: Session = Depends(get_db),
):
    rm = db.get(Workplace, rm_id)
    if not rm: raise HTTPException(404)
    kut = calc_intens.classify_intensity(
        intellectual_load=intellectual_load,
        perception_load=perception_load,
        work_distribution=work_distribution,
        work_nature=work_nature,
        concentration_pct=concentration_pct,
        signal_density=signal_density,
        watch_objects=watch_objects,
        optic_pct=optic_pct,
        voice_hours_week=voice_hours_week,
        emotional_load=emotional_load,
        life_risk=life_risk,
        others_safety=others_safety,
        conflicts_per_shift=conflicts_per_shift,
        mono_elements=mono_elements,
        operation_duration_sec=operation_duration_sec,
        active_actions_pct=active_actions_pct,
        passive_watch_pct=passive_watch_pct,
        shift_duration_hours=shift_duration_hours,
        shift_type=shift_type,
        break_adequacy=break_adequacy,
    )
    if rm.intensities:
        m = rm.intensities[0]
    else:
        m = MeasIntensity(rm_id=rm_id)
        db.add(m)
    m.intellectual_load = intellectual_load
    m.perception_load = perception_load
    m.work_distribution = work_distribution
    m.work_nature = work_nature
    m.concentration_pct = concentration_pct
    m.signal_density = signal_density
    m.watch_objects = watch_objects
    m.optic_pct = optic_pct
    m.voice_hours_week = voice_hours_week
    m.emotional_load = emotional_load
    m.life_risk = life_risk
    m.others_safety = others_safety
    m.conflicts_per_shift = conflicts_per_shift
    m.mono_elements = mono_elements
    m.operation_duration_sec = operation_duration_sec
    m.active_actions_pct = active_actions_pct
    m.passive_watch_pct = passive_watch_pct
    m.shift_duration_hours = shift_duration_hours
    m.shift_type = shift_type
    m.break_adequacy = break_adequacy
    m.kut = kut
    _update_summary_kut(rm, "intensity", kut, db)
    return RedirectResponse(f"/factor/intensity/{rm_id}", status_code=303)


# ── БИОЛОГИЧЕСКИЙ ─────────────────────────────────────────────────────────────

@router.get("/bio/{rm_id}", response_class=HTMLResponse)
def bio_form(rm_id: int, request: Request, db: Session = Depends(get_db)):
    rm = db.get(Workplace, rm_id)
    if not rm: raise HTTPException(404)
    return templates.TemplateResponse("factors/bio.html", {"request": request, "rm": rm, "items": rm.bios})


@router.post("/bio/{rm_id}/add")
def add_bio(
    rm_id: int,
    name: str = Form(...),
    bio_type: str = Form("producer"),
    pdk: float = Form(None),
    c_fact: float = Form(None),
    pathogenicity_group: int = Form(None),
    db: Session = Depends(get_db),
):
    rm = db.get(Workplace, rm_id)
    if not rm: raise HTTPException(404)
    kut = calc_bio.classify_bio(
        bio_type=bio_type, c_fact=c_fact, pdk=pdk,
        pathogenicity_group=pathogenicity_group,
    )
    m = MeasBio(
        rm_id=rm_id, name=name, bio_type=bio_type,
        pdk=pdk, c_fact=c_fact, pathogenicity_group=pathogenicity_group, kut=kut,
    )
    db.add(m)
    db.flush()
    all_kuts = [x.kut for x in rm.bios if x.kut is not None]
    _update_summary_kut(rm, "bio", (kut_max(all_kuts) or 2), db)
    return RedirectResponse(f"/factor/bio/{rm_id}", status_code=303)


@router.post("/bio/{rm_id}/delete/{item_id}")
def delete_bio(rm_id: int, item_id: int, db: Session = Depends(get_db)):
    m = db.get(MeasBio, item_id)
    if m: db.delete(m)
    db.flush()
    rm = db.get(Workplace, rm_id)
    all_kuts = [x.kut for x in rm.bios if x.kut is not None]
    _update_summary_kut(rm, "bio", (kut_max(all_kuts) or 2), db)
    return RedirectResponse(f"/factor/bio/{rm_id}", status_code=303)


# ── ЛАЗЕРНОЕ ИЗЛУЧЕНИЕ ────────────────────────────────────────────────────────

@router.get("/laser/{rm_id}", response_class=HTMLResponse)
def laser_form(rm_id: int, request: Request, db: Session = Depends(get_db)):
    rm = db.get(Workplace, rm_id)
    if not rm: raise HTTPException(404)
    return templates.TemplateResponse("factors/laser.html", {"request": request, "rm": rm, "items": rm.lasers})


@router.post("/laser/{rm_id}/add")
def add_laser(
    rm_id: int,
    fact_value: float = Form(...),
    pdu1: float = Form(...),
    pdu2: float = Form(...),
    db: Session = Depends(get_db),
):
    rm = db.get(Workplace, rm_id)
    if not rm: raise HTTPException(404)
    kut = calc_laser.classify_laser(fact_value, pdu1, pdu2)
    m = MeasLaser(rm_id=rm_id, fact_value=fact_value, pdu1=pdu1, pdu2=pdu2, kut=kut)
    db.add(m)
    db.flush()
    all_kuts = [x.kut for x in rm.lasers if x.kut is not None]
    _update_summary_kut(rm, "laser", (kut_max(all_kuts) or 2), db)
    return RedirectResponse(f"/factor/laser/{rm_id}", status_code=303)


@router.post("/laser/{rm_id}/delete/{item_id}")
def delete_laser(rm_id: int, item_id: int, db: Session = Depends(get_db)):
    m = db.get(MeasLaser, item_id)
    if m: db.delete(m)
    db.flush()
    rm = db.get(Workplace, rm_id)
    all_kuts = [x.kut for x in rm.lasers if x.kut is not None]
    _update_summary_kut(rm, "laser", (kut_max(all_kuts) or 2), db)
    return RedirectResponse(f"/factor/laser/{rm_id}", status_code=303)


# ── УФ-ИЗЛУЧЕНИЕ ──────────────────────────────────────────────────────────────

@router.get("/uv/{rm_id}", response_class=HTMLResponse)
def uv_form(rm_id: int, request: Request, db: Session = Depends(get_db)):
    rm = db.get(Workplace, rm_id)
    if not rm: raise HTTPException(404)
    return templates.TemplateResponse("factors/uv.html", {"request": request, "rm": rm, "items": rm.uvs})


@router.post("/uv/{rm_id}/add")
def add_uv(
    rm_id: int,
    fact_value: float = Form(...),
    dii: float = Form(...),
    db: Session = Depends(get_db),
):
    rm = db.get(Workplace, rm_id)
    if not rm: raise HTTPException(404)
    kut = calc_laser.classify_uv(fact_value, dii)
    m = MeasUV(rm_id=rm_id, fact_value=fact_value, dii=dii, kut=kut)
    db.add(m)
    db.flush()
    all_kuts = [x.kut for x in rm.uvs if x.kut is not None]
    _update_summary_kut(rm, "uv", (kut_max(all_kuts) or 2), db)
    return RedirectResponse(f"/factor/uv/{rm_id}", status_code=303)


@router.post("/uv/{rm_id}/delete/{item_id}")
def delete_uv(rm_id: int, item_id: int, db: Session = Depends(get_db)):
    m = db.get(MeasUV, item_id)
    if m: db.delete(m)
    db.flush()
    rm = db.get(Workplace, rm_id)
    all_kuts = [x.kut for x in rm.uvs if x.kut is not None]
    _update_summary_kut(rm, "uv", (kut_max(all_kuts) or 2), db)
    return RedirectResponse(f"/factor/uv/{rm_id}", status_code=303)


# ── АЭРОИОННЫЙ СОСТАВ ─────────────────────────────────────────────────────────

@router.get("/aeroion/{rm_id}", response_class=HTMLResponse)
def aeroion_form(rm_id: int, request: Request, db: Session = Depends(get_db)):
    rm = db.get(Workplace, rm_id)
    if not rm: raise HTTPException(404)
    return templates.TemplateResponse("factors/aeroion.html", {"request": request, "rm": rm, "items": rm.aeroions})


@router.post("/aeroion/{rm_id}/add")
def add_aeroion(
    rm_id: int,
    ro_pos: float = Form(...),
    ro_neg: float = Form(...),
    db: Session = Depends(get_db),
):
    rm = db.get(Workplace, rm_id)
    if not rm: raise HTTPException(404)
    kut = calc_aeroion.classify_aeroion(ro_pos, ro_neg)
    m = MeasAeroion(rm_id=rm_id, ro_pos=ro_pos, ro_neg=ro_neg, kut=kut)
    db.add(m)
    db.flush()
    all_kuts = [x.kut for x in rm.aeroions if x.kut is not None]
    _update_summary_kut(rm, "aeroion", (kut_max(all_kuts) or 2), db)
    return RedirectResponse(f"/factor/aeroion/{rm_id}", status_code=303)


@router.post("/aeroion/{rm_id}/delete/{item_id}")
def delete_aeroion(rm_id: int, item_id: int, db: Session = Depends(get_db)):
    m = db.get(MeasAeroion, item_id)
    if m: db.delete(m)
    db.flush()
    rm = db.get(Workplace, rm_id)
    all_kuts = [x.kut for x in rm.aeroions if x.kut is not None]
    _update_summary_kut(rm, "aeroion", (kut_max(all_kuts) or 2), db)
    return RedirectResponse(f"/factor/aeroion/{rm_id}", status_code=303)
