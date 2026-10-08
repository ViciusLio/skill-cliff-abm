"""Parametri del modello: dataclass immutabili caricate da YAML."""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class ByQual:
    low: float
    high: float


@dataclass(frozen=True)
class PopulationCfg:
    N: int = 5000
    share_high: float = 0.30
    entry_age: ByQual = field(default_factory=lambda: ByQual(20, 25))
    retirement_age: int = 65
    h0: ByQual = field(default_factory=lambda: ByQual(1.0, 1.5))
    h0_sigma: float = 0.20


@dataclass(frozen=True)
class RolesCfg:
    junior_max_exp: int = 5
    senior_min_exp: int = 15


@dataclass(frozen=True)
class MeetingsCfg:
    p: float = 0.6
    kappa: float = 0.20
    beta: float = 0.10
    same_qual: bool = True


@dataclass(frozen=True)
class LearningCfg:
    delta0: float = 0.04
    horizon: float = 50.0
    depreciation: float = 0.012


@dataclass(frozen=True)
class DemographyCfg:
    mode: str = "stationary"


@dataclass(frozen=True)
class AICfg:
    enabled: bool = False
    target: str = "junior"      # junior | senior | qualificati | non_qualificati | complementare
    start: int = 10             # anno (registrato) di introduzione
    g: float = 0.03             # crescita annua della produttività dell'IA A(t)
    phi_max: float = 0.6        # quota massima dei compiti del bersaglio automatizzabile
    theta: float = 0.02         # Y = H * (1 + theta * (A - 1))
    displacement: bool = False  # D13: i junior sostituiti diventano non occupati (invece di incontrare meno)


@dataclass(frozen=True)
class Config:
    seed: int = 20261008
    n_reps: int = 30
    burn_in: int = 120
    T: int = 60
    population: PopulationCfg = field(default_factory=PopulationCfg)
    roles: RolesCfg = field(default_factory=RolesCfg)
    meetings: MeetingsCfg = field(default_factory=MeetingsCfg)
    learning: LearningCfg = field(default_factory=LearningCfg)
    demography: DemographyCfg = field(default_factory=DemographyCfg)
    ai: AICfg = field(default_factory=AICfg)

    def __post_init__(self) -> None:
        p = self.population
        if not 0 <= self.meetings.p <= 1:
            raise ValueError("meetings.p deve stare in [0, 1]")
        if not 0 <= self.learning.depreciation < 1:
            raise ValueError("learning.depreciation deve stare in [0, 1)")
        if self.roles.junior_max_exp > self.roles.senior_min_exp:
            raise ValueError("junior_max_exp non può superare senior_min_exp")
        if max(p.entry_age.low, p.entry_age.high) >= p.retirement_age:
            raise ValueError("età d'ingresso >= età di pensionamento")
        if self.demography.mode not in ("stationary",):
            raise NotImplementedError(f"demography.mode={self.demography.mode!r}")

    @property
    def max_age(self) -> int:
        return self.population.retirement_age

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    def with_overrides(self, overrides: dict[str, Any]) -> "Config":
        """Copia con override in notazione puntata, es. {"meetings.p": 0.0}."""
        d = self.to_dict()
        for key, value in overrides.items():
            node = d
            *path, last = key.split(".")
            for part in path:
                node = node[part]
            if last not in node:
                raise KeyError(f"parametro sconosciuto: {key}")
            node[last] = value
        return from_dict(d)


def _build(cls: type, data: dict[str, Any]) -> Any:
    known = {f.name: f for f in dataclasses.fields(cls)}
    unknown = set(data) - set(known)
    if unknown:
        raise KeyError(f"{cls.__name__}: parametri sconosciuti {sorted(unknown)}")
    kwargs = {}
    for name, value in data.items():
        sub = _NESTED.get((cls, name))
        kwargs[name] = _build(sub, value) if sub is not None else value
    return cls(**kwargs)


_NESTED: dict[tuple[type, str], type] = {
    (Config, "population"): PopulationCfg,
    (Config, "roles"): RolesCfg,
    (Config, "meetings"): MeetingsCfg,
    (Config, "learning"): LearningCfg,
    (Config, "demography"): DemographyCfg,
    (Config, "ai"): AICfg,
    (PopulationCfg, "entry_age"): ByQual,
    (PopulationCfg, "h0"): ByQual,
}


def from_dict(data: dict[str, Any]) -> Config:
    return _build(Config, data)


def load_config(path: str | Path) -> Config:
    with open(path, encoding="utf-8") as fh:
        return from_dict(yaml.safe_load(fh))
