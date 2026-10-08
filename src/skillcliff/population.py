"""Popolazione come struttura di array (un elemento per lavoratore) e demografia."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from skillcliff.config import Config


@dataclass
class Population:
    age: np.ndarray        # int, anni compiuti
    exp: np.ndarray        # int, anni di esperienza s = età - età d'ingresso
    high: np.ndarray       # bool, qualificato
    h: np.ndarray          # float, capitale umano

    def __len__(self) -> int:
        return self.h.size

    def keep(self, mask: np.ndarray) -> None:
        self.age, self.exp, self.high, self.h = (
            self.age[mask], self.exp[mask], self.high[mask], self.h[mask]
        )

    def append(self, other: "Population") -> None:
        self.age = np.concatenate([self.age, other.age])
        self.exp = np.concatenate([self.exp, other.exp])
        self.high = np.concatenate([self.high, other.high])
        self.h = np.concatenate([self.h, other.h])


def entry_age(cfg: Config, high: np.ndarray) -> np.ndarray:
    ea = cfg.population.entry_age
    return np.where(high, ea.high, ea.low).astype(np.int64)


def draw_h0(cfg: Config, high: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """h0 = h0[qualifica] * exp(eps), eps ~ N(-sigma^2/2, sigma^2): rumore a media 1."""
    pc = cfg.population
    base = np.where(high, pc.h0.high, pc.h0.low)
    s = pc.h0_sigma
    return base * np.exp(rng.normal(-0.5 * s * s, s, size=high.size))


def new_entrants(cfg: Config, n: int, rng: np.random.Generator) -> Population:
    high = rng.random(n) < cfg.population.share_high
    return Population(
        age=entry_age(cfg, high),
        exp=np.zeros(n, dtype=np.int64),
        high=high,
        h=draw_h0(cfg, high, rng),
    )


def initial_population(cfg: Config, rng: np.random.Generator) -> Population:
    """Età uniformi sulla carriera di ciascuna qualifica; h viene poi portato a regime dal burn-in."""
    n = cfg.population.N
    pop = new_entrants(cfg, n, rng)
    career = cfg.population.retirement_age - pop.age
    pop.exp = (rng.random(n) * career).astype(np.int64)
    pop.age = pop.age + pop.exp
    return pop


def n_entrants(cfg: Config, n_before: int, n_after_exit: int) -> int:
    """Numero di entranti nell'anno. Stazionario: rimpiazzo uno a uno dei pensionati."""
    if cfg.demography.mode == "stationary":
        return n_before - n_after_exit
    raise NotImplementedError(cfg.demography.mode)
