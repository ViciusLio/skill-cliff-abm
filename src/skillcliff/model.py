"""Dinamica annuale del modello.

Ordine degli eventi nell'anno t:
  1. invecchiamento (età e esperienza +1)
  2. pensionamento (età >= retirement_age)
  3. ingresso dei nuovi junior
  4. incontri junior-senior e apprendimento autonomo, calcolati sullo stesso h (aggiornamento simultaneo)
  5. registrazione delle metriche
"""
from __future__ import annotations

import numpy as np

from skillcliff.ai import make_ai
from skillcliff.config import Config
from skillcliff.learning import autonomous_gains, meeting_gains, role_masks
from skillcliff.metrics import SCALARS, by_age, gini, masked_mean
from skillcliff.population import initial_population, n_entrants, new_entrants


class Model:
    def __init__(self, cfg: Config, seed_seq: np.random.SeedSequence) -> None:
        self.cfg = cfg
        # Stream separati: le estrazioni demografiche non dipendono da quelle degli incontri.
        ss_init, ss_demo, ss_meet = seed_seq.spawn(3)
        self.rng_demo = np.random.default_rng(ss_demo)
        self.rng_meet = np.random.default_rng(ss_meet)
        self.pop = initial_population(cfg, np.random.default_rng(ss_init))
        self.ai = make_ai(cfg)
        self.t = -cfg.burn_in

    def step(self) -> dict[str, np.ndarray | float]:
        cfg, pop = self.cfg, self.pop

        # 1-3. demografia
        pop.age += 1
        pop.exp += 1
        n_before = len(pop)
        pop.keep(pop.age < cfg.population.retirement_age)
        n_new = n_entrants(cfg, n_before, len(pop))
        pop.append(new_entrants(cfg, n_new, self.rng_demo))

        # 4. apprendimento
        junior, senior = role_masks(cfg, pop.exp)
        p_mult, beta_mult = self.ai.meeting_multipliers(self.t)
        meet = meeting_gains(cfg, pop.h, junior, senior, self.rng_meet, p_mult, beta_mult)
        dh_aut = autonomous_gains(cfg, pop.h, pop.exp)
        h_prev = pop.h
        pop.h = h_prev + meet.dh + dh_aut

        rec = self._record(h_prev, meet, dh_aut, junior, senior)
        self.t += 1
        return rec

    def _record(self, h_prev, meet, dh_aut, junior, senior) -> dict[str, np.ndarray | float]:
        pop, n_ages = self.pop, self.cfg.max_age
        mid = ~junior & ~senior
        w = pop.h  # salario = prodotto marginale = h (Y lineare)
        g_meet, g_aut = meet.dh / h_prev, dh_aut / h_prev
        rec: dict[str, np.ndarray | float] = {
            "N": len(pop),
            "n_junior": int(junior.sum()),
            "n_mid": int(mid.sum()),
            "n_senior": int(senior.sum()),
            "n_meetings": meet.n_meetings,
            "p_eff": meet.p_eff,
            "Y": self.ai.output(self.t, float(pop.h.sum())),
            "mean_h": float(pop.h.mean()),
            "mean_h_junior": masked_mean(pop.h, junior),
            "mean_h_mid": masked_mean(pop.h, mid),
            "mean_h_senior": masked_mean(pop.h, senior),
            "B_meet": masked_mean(g_meet, junior),
            "B_aut": masked_mean(g_aut, junior),
            "gini_w": gini(w),
        }
        rec["B"] = rec["B_meet"] + rec["B_aut"]
        rec["h_by_age"], rec["n_by_age"] = by_age(pop.h, pop.age, n_ages)
        rec["h_by_age_high"], _ = by_age(pop.h[pop.high], pop.age[pop.high], n_ages)
        rec["h_by_age_low"], _ = by_age(pop.h[~pop.high], pop.age[~pop.high], n_ages)
        return rec


ARRAYS = ("h_by_age", "n_by_age", "h_by_age_high", "h_by_age_low")


def run_model(cfg: Config, seed_seq: np.random.SeedSequence) -> dict[str, np.ndarray]:
    """Burn-in e poi T anni registrati. Ritorna serie di lunghezza T (o T x età)."""
    model = Model(cfg, seed_seq)
    for _ in range(cfg.burn_in):
        model.step()
    records = [model.step() for _ in range(cfg.T)]
    out = {k: np.array([r[k] for r in records], dtype=float) for k in SCALARS + ARRAYS}
    return out
