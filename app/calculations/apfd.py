"""
АПФД (аэрозоли фиброгенного действия) — Приложение №10 к Приказу №33н.
"""


def calc_pn(c_fact: float, shifts_per_year: int, work_years: float) -> float:
    """Фактическая пылевая нагрузка за нормируемый стаж мг×смен."""
    return c_fact * shifts_per_year * work_years


def calc_kpn(pdk_ss: float, shifts_per_year: int, work_years: float) -> float:
    """Контрольная пылевая нагрузка."""
    return pdk_ss * shifts_per_year * work_years


def classify_apfd(
    pdk_ss: float,
    fibrogenicity: str,  # "high"/"moderate" (ПДК≤2) or "low" (ПДК>2)
    c_fact: float,
    shifts_per_year: int = 247,
    work_years: float = 25.0,
) -> tuple[int, float, float]:
    """Returns (kut, pn_fact, kpn)."""
    pn = calc_pn(c_fact, shifts_per_year, work_years)
    kpn = calc_kpn(pdk_ss, shifts_per_year, work_years)

    # Первичная оценка по концентрации
    r_conc = c_fact / pdk_ss if pdk_ss else 0.0

    # Первичная оценка по ПН
    r_pn = pn / kpn if kpn else 0.0

    # Используем максимальную кратность
    r = max(r_conc, r_pn)

    # Высокофиброгенные и умеренно фиброгенные (ПДК ≤ 2 мг/м³)
    if fibrogenicity in ("high", "moderate"):
        if r <= 1.0:
            kut = 2
        elif r <= 2.0:
            kut = 31
        elif r <= 4.0:
            kut = 32
        elif r <= 10.0:
            kut = 33
        else:
            kut = 34
    else:
        # Слабофиброгенные (ПДК > 2 мг/м³)
        if r <= 1.0:
            kut = 2
        elif r <= 3.0:
            kut = 31
        elif r <= 6.0:
            kut = 32
        elif r <= 10.0:
            kut = 33
        else:
            kut = 34

    return kut, pn, kpn
