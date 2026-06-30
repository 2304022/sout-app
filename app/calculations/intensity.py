"""
Напряжённость трудового процесса — Приложение №21 к Приказу №33н.
Источник порогов: tin3.mdb → napr.
"""


def _level_to_kut(level: int) -> int:
    """Качественные показатели на 4-балльной шкале → класс."""
    if level <= 1: return 1
    if level <= 2: return 2
    if level <= 3: return 31
    return 32


def _kut_concentration_pct(pct: float) -> int:
    """2.1. Длительность сосредоточенного наблюдения, % смены."""
    if pct <= 25: return 1
    if pct <= 50: return 2
    if pct <= 75: return 31
    return 32


def _kut_signal_density(per_hour: int) -> int:
    """2.2. Плотность сигналов (световых, звуковых), ед./час."""
    if per_hour <= 75:  return 1
    if per_hour <= 175: return 2
    if per_hour <= 300: return 31
    return 32


def _kut_watch_objects(count: int) -> int:
    """2.3. Число объектов одновременного наблюдения."""
    if count <= 5:  return 1
    if count <= 10: return 2
    if count <= 25: return 31
    return 32


def _kut_optic(pct: float) -> int:
    """2.5. Работа с оптическими приборами, % смены."""
    if pct <= 25: return 1
    if pct <= 50: return 2
    if pct <= 75: return 31
    return 32


def _kut_voice_hours(hours_per_week: float) -> int:
    """2.8. Нагрузка на голосовой аппарат, суммарных часов в неделю."""
    if hours_per_week < 16: return 1
    if hours_per_week <= 20: return 2
    if hours_per_week <= 25: return 31
    return 32


def _kut_conflicts(count: int) -> int:
    """3.4. Количество конфликтных ситуаций за смену."""
    if count == 0:  return 1
    if count <= 3:  return 2
    if count <= 8:  return 31
    return 32


def _kut_mono_elements(count: int) -> int:
    """4.1. Число элементов (приемов) в простой повторяющейся операции."""
    if count > 10: return 1
    if count >= 6: return 2
    if count >= 3: return 31
    return 32


def _kut_operation_duration(seconds: int) -> int:
    """4.2. Продолжительность выполнения простых заданий, сек."""
    if seconds > 100: return 1
    if seconds >= 25: return 2
    if seconds >= 10: return 31
    return 32


def _kut_active_actions_pct(pct: float) -> int:
    """4.3. Время активных действий, % смены (остальное — пассивное наблюдение)."""
    if pct >= 20: return 1
    if pct >= 10: return 2
    if pct >= 5:  return 31
    return 32


def _kut_passive_watch(pct: float) -> int:
    """4.4. Монотонность: пассивное наблюдение за техпроцессом, % смены."""
    if pct < 75:  return 1
    if pct <= 80: return 2
    if pct <= 90: return 31
    return 32


def _kut_shift_duration(hours: float) -> int:
    """5.1. Фактическая продолжительность рабочего дня, ч."""
    if hours <= 7:  return 1
    if hours <= 9:  return 2
    if hours <= 12: return 31
    return 32


def classify_intensity(
    intellectual_load: int = 1,       # 1.1 содержание работы (1-4)
    perception_load: int = 1,          # 1.2 восприятие сигналов (1-4)
    work_distribution: int = 1,        # 1.3 распределение функций (1-4)
    work_nature: int = 1,              # 1.4 характер выполняемой работы (1-4)
    concentration_pct: float | None = None,  # 2.1 % смены сосредоточенного наблюдения
    signal_density: int | None = None,       # 2.2 сигналов/час
    watch_objects: int | None = None,        # 2.3 объектов наблюдения
    optic_pct: float | None = None,          # 2.5 % смены с оптикой
    voice_hours_week: float | None = None,   # 2.8 часов в неделю голос. нагрузки
    emotional_load: int = 1,                 # 3.1 ответственность (1-4)
    life_risk: bool = False,                 # 3.2 риск для жизни
    others_safety: bool = False,             # 3.3 ответственность за безопасность других
    conflicts_per_shift: int | None = None,  # 3.4 конфликтных ситуаций за смену
    mono_elements: int | None = None,        # 4.1 элементов операции
    operation_duration_sec: int | None = None,  # 4.2 длительность операции, сек
    active_actions_pct: float | None = None,    # 4.3 активные действия, % смены
    passive_watch_pct: float | None = None,     # 4.4 пассивное наблюдение, % смены
    shift_duration_hours: float | None = None,  # 5.1 длительность смены, ч
    shift_type: int = 1,               # 5.2 сменность (1=однсм, 2=двусм, 3=трёхсм с ночью, 4=нерегул.)
    break_adequacy: int = 1,           # 5.3 наличие и достаточность перерывов (1-4)
) -> int:
    kuts = [
        _level_to_kut(intellectual_load),
        _level_to_kut(perception_load),
        _level_to_kut(work_distribution),
        _level_to_kut(work_nature),
        _level_to_kut(emotional_load),
        _level_to_kut(shift_type),
        _level_to_kut(break_adequacy),
    ]
    if concentration_pct is not None:
        kuts.append(_kut_concentration_pct(concentration_pct))
    if signal_density is not None:
        kuts.append(_kut_signal_density(signal_density))
    if watch_objects is not None:
        kuts.append(_kut_watch_objects(watch_objects))
    if optic_pct is not None:
        kuts.append(_kut_optic(optic_pct))
    if voice_hours_week is not None:
        kuts.append(_kut_voice_hours(voice_hours_week))
    if life_risk:
        kuts.append(32)
    if others_safety:
        kuts.append(32)
    if conflicts_per_shift is not None:
        kuts.append(_kut_conflicts(conflicts_per_shift))
    if mono_elements is not None:
        kuts.append(_kut_mono_elements(mono_elements))
    if operation_duration_sec is not None:
        kuts.append(_kut_operation_duration(operation_duration_sec))
    if active_actions_pct is not None:
        kuts.append(_kut_active_actions_pct(active_actions_pct))
    if passive_watch_pct is not None:
        kuts.append(_kut_passive_watch(passive_watch_pct))
    if shift_duration_hours is not None:
        kuts.append(_kut_shift_duration(shift_duration_hours))
    return max(kuts)
