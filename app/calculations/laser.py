"""
Лазерное и ультрафиолетовое излучение — Приложение №18 к Приказу №33н.
"""


def classify_laser(fact_value: float, pdu1: float, pdu2: float) -> int:
    """
    Лазерное излучение.
    pdu1 — ПДУ для однократного воздействия / хронического (меньший норматив);
    pdu2 — ПДУ максимальный (больший норматив);
    fact_value — фактический уровень в тех же единицах.
    """
    if pdu2 <= 0:
        return 2
    # ≤ ПДУ1 и ≤ ПДУ2 → допустимый
    if fact_value <= pdu1 and fact_value <= pdu2:
        return 2
    # > ПДУ1, но ≤ ПДУ2 → 3.1
    if fact_value <= pdu2:
        return 31
    r = fact_value / pdu2
    if r <= 10.0:
        return 32
    if r <= 100.0:
        return 33
    if r <= 1000.0:
        return 34
    return 4


def classify_uv(fact_value: float, dii: float) -> int:
    """
    УФ-излучение. Оценка по допустимой интенсивности излучения (ДИИ), Вт/м².
    ≤ ДИИ → класс 2; > ДИИ → класс 3.1 (работа только в СИЗ).
    """
    if dii <= 0:
        return 2
    return 2 if fact_value <= dii else 31
