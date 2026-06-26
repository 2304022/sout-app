"""
Итоговая оценка класса условий труда — Приложение №22 к Приказу №33н.

Правила:
1. Итоговый класс = максимальный среди всех факторов.
2. Если 3 и более фактора с классом 3.1 — итог повышается до 3.2.
3. Если 3 и более фактора с классом 3.2 — итог повышается до 3.3.
4. Аналогично для 3.3 → 3.4.
"""
from app.calculations.utils import KUT_ORDER


def classify_summary(factor_kuts: list[int | None]) -> int:
    """
    factor_kuts — список классов по каждому фактору (None игнорируется).
    Возвращает итоговый класс.
    """
    valid = [k for k in factor_kuts if k is not None]
    if not valid:
        return 1

    result = max(valid)

    # Правило эскалации: 3 и более факторов с одним подклассом
    for base_kut, next_kut in [(31, 32), (32, 33), (33, 34)]:
        count = sum(1 for k in valid if k == base_kut)
        if count >= 3 and result == base_kut:
            result = next_kut

    return result


def kut_display(kut: int) -> str:
    mapping = {1: "1", 2: "2", 31: "3.1", 32: "3.2", 33: "3.3", 34: "3.4", 4: "4"}
    return mapping.get(kut, str(kut))
