"""
Аэроионный состав воздуха.

В Приказе №33н отдельного приложения нет; оценка ведётся по
СанПиН 2.2.4.1294-03 / Р 2.2.2006-05:
  - концентрация положительных аэроионов ρ⁺: 400 … 50 000 ион/см³;
  - концентрация отрицательных аэроионов ρ⁻: 600 … 50 000 ион/см³;
  - коэффициент униполярности Y = ρ⁺/ρ⁻: 0,4 … < 1,0.
Соответствие нормам → класс 2, любое отклонение → класс 3.1.
"""

RO_POS_MIN, RO_POS_MAX = 400.0, 50000.0
RO_NEG_MIN, RO_NEG_MAX = 600.0, 50000.0
Y_MIN, Y_MAX = 0.4, 1.0


def calc_unipolarity(ro_pos: float, ro_neg: float) -> float | None:
    """Коэффициент униполярности Y = ρ⁺/ρ⁻."""
    if not ro_neg:
        return None
    return ro_pos / ro_neg


def classify_aeroion(ro_pos: float, ro_neg: float) -> int:
    """ρ⁺, ρ⁻ — концентрации аэроионов, ион/см³."""
    in_norm = (
        RO_POS_MIN <= ro_pos <= RO_POS_MAX
        and RO_NEG_MIN <= ro_neg <= RO_NEG_MAX
    )
    y = calc_unipolarity(ro_pos, ro_neg)
    if y is not None:
        in_norm = in_norm and (Y_MIN <= y < Y_MAX)
    return 2 if in_norm else 31
