"""
Световая среда — Приложение №16 к Приказу №33н.
"""


def classify_lighting(e_fact: float, e_norm: float) -> int:
    """
    e_fact — фактическая освещённость лк
    e_norm — нормативная освещённость лк (по СанПиН/СанНиП для данного вида работ)
    """
    if e_norm <= 0:
        return 2
    ratio = e_fact / e_norm
    if ratio >= 1.0:
        return 2
    if ratio >= 0.5:
        return 31
    return 32
