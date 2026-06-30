"""
Биологический фактор — Приложение №9 к Приказу №33н.

Два вида оценки:
1. Микроорганизмы-продуценты (живые клетки, споры, бактериальные препараты):
   по кратности превышения ПДК (ГН 2.2.6.2178-07).
2. Патогенные микроорганизмы: класс назначается по группе патогенности
   (СП 1.3.3118-13) без проведения измерений.
"""

# Группа патогенности → класс условий труда (по позициям в таблице Прил. №9)
_PATHOGEN_GROUP_KUT = {
    1: 4,    # I группа — возбудители особо опасных инфекций
    2: 33,   # II группа — высококонтагиозные эпидемические заболевания
    3: 32,   # III группа — самостоятельные нозологические группы
    4: 31,   # IV группа — условно-патогенные
}


def classify_bio_producer(c_fact: float | None, pdk: float | None) -> int:
    """Микроорганизмы-продуценты по кратности С/ПДК."""
    if not pdk or c_fact is None:
        return 2
    r = c_fact / pdk
    if r <= 1.0:
        return 2
    if r <= 10.0:
        return 31
    if r <= 100.0:
        return 32
    return 33


def classify_bio_pathogen(pathogenicity_group: int) -> int:
    """Патогенные микроорганизмы по группе патогенности (без измерений)."""
    return _PATHOGEN_GROUP_KUT.get(pathogenicity_group, 31)


def classify_bio(
    bio_type: str,                       # "producer" | "pathogen"
    c_fact: float | None = None,
    pdk: float | None = None,
    pathogenicity_group: int | None = None,
) -> int:
    if bio_type == "pathogen":
        return classify_bio_pathogen(pathogenicity_group or 4)
    return classify_bio_producer(c_fact, pdk)
