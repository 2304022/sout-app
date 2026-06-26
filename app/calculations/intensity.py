"""
Напряжённость трудового процесса — Приложение №21 к Приказу №33н.
"""


def _kut_intellectual(level: int) -> int:
    """Интеллектуальные нагрузки (1–4 балла по описанию)."""
    # 1=простые задачи, 2=несколько операций, 3=сложные задачи, 4=эвристическая деятельность
    if level <= 1: return 1
    if level <= 2: return 2
    if level <= 3: return 31
    return 32


def _kut_signal_density(per_hour: int) -> int:
    """Плотность сигналов, ед./час."""
    if per_hour <= 75:  return 1
    if per_hour <= 175: return 2
    if per_hour <= 300: return 31
    return 32


def _kut_watch_objects(count: int) -> int:
    """Число объектов одновременного наблюдения."""
    if count <= 5:  return 1
    if count <= 10: return 2
    if count <= 25: return 31
    return 32


def _kut_optic(pct: float) -> int:
    """Работа с оптическими приборами, % смены."""
    if pct <= 25: return 1
    if pct <= 50: return 2
    if pct <= 75: return 31
    return 32


def _kut_emotional(level: int) -> int:
    """Эмоциональные нагрузки (1–4)."""
    if level <= 1: return 1
    if level <= 2: return 2
    if level <= 3: return 31
    return 32


def _kut_mono_elements(count: int) -> int:
    """Число элементов в простой операции."""
    if count > 10: return 1
    if count >= 6: return 2
    if count >= 3: return 31
    return 32


def _kut_passive_watch(pct: float) -> int:
    """Пассивное наблюдение, % смены."""
    if pct < 75: return 1
    if pct <= 80: return 2
    if pct <= 90: return 31
    return 32


def classify_intensity(
    intellectual_load: int = 1,
    signal_density: int | None = None,
    watch_objects: int | None = None,
    optic_pct: float | None = None,
    emotional_load: int = 1,
    mono_elements: int | None = None,
    passive_watch_pct: float | None = None,
) -> int:
    kuts = [
        _kut_intellectual(intellectual_load),
        _kut_emotional(emotional_load),
    ]
    if signal_density is not None:
        kuts.append(_kut_signal_density(signal_density))
    if watch_objects is not None:
        kuts.append(_kut_watch_objects(watch_objects))
    if optic_pct is not None:
        kuts.append(_kut_optic(optic_pct))
    if mono_elements is not None:
        kuts.append(_kut_mono_elements(mono_elements))
    if passive_watch_pct is not None:
        kuts.append(_kut_passive_watch(passive_watch_pct))
    return max(kuts)
