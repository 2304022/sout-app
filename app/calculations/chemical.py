"""
Химический фактор — Приложение №1 к Приказу №33н.
Возвращает kut: 1, 2, 31, 32, 33, 34, 4.
"""
import math


def classify_chemical(
    danger_class: int,
    is_carcinogen: bool,
    is_allergen_high: bool,
    is_allergen_mod: bool,
    is_irritant: bool,
    is_directed: bool,  # остронаправленного действия
    is_repro: bool,     # репротоксикант
    is_antitumor: bool, # противоопухолевые / гормоны / наркоанальгетики
    c_ss: float | None,   # факт. среднесменная мг/м³
    c_max: float | None,  # факт. максимальная мг/м³
    pdk_ss: float | None,
    pdk_max: float | None,
) -> int:
    # Вещества авт. класс 4 (без измерений)
    if is_antitumor:
        return 4

    # Канцерогены и репротоксиканты оцениваются по ПДКсс
    if is_carcinogen or is_repro:
        if pdk_ss is None or c_ss is None:
            return 2
        r = c_ss / pdk_ss
        if r <= 1.0:
            return 2
        if r <= 2.0:
            return 31
        if r <= 4.0:
            return 32
        if r <= 10.0:
            return 33
        return 34

    # Высокоопасные аллергены
    if is_allergen_high:
        if pdk_max is None or c_max is None:
            return 2
        r = c_max / pdk_max
        if r <= 1.0:
            return 2
        if r <= 2.0:
            return 32
        if r <= 5.0:
            return 33
        if r <= 15.0:
            return 34
        if r <= 20.0:
            return 4
        return 4

    # Умеренно опасные аллергены
    if is_allergen_mod:
        if pdk_max is None or c_max is None:
            return 2
        r = c_max / pdk_max
        if r <= 1.0:
            return 2
        if r <= 3.0:
            return 31
        if r <= 15.0:
            return 32
        if r <= 20.0:
            return 33
        return 34

    # Раздражающие
    if is_irritant:
        if pdk_max is None or c_max is None:
            return 2
        r = c_max / pdk_max
        if r <= 1.0:
            return 2
        if r <= 2.0:
            return 31
        if r <= 5.0:
            return 32
        if r <= 10.0:
            return 33
        if r <= 50.0:
            return 34
        return 4

    # Остронаправленного действия
    if is_directed:
        if pdk_max is None or c_max is None:
            return 2
        r = c_max / pdk_max
        if r <= 1.0:
            return 2
        if r <= 2.0:
            return 31
        if r <= 4.0:
            return 32
        if r <= 6.0:
            return 33
        if r <= 10.0:
            return 34
        return 4

    # Общие (1–4 кл. опасности)
    # Оцениваем по максимальной (если есть) и среднесменной
    kut_vals = []

    if pdk_ss and c_ss:
        r = c_ss / pdk_ss
        if r <= 1.0:
            kut_vals.append(2)
        elif r <= 3.0:
            kut_vals.append(31)
        elif r <= 10.0:
            kut_vals.append(32)
        elif r <= 15.0:
            kut_vals.append(33)
        elif r <= 20.0:
            kut_vals.append(34)
        else:
            kut_vals.append(4)

    if pdk_max and c_max:
        r = c_max / pdk_max
        if r <= 1.0:
            kut_vals.append(2)
        elif r <= 3.0:
            kut_vals.append(31)
        elif r <= 10.0:
            kut_vals.append(32)
        elif r <= 15.0:
            kut_vals.append(33)
        elif r <= 20.0:
            kut_vals.append(34)
        else:
            kut_vals.append(4)

    if not kut_vals:
        return 2

    return max(kut_vals)


def classify_chemical_mixture(substances: list[dict]) -> int:
    """
    Эффект суммации для смеси однонаправленных веществ.
    substances: list of {c_ss, pdk_ss}
    Возвращает kut суммарного воздействия.
    """
    total = sum(
        (s["c_ss"] / s["pdk_ss"])
        for s in substances
        if s.get("c_ss") and s.get("pdk_ss")
    )
    if total <= 1.0:
        return 2
    if total <= 3.0:
        return 31
    if total <= 10.0:
        return 32
    if total <= 15.0:
        return 33
    if total <= 20.0:
        return 34
    return 4
