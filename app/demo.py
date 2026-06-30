# -*- coding: utf-8 -*-
"""
Демонстрационные данные, извлечённые из рабочей копии «Аттестация 5.1»
(ИЛ ООО «Югополис», г. Краснодар): организация, рабочие места и замеры
по факторам. Загружается только при SEED_DEMO_DATA=true (идемпотентно).
"""
import logging

from sqlalchemy.orm import Session

from app.calculations import (
    chemical as calc_chem,
    microclimate as calc_micro,
    noise_vibration as calc_nv,
)
from app.calculations.summary import classify_summary
from app.calculations.utils import kut_max
from app.models import (
    MeasChemical, MeasMicroclimate, MeasNoise, MeasVibrGeneral,
    Organization, Summary, Workplace,
)

log = logging.getLogger(__name__)

ORG_INN = "2308217850"

# Химические вещества в кабине/салоне ТС (все фактические — ННПО, ниже предела
# обнаружения, поэтому c=0). Источник: xml/Химический.xml.
_TS_CHEMICALS = [
    # name, danger_class, pdk_ss, pdk_max, is_irritant, is_directed
    ("Углерод оксид",                                    4, None, 20.0,  False, True),
    ("Углеводороды алифатические предельные С1-10 (в пересчёте на С)", 4, 300.0, 900.0, False, False),
    ("Азота диоксид",                                    3, None, 2.0,   True,  True),
    ("Проп-2-ен-1-аль (акролеин)",                       2, None, 0.2,   True,  False),
]


def _add_chemicals(db: Session, rm: Workplace) -> int:
    kuts = []
    for name, dc, pdk_ss, pdk_max, irr, directed in _TS_CHEMICALS:
        kut = calc_chem.classify_chemical(
            danger_class=dc, is_carcinogen=False,
            is_allergen_high=False, is_allergen_mod=False,
            is_irritant=irr, is_directed=directed,
            is_repro=False, is_antitumor=False,
            c_ss=0.0, c_max=0.0, pdk_ss=pdk_ss, pdk_max=pdk_max,
        )
        db.add(MeasChemical(
            rm_id=rm.id, substance_name=name, danger_class=dc,
            pdk_ss=pdk_ss, pdk_max=pdk_max, c_ss=0.0, c_max=0.0,
            is_irritant=irr, is_directed=directed, kut=kut,
        ))
        kuts.append(kut)
    return kut_max(kuts) or 2


def load_demo(db: Session) -> bool:
    """Создаёт демо-организацию с РМ и замерами. Возвращает False, если уже есть."""
    if db.query(Organization).filter_by(inn=ORG_INN).first():
        return False

    org = Organization(
        name="ООО «Югополис»",
        inn=ORG_INN,
        address="350033, Краснодарский край, г. Краснодар, ул. Ставропольская, 41",
    )
    db.add(org)
    db.flush()

    # ── РМ 1: Водитель ТС (ГАЗ 322132) — химический ──────────────────────────
    rm1 = Workplace(org_id=org.id, name="Водитель транспортного средства (ГАЗ 322132, рег. Н637АТ93)",
                    podr="Транспортный участок", profession="Водитель", num_workers=1, shift_hours=8.0)
    db.add(rm1); db.flush()
    k_chem1 = _add_chemicals(db, rm1)
    db.add(Summary(rm_id=rm1.id, kut_chemical=k_chem1,
                   kut_final=classify_summary([k_chem1])))

    # ── РМ 2: Машинист крана (управление краном) — химический ────────────────
    rm2 = Workplace(org_id=org.id, name="Машинист крана автомобильного",
                    podr="Транспортный участок", profession="Машинист крана", num_workers=1, shift_hours=8.0)
    db.add(rm2); db.flush()
    k_chem2 = _add_chemicals(db, rm2)
    db.add(Summary(rm_id=rm2.id, kut_chemical=k_chem2,
                   kut_final=classify_summary([k_chem2])))

    # ── РМ 3: Стропальщик (работы с тележкой) — вибрация общая ───────────────
    rm3 = Workplace(org_id=org.id, name="Стропальщик (выполнение работ с применением тележки)",
                    podr="Транспортный участок", profession="Стропальщик", num_workers=1, shift_hours=8.0)
    db.add(rm3); db.flush()
    vibr = [("X", 97.0, 112.0), ("Y", 96.0, 112.0), ("Z", 97.0, 115.0)]
    vk = []
    for axis, fact, _norm in vibr:
        kut = calc_nv.classify_vibr_general(fact, axis)
        db.add(MeasVibrGeneral(rm_id=rm3.id, axis=axis, corr_level_db=fact, kut=kut))
        vk.append(kut)
    k_vibr = kut_max(vk) or 2
    db.add(Summary(rm_id=rm3.id, kut_vibr_general=k_vibr,
                   kut_final=classify_summary([k_vibr])))

    # ── РМ 4: Рабочий теплицы — микроклимат (нагрев, IIб) ────────────────────
    rm4 = Workplace(org_id=org.id, name="Овощевод (теплица)",
                    podr="Тепличное хозяйство", profession="Овощевод", num_workers=1, shift_hours=8.0)
    db.add(rm4); db.flush()
    k_micro = calc_micro.classify_microclimate_heating("IIb", 20.5)
    db.add(MeasMicroclimate(
        rm_id=rm4.id, season="warm", mode="heating", work_category="IIb",
        tns_index=20.5, air_temp=23.8, air_speed=0.1, humidity=52.0, kut=k_micro,
    ))
    db.add(Summary(rm_id=rm4.id, kut_microclimate=k_micro,
                   kut_final=classify_summary([k_micro])))

    # ── РМ 5: Лаборант — шум (отбор проб / ремонтные работы) ─────────────────
    rm5 = Workplace(org_id=org.id, name="Лаборант (отбор проб, ремонтные работы)",
                    podr="Испытательная лаборатория", profession="Лаборант", num_workers=1, shift_hours=8.0)
    db.add(rm5); db.flush()
    nk = []
    for leq in (86.0, 84.0):
        kut = calc_nv.classify_noise(leq)
        db.add(MeasNoise(rm_id=rm5.id, leq_dba=leq, kut=kut))
        nk.append(kut)
    k_noise = kut_max(nk) or 2
    db.add(Summary(rm_id=rm5.id, kut_noise=k_noise,
                   kut_final=classify_summary([k_noise])))

    db.commit()
    log.info("Demo data loaded: org «Югополис» + 5 РМ")
    return True
