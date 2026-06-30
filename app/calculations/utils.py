"""Shared utilities for classification."""

# Encoding: integer class codes
# 1=оптимальный, 2=допустимый, 31=3.1, 32=3.2, 33=3.3, 34=3.4, 4=опасный

KUT_LABELS = {
    1: "1 (оптимальный)",
    2: "2 (допустимый)",
    31: "3.1 (вредный)",
    32: "3.2 (вредный)",
    33: "3.3 (вредный)",
    34: "3.4 (вредный)",
    4: "4 (опасный)",
}

KUT_ORDER = [1, 2, 31, 32, 33, 34, 4]


def kut_severity(kut: int | None) -> int:
    """Ранг тяжести класса (по KUT_ORDER). None → -1."""
    if kut is None:
        return -1
    try:
        return KUT_ORDER.index(kut)
    except ValueError:
        return -1


def kut_max(kuts) -> int | None:
    """Наиболее тяжёлый класс из списка (учитывает, что 4 хуже 3.4).
    None-значения игнорируются; пустой/нулевой список → None."""
    valid = [k for k in kuts if k is not None]
    if not valid:
        return None
    return max(valid, key=kut_severity)


def kut_label(kut: int | None) -> str:
    if kut is None:
        return "—"
    return KUT_LABELS.get(kut, str(kut))


def kut_next(kut: int) -> int:
    """Return the next higher class."""
    idx = KUT_ORDER.index(kut)
    if idx < len(KUT_ORDER) - 1:
        return KUT_ORDER[idx + 1]
    return kut


def ratio_to_kut(ratio: float, thresholds: list[tuple[float, int]]) -> int:
    """
    Map a ratio (fact/norm) to a class given sorted thresholds.
    thresholds: list of (upper_bound_exclusive, kut) from lowest class upward.
    If ratio <= upper_bound the class is returned.
    Last entry's upper_bound is math.inf.
    """
    for upper, klass in thresholds:
        if ratio <= upper:
            return klass
    return thresholds[-1][1]
