from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Organization(Base):
    __tablename__ = "organizations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    inn: Mapped[str | None] = mapped_column(String(12))
    address: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    workplaces: Mapped[list["Workplace"]] = relationship(back_populates="org", cascade="all, delete-orphan")


class Workplace(Base):
    __tablename__ = "workplaces"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    podr: Mapped[str | None] = mapped_column(String(500))
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    profession: Mapped[str | None] = mapped_column(String(300))
    num_workers: Mapped[int] = mapped_column(Integer, default=1)
    shift_hours: Mapped[float] = mapped_column(Float, default=8.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    org: Mapped["Organization"] = relationship(back_populates="workplaces")
    chemicals: Mapped[list["MeasChemical"]] = relationship(back_populates="rm", cascade="all, delete-orphan")
    apfds: Mapped[list["MeasAPFD"]] = relationship(back_populates="rm", cascade="all, delete-orphan")
    noises: Mapped[list["MeasNoise"]] = relationship(back_populates="rm", cascade="all, delete-orphan")
    vibr_locals: Mapped[list["MeasVibrLocal"]] = relationship(back_populates="rm", cascade="all, delete-orphan")
    vibr_generals: Mapped[list["MeasVibrGeneral"]] = relationship(back_populates="rm", cascade="all, delete-orphan")
    infrasounds: Mapped[list["MeasInfrasound"]] = relationship(back_populates="rm", cascade="all, delete-orphan")
    ultrasounds: Mapped[list["MeasUltrasound"]] = relationship(back_populates="rm", cascade="all, delete-orphan")
    microclimates: Mapped[list["MeasMicroclimate"]] = relationship(back_populates="rm", cascade="all, delete-orphan")
    lightings: Mapped[list["MeasLighting"]] = relationship(back_populates="rm", cascade="all, delete-orphan")
    emfs: Mapped[list["MeasEMF"]] = relationship(back_populates="rm", cascade="all, delete-orphan")
    radiations: Mapped[list["MeasRadiation"]] = relationship(back_populates="rm", cascade="all, delete-orphan")
    heavinesses: Mapped[list["MeasHeaviness"]] = relationship(back_populates="rm", cascade="all, delete-orphan")
    intensities: Mapped[list["MeasIntensity"]] = relationship(back_populates="rm", cascade="all, delete-orphan")
    summary: Mapped["Summary | None"] = relationship(back_populates="rm", cascade="all, delete-orphan")


class MeasChemical(Base):
    __tablename__ = "meas_chemical"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rm_id: Mapped[int] = mapped_column(ForeignKey("workplaces.id"))
    substance_name: Mapped[str] = mapped_column(String(300))
    pdk_ss: Mapped[float | None] = mapped_column(Float)      # среднесменная ПДК
    pdk_max: Mapped[float | None] = mapped_column(Float)     # максимальная ПДК
    danger_class: Mapped[int] = mapped_column(Integer, default=3)  # 1-4
    is_carcinogen: Mapped[bool] = mapped_column(Boolean, default=False)
    is_allergen_high: Mapped[bool] = mapped_column(Boolean, default=False)
    is_allergen_mod: Mapped[bool] = mapped_column(Boolean, default=False)
    is_irritant: Mapped[bool] = mapped_column(Boolean, default=False)
    is_directed: Mapped[bool] = mapped_column(Boolean, default=False)   # остронаправленного действия
    is_repro: Mapped[bool] = mapped_column(Boolean, default=False)      # репротоксикант
    is_antitumor: Mapped[bool] = mapped_column(Boolean, default=False)  # противоопухолевые/гормоны
    c_ss: Mapped[float | None] = mapped_column(Float)    # факт. среднесменная
    c_max: Mapped[float | None] = mapped_column(Float)   # факт. максимальная
    kut: Mapped[int | None] = mapped_column(Integer)
    rm: Mapped["Workplace"] = relationship(back_populates="chemicals")


class MeasAPFD(Base):
    __tablename__ = "meas_apfd"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rm_id: Mapped[int] = mapped_column(ForeignKey("workplaces.id"))
    substance_name: Mapped[str] = mapped_column(String(300))
    pdk_ss: Mapped[float] = mapped_column(Float)         # ПДКсс мг/м³
    fibrogenicity: Mapped[str] = mapped_column(String(10), default="high")  # high/moderate/low
    c_fact: Mapped[float] = mapped_column(Float)          # факт. концентрация мг/м³
    # пылевая нагрузка
    work_years: Mapped[float] = mapped_column(Float, default=25.0)   # нормируемый стаж лет
    shifts_per_year: Mapped[int] = mapped_column(Integer, default=247)
    kpn: Mapped[float | None] = mapped_column(Float)     # контрольная ПН (calculated)
    pn_fact: Mapped[float | None] = mapped_column(Float) # фактич. ПН (calculated)
    kut: Mapped[int | None] = mapped_column(Integer)
    rm: Mapped["Workplace"] = relationship(back_populates="apfds")


class MeasNoise(Base):
    __tablename__ = "meas_noise"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rm_id: Mapped[int] = mapped_column(ForeignKey("workplaces.id"))
    leq_dba: Mapped[float] = mapped_column(Float)   # эквивалентный уровень дБА
    lpeak_dbc: Mapped[float | None] = mapped_column(Float)  # пиковый дБС
    kut: Mapped[int | None] = mapped_column(Integer)
    rm: Mapped["Workplace"] = relationship(back_populates="noises")


class MeasVibrLocal(Base):
    __tablename__ = "meas_vibr_local"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rm_id: Mapped[int] = mapped_column(ForeignKey("workplaces.id"))
    corr_level_db: Mapped[float] = mapped_column(Float)  # корректированный уровень дБ
    kut: Mapped[int | None] = mapped_column(Integer)
    rm: Mapped["Workplace"] = relationship(back_populates="vibr_locals")


class MeasVibrGeneral(Base):
    __tablename__ = "meas_vibr_general"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rm_id: Mapped[int] = mapped_column(ForeignKey("workplaces.id"))
    axis: Mapped[str] = mapped_column(String(2), default="Z")  # Z, X, Y
    corr_level_db: Mapped[float] = mapped_column(Float)
    kut: Mapped[int | None] = mapped_column(Integer)
    rm: Mapped["Workplace"] = relationship(back_populates="vibr_generals")


class MeasInfrasound(Base):
    __tablename__ = "meas_infrasound"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rm_id: Mapped[int] = mapped_column(ForeignKey("workplaces.id"))
    level_db_lin: Mapped[float] = mapped_column(Float)  # уровень дБЛин
    kut: Mapped[int | None] = mapped_column(Integer)
    rm: Mapped["Workplace"] = relationship(back_populates="infrasounds")


class MeasUltrasound(Base):
    __tablename__ = "meas_ultrasound"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rm_id: Mapped[int] = mapped_column(ForeignKey("workplaces.id"))
    excess_db: Mapped[float] = mapped_column(Float)  # превышение над ПДУ в дБ
    kut: Mapped[int | None] = mapped_column(Integer)
    rm: Mapped["Workplace"] = relationship(back_populates="ultrasounds")


class MeasMicroclimate(Base):
    __tablename__ = "meas_microclimate"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rm_id: Mapped[int] = mapped_column(ForeignKey("workplaces.id"))
    season: Mapped[str] = mapped_column(String(10), default="warm")   # warm/cold
    mode: Mapped[str] = mapped_column(String(10), default="heating")  # heating/cooling
    work_category: Mapped[str] = mapped_column(String(5), default="IIa")  # Ia Ib IIa IIb III
    tns_index: Mapped[float | None] = mapped_column(Float)   # ТНС °С (нагрев)
    air_temp: Mapped[float | None] = mapped_column(Float)    # температура °С (охлаждение)
    air_speed: Mapped[float | None] = mapped_column(Float)   # скорость воздуха м/с
    humidity: Mapped[float | None] = mapped_column(Float)    # влажность %
    radiant_heat: Mapped[float | None] = mapped_column(Float)  # тепловое излучение Вт/м²
    kut: Mapped[int | None] = mapped_column(Integer)
    rm: Mapped["Workplace"] = relationship(back_populates="microclimates")


class MeasLighting(Base):
    __tablename__ = "meas_lighting"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rm_id: Mapped[int] = mapped_column(ForeignKey("workplaces.id"))
    e_fact: Mapped[float] = mapped_column(Float)   # фактическая освещённость лк
    e_norm: Mapped[float] = mapped_column(Float)   # нормативная освещённость лк
    kut: Mapped[int | None] = mapped_column(Integer)
    rm: Mapped["Workplace"] = relationship(back_populates="lightings")


class MeasEMF(Base):
    __tablename__ = "meas_emf"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rm_id: Mapped[int] = mapped_column(ForeignKey("workplaces.id"))
    emf_type: Mapped[str] = mapped_column(String(30))  # esp/pmp/emp50/emp_rd/ufi/rf01/rf03/rf30/rf300
    fact_value: Mapped[float] = mapped_column(Float)
    pdu_value: Mapped[float] = mapped_column(Float)
    kut: Mapped[int | None] = mapped_column(Integer)
    rm: Mapped["Workplace"] = relationship(back_populates="emfs")


class MeasRadiation(Base):
    __tablename__ = "meas_radiation"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rm_id: Mapped[int] = mapped_column(ForeignKey("workplaces.id"))
    eff_dose_msv: Mapped[float] = mapped_column(Float)   # эффективная доза мЗв/год
    lens_dose_msv: Mapped[float | None] = mapped_column(Float)   # доза хрусталик
    skin_dose_msv: Mapped[float | None] = mapped_column(Float)   # доза кожа/кисти
    kut: Mapped[int | None] = mapped_column(Integer)
    rm: Mapped["Workplace"] = relationship(back_populates="radiations")


class MeasHeaviness(Base):
    __tablename__ = "meas_heaviness"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rm_id: Mapped[int] = mapped_column(ForeignKey("workplaces.id"))
    sex: Mapped[str] = mapped_column(String(1), default="m")  # m/f
    # физическая динамическая нагрузка кг·м/смену
    load_regional_1m: Mapped[float | None] = mapped_column(Float)   # региональная до 1 м
    load_general_1_5m: Mapped[float | None] = mapped_column(Float)  # общая 1-5 м
    load_general_5m: Mapped[float | None] = mapped_column(Float)    # общая > 5 м
    # масса груза кг
    mass_rare: Mapped[float | None] = mapped_column(Float)     # разово до 2 раз/час
    mass_frequent: Mapped[float | None] = mapped_column(Float) # постоянно > 2 раз/час
    # суммарная масса за смену кг
    mass_total_floor: Mapped[float | None] = mapped_column(Float)   # с пола
    mass_total_bench: Mapped[float | None] = mapped_column(Float)   # с рабочей поверхности
    # рабочая поза (% смены стоя/на корточках)
    pose_standing_pct: Mapped[float | None] = mapped_column(Float)
    pose_awkward_pct: Mapped[float | None] = mapped_column(Float)
    # наклоны корпуса (>30°) кол/смену
    bends_count: Mapped[int | None] = mapped_column(Integer)
    # перемещения км/смену
    moves_horizontal_km: Mapped[float | None] = mapped_column(Float)
    kut: Mapped[int | None] = mapped_column(Integer)
    rm: Mapped["Workplace"] = relationship(back_populates="heavinesses")


class MeasIntensity(Base):
    __tablename__ = "meas_intensity"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rm_id: Mapped[int] = mapped_column(ForeignKey("workplaces.id"))
    # интеллектуальные нагрузки
    intellectual_load: Mapped[int] = mapped_column(Integer, default=1)  # 1-4
    # сенсорные нагрузки
    signal_density: Mapped[int | None] = mapped_column(Integer)     # сигналов/час
    watch_objects: Mapped[int | None] = mapped_column(Integer)      # объектов наблюдения
    optic_pct: Mapped[float | None] = mapped_column(Float)          # работа с оптикой % смены
    # эмоциональные
    emotional_load: Mapped[int] = mapped_column(Integer, default=1)  # 1-4
    # монотонность
    mono_elements: Mapped[int | None] = mapped_column(Integer)       # кол. элементов простой операции
    passive_watch_pct: Mapped[float | None] = mapped_column(Float)   # пассивное наблюдение % смены
    kut: Mapped[int | None] = mapped_column(Integer)
    rm: Mapped["Workplace"] = relationship(back_populates="intensities")


class Summary(Base):
    __tablename__ = "summary"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rm_id: Mapped[int] = mapped_column(ForeignKey("workplaces.id"), unique=True)
    kut_chemical: Mapped[int | None] = mapped_column(Integer)
    kut_apfd: Mapped[int | None] = mapped_column(Integer)
    kut_noise: Mapped[int | None] = mapped_column(Integer)
    kut_vibr_local: Mapped[int | None] = mapped_column(Integer)
    kut_vibr_general: Mapped[int | None] = mapped_column(Integer)
    kut_infrasound: Mapped[int | None] = mapped_column(Integer)
    kut_ultrasound: Mapped[int | None] = mapped_column(Integer)
    kut_microclimate: Mapped[int | None] = mapped_column(Integer)
    kut_lighting: Mapped[int | None] = mapped_column(Integer)
    kut_emf: Mapped[int | None] = mapped_column(Integer)
    kut_radiation: Mapped[int | None] = mapped_column(Integer)
    kut_heaviness: Mapped[int | None] = mapped_column(Integer)
    kut_intensity: Mapped[int | None] = mapped_column(Integer)
    kut_final: Mapped[int | None] = mapped_column(Integer)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    rm: Mapped["Workplace"] = relationship(back_populates="summary")
