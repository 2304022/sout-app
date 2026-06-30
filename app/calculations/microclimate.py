"""
Микроклимат — Приложения №13 (нагрев) и №14 (охлаждение) к Приказу №33н.
"""
from app.calculations.utils import kut_max

# ТНС-индекс °С: (категория -> [(верхняя граница включительно, kut), ...])
_TNS_THRESHOLDS: dict[str, list[tuple[float, int]]] = {
    "Ia":  [(26.4, 2), (26.6, 31), (27.4, 32), (28.6, 33), (31.0, 34)],
    "Ib":  [(25.8, 2), (26.1, 31), (26.9, 32), (27.9, 33), (30.3, 34)],
    "IIa": [(25.1, 2), (25.5, 31), (26.2, 32), (27.3, 33), (29.9, 34)],
    "IIb": [(23.9, 2), (24.2, 31), (25.0, 32), (26.4, 33), (29.1, 34)],
    "III": [(21.8, 2), (22.0, 31), (23.4, 32), (25.7, 33), (27.9, 34)],
}

# Температура воздуха °С для охлаждающего микроклимата (нижняя граница → kut)
# Таблица для теплого/холодного периода (категория -> [(нижняя граница, kut), ...] убывающий)
_COOL_THRESHOLDS: dict[str, list[tuple[float, int]]] = {
    "Ia":  [(20.0, 2), (18.0, 31), (16.0, 32), (14.0, 33), (12.0, 34)],
    "Ib":  [(19.0, 2), (17.0, 31), (15.0, 32), (13.0, 33), (11.0, 34)],
    "IIa": [(17.0, 2), (14.0, 31), (12.0, 32), (10.0, 33), (8.0, 34)],
    "IIb": [(15.0, 2), (13.0, 31), (11.0, 32), (9.0, 33),  (7.0, 34)],
    "III": [(13.0, 2), (12.0, 31), (10.0, 32), (8.0, 33),  (6.0, 34)],
}


def classify_microclimate_heating(work_category: str, tns_index: float) -> int:
    """ТНС-индекс → класс (нагревающий микроклимат)."""
    thresholds = _TNS_THRESHOLDS.get(work_category, _TNS_THRESHOLDS["IIa"])
    for upper, kut in thresholds:
        if tns_index <= upper:
            return kut
    return 4


def classify_microclimate_cooling(
    work_category: str,
    air_temp: float,
    air_speed: float | None = None,
    humidity: float | None = None,
    radiant_heat: float | None = None,
) -> int:
    """Охлаждающий микроклимат — базовая оценка по температуре воздуха."""
    thresholds = _COOL_THRESHOLDS.get(work_category, _COOL_THRESHOLDS["IIa"])

    # Базовый класс по температуре воздуха
    base = 4
    for lower, k in thresholds:
        if air_temp >= lower:
            base = k
            break

    # Каждая корректировка задаёт «пол» по тяжести; берём наиболее тяжёлый класс
    candidates = [base]

    # Скорость воздуха
    if air_speed is not None and air_speed >= 0.6:
        candidates.append(31)

    # Влажность
    if humidity is not None:
        if humidity < 10:
            candidates.append(32)
        elif humidity < 15:
            candidates.append(31)

    # Тепловое излучение (Вт/м²): источник micro.mdb KUT тип «тепл»
    if radiant_heat is not None:
        if radiant_heat > 2800:
            candidates.append(4)
        elif radiant_heat > 2500:
            candidates.append(34)
        elif radiant_heat > 2000:
            candidates.append(33)
        elif radiant_heat > 1500:
            candidates.append(32)
        elif radiant_heat > 140:
            candidates.append(31)

    return kut_max(candidates)
