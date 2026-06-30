"""
Ионизирующее излучение — Приложение №19 к Приказу №33н.
"""
from app.calculations.utils import kut_max


def classify_radiation(
    eff_dose_msv: float,
    lens_dose_msv: float | None = None,
    skin_dose_msv: float | None = None,
) -> int:
    """
    eff_dose_msv — эффективная доза мЗв/год
    lens_dose_msv — доза на хрусталик мЗв/год
    skin_dose_msv — доза на кожу/кисти/стопы мЗв/год
    """
    def classify_eff(d: float) -> int:
        if d <= 5:    return 2
        if d <= 10:   return 31
        if d <= 20:   return 32
        if d <= 50:   return 33
        if d <= 100:  return 34
        return 4

    def classify_lens(d: float) -> int:
        if d <= 37.5:  return 2
        if d <= 75:    return 31
        if d <= 150:   return 32
        if d <= 225:   return 33
        if d <= 300:   return 34
        return 4

    def classify_skin(d: float) -> int:
        if d <= 125:   return 2
        if d <= 250:   return 31
        if d <= 500:   return 32
        if d <= 750:   return 33
        if d <= 1000:  return 34
        return 4

    kuts = [classify_eff(eff_dose_msv)]
    if lens_dose_msv is not None:
        kuts.append(classify_lens(lens_dose_msv))
    if skin_dose_msv is not None:
        kuts.append(classify_skin(skin_dose_msv))
    return kut_max(kuts)
