"""
Тяжесть трудового процесса — Приложение №20 к Приказу №33н.
Возвращает максимальный класс среди всех показателей.
"""


def _kut_load_regional(value: float, sex: str) -> int:
    """Физическая динамическая нагрузка региональная (до 1 м) кг·м/смену."""
    if sex == "f":
        if value < 1500: return 1
        if value < 3000: return 2
        if value < 4000: return 31
        return 32
    else:
        if value < 2500: return 1
        if value < 5000: return 2
        if value < 7000: return 31
        return 32


def _kut_load_general_1_5m(value: float, sex: str) -> int:
    """Физическая динамическая нагрузка общая 1–5 м кг·м/смену."""
    if sex == "f":
        if value < 7500:  return 1
        if value < 15000: return 2
        if value < 25000: return 31
        return 32
    else:
        if value < 12500: return 1
        if value < 25000: return 2
        if value < 35000: return 31
        return 32


def _kut_load_general_5m(value: float, sex: str) -> int:
    """Физическая динамическая нагрузка общая >5 м кг·м/смену."""
    if sex == "f":
        if value < 14000: return 1
        if value < 28000: return 2
        if value < 40000: return 31
        return 32
    else:
        if value < 24000: return 1
        if value < 46000: return 2
        if value < 70000: return 31
        return 32


def _kut_mass_rare(value: float, sex: str) -> int:
    """Масса поднимаемого груза разово (до 2 раз/ч) кг."""
    if sex == "f":
        if value <= 5:  return 1
        if value <= 10: return 2
        if value <= 12: return 31
        return 32
    else:
        if value <= 15: return 1
        if value <= 30: return 2
        if value <= 35: return 31
        return 32


def _kut_mass_frequent(value: float, sex: str) -> int:
    """Масса поднимаемого груза постоянно (>2 раз/ч) кг."""
    if sex == "f":
        if value <= 3:  return 1
        if value <= 7:  return 2
        if value <= 10: return 31
        return 32
    else:
        if value <= 5:  return 1
        if value <= 15: return 2
        if value <= 20: return 31
        return 32


def _kut_mass_total(value: float, sex: str, source: str = "floor") -> int:
    """Суммарная масса груза за смену кг. source: floor/bench."""
    if source == "floor":
        if sex == "f":
            if value <= 500:  return 1
            if value <= 1000: return 2
            if value <= 1500: return 31
            return 32
        else:
            if value <= 3000: return 1
            if value <= 5000: return 2
            if value <= 7000: return 31
            return 32
    else:  # bench
        if sex == "f":
            if value <= 1500: return 1
            if value <= 2000: return 2
            if value <= 2500: return 31
            return 32
        else:
            if value <= 12000: return 1
            if value <= 15000: return 2
            if value <= 20000: return 31
            return 32


def _kut_pose_standing(pct: float) -> int:
    if pct < 40:  return 1
    if pct < 60:  return 2
    if pct < 80:  return 31
    return 32


def _kut_pose_awkward(pct: float) -> int:
    if pct < 10:  return 1
    if pct < 25:  return 2
    if pct < 50:  return 31
    return 32


def _kut_bends(count: int) -> int:
    if count < 50:   return 1
    if count < 100:  return 2
    if count < 300:  return 31
    return 32


def _kut_moves_horiz(km: float) -> int:
    if km < 4:  return 1
    if km < 8:  return 2
    if km < 12: return 31
    return 32


def _kut_moves_vert(km: float) -> int:
    if km < 1:   return 1
    if km < 2.5: return 2
    if km < 5:   return 31
    return 32


def _kut_static_local(value: float) -> int:
    if value < 20000: return 1
    if value < 40000: return 2
    if value < 60000: return 31
    return 32


def _kut_static_regional(value: float) -> int:
    if value < 10000: return 1
    if value < 20000: return 2
    if value < 30000: return 31
    return 32


def _kut_static_one_hand(value: float, sex: str) -> int:
    if sex == "f":
        if value < 11000: return 1
        if value < 22000: return 2
        if value < 42000: return 31
        return 32
    else:
        if value < 18000: return 1
        if value < 36000: return 2
        if value < 70000: return 31
        return 32


def _kut_static_two_hands(value: float, sex: str) -> int:
    if sex == "f":
        if value < 22000:  return 1
        if value < 42000:  return 2
        if value < 84000:  return 31
        return 32
    else:
        if value < 36000:  return 1
        if value < 70000:  return 2
        if value < 140000: return 31
        return 32


def _kut_static_body_legs(value: float, sex: str) -> int:
    if sex == "f":
        if value < 26000:  return 1
        if value < 60000:  return 2
        if value < 120000: return 31
        return 32
    else:
        if value < 43000:  return 1
        if value < 100000: return 2
        if value < 200000: return 31
        return 32


def classify_heaviness(
    sex: str = "m",
    load_regional_1m: float | None = None,
    load_general_1_5m: float | None = None,
    load_general_5m: float | None = None,
    mass_rare: float | None = None,
    mass_frequent: float | None = None,
    mass_total_floor: float | None = None,
    mass_total_bench: float | None = None,
    pose_standing_pct: float | None = None,
    pose_awkward_pct: float | None = None,
    bends_count: int | None = None,
    moves_horizontal_km: float | None = None,
    moves_vertical_km: float | None = None,
    static_local: float | None = None,
    static_regional: float | None = None,
    static_one_hand: float | None = None,
    static_two_hands: float | None = None,
    static_body_legs: float | None = None,
) -> int:
    kuts = []
    if load_regional_1m is not None:
        kuts.append(_kut_load_regional(load_regional_1m, sex))
    if load_general_1_5m is not None:
        kuts.append(_kut_load_general_1_5m(load_general_1_5m, sex))
    if load_general_5m is not None:
        kuts.append(_kut_load_general_5m(load_general_5m, sex))
    if mass_rare is not None:
        kuts.append(_kut_mass_rare(mass_rare, sex))
    if mass_frequent is not None:
        kuts.append(_kut_mass_frequent(mass_frequent, sex))
    if mass_total_floor is not None:
        kuts.append(_kut_mass_total(mass_total_floor, sex, "floor"))
    if mass_total_bench is not None:
        kuts.append(_kut_mass_total(mass_total_bench, sex, "bench"))
    if pose_standing_pct is not None:
        kuts.append(_kut_pose_standing(pose_standing_pct))
    if pose_awkward_pct is not None:
        kuts.append(_kut_pose_awkward(pose_awkward_pct))
    if bends_count is not None:
        kuts.append(_kut_bends(bends_count))
    if moves_horizontal_km is not None:
        kuts.append(_kut_moves_horiz(moves_horizontal_km))
    if moves_vertical_km is not None:
        kuts.append(_kut_moves_vert(moves_vertical_km))
    if static_local is not None:
        kuts.append(_kut_static_local(static_local))
    if static_regional is not None:
        kuts.append(_kut_static_regional(static_regional))
    if static_one_hand is not None:
        kuts.append(_kut_static_one_hand(static_one_hand, sex))
    if static_two_hands is not None:
        kuts.append(_kut_static_two_hands(static_two_hands, sex))
    if static_body_legs is not None:
        kuts.append(_kut_static_body_legs(static_body_legs, sex))
    return max(kuts) if kuts else 2
