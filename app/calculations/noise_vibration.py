"""
Шум, вибрация, инфразвук, ультразвук — Приложение №11 к Приказу №33н.
"""


def classify_noise(leq_dba: float) -> int:
    """Шум по эквивалентному уровню дБА."""
    if leq_dba <= 80:
        return 2
    if leq_dba <= 85:
        return 31
    if leq_dba <= 95:
        return 32
    if leq_dba <= 105:
        return 33
    if leq_dba <= 115:
        return 34
    return 4


def classify_vibr_local(corr_db: float) -> int:
    """Локальная вибрация по корректированному уровню дБ."""
    if corr_db <= 126:
        return 2
    if corr_db <= 129:
        return 31
    if corr_db <= 132:
        return 32
    if corr_db <= 135:
        return 33
    if corr_db <= 138:
        return 34
    return 4


def classify_vibr_general(corr_db: float, axis: str = "Z") -> int:
    """Общая вибрация. Ось Z имеет более жёсткий норматив."""
    if axis.upper() == "Z":
        if corr_db <= 115:
            return 2
        if corr_db <= 121:
            return 31
        if corr_db <= 127:
            return 32
        if corr_db <= 133:
            return 33
        if corr_db <= 139:
            return 34
        return 4
    else:  # X, Y
        if corr_db <= 112:
            return 2
        if corr_db <= 118:
            return 31
        if corr_db <= 124:
            return 32
        if corr_db <= 130:
            return 33
        if corr_db <= 136:
            return 34
        return 4


def classify_infrasound(level_db_lin: float) -> int:
    """Инфразвук по суммарному уровню дБЛин."""
    if level_db_lin <= 110:
        return 2
    if level_db_lin <= 115:
        return 31
    if level_db_lin <= 120:
        return 32
    if level_db_lin <= 125:
        return 33
    if level_db_lin <= 130:
        return 34
    return 4


def classify_ultrasound(excess_db: float) -> int:
    """
    Ультразвук воздушный.
    excess_db — превышение фактического уровня над ПДУ в дБ.
    """
    if excess_db <= 0:
        return 2
    if excess_db <= 10:
        return 31
    if excess_db <= 20:
        return 32
    if excess_db <= 30:
        return 33
    if excess_db <= 40:
        return 34
    return 4
