"""Gemello Mesa del modello base, usato solo per il docking (Axtell et al., 1996).

Implementa le stesse regole di model.py con un oggetto per agente e cicli espliciti,
in modo indipendente dal codice vettorizzato. I due modelli NON condividono i flussi
di numeri casuali: il confronto è statistico (distribuzioni tra repliche), non esatto.
"""
from __future__ import annotations

import math

import mesa
import numpy as np

from skillcliff.config import Config


class Worker(mesa.Agent):
    def __init__(self, model: "MesaSkillModel", high: bool, exp: int) -> None:
        super().__init__(model)
        pc = model.cfg.population
        self.high = high
        self.exp = exp
        self.age = (pc.entry_age.high if high else pc.entry_age.low) + exp
        s = pc.h0_sigma
        base = pc.h0.high if high else pc.h0.low
        self.h = base * math.exp(model.rng.normal(-0.5 * s * s, s))
        self.dh = 0.0

    def age_one_year(self) -> None:
        self.age += 1
        self.exp += 1

    def learn_autonomously(self) -> None:
        lc = self.model.cfg.learning
        delta = lc.delta0 * max(0.0, 1.0 - self.exp / lc.horizon)
        self.dh += (delta - lc.depreciation) * self.h


class MesaSkillModel(mesa.Model):
    def __init__(self, cfg: Config, seed: int) -> None:
        super().__init__(rng=seed)
        self.cfg = cfg
        pc = cfg.population
        for _ in range(pc.N):
            high = bool(self.rng.random() < pc.share_high)
            career = pc.retirement_age - (pc.entry_age.high if high else pc.entry_age.low)
            Worker(self, high, int(self.rng.random() * career))
        self.history: list[dict[str, float]] = []

    def step(self) -> None:
        cfg = self.cfg
        # 1-3. demografia
        self.agents.do("age_one_year")
        retiring = [a for a in self.agents if a.age >= cfg.population.retirement_age]
        for a in retiring:
            a.remove()
        for _ in range(len(retiring)):
            Worker(self, bool(self.rng.random() < cfg.population.share_high), 0)

        # 4. apprendimento (dh calcolati sullo stesso h, poi applicati)
        workers = list(self.agents)
        for a in workers:
            a.dh = 0.0
        juniors = [a for a in workers if a.exp < cfg.roles.junior_max_exp]
        seniors = [a for a in workers if a.exp >= cfg.roles.senior_min_exp]
        m = cfg.meetings
        # Con same_qual i junior incontrano senior della propria qualifica, con capacità per gruppo.
        quals = (False, True) if m.same_qual else (None,)
        meet_gain = 0.0
        for q in quals:
            js = [a for a in juniors if q is None or a.high == q]
            ss = [a for a in seniors if q is None or a.high == q]
            p_eff = min(m.p, m.kappa * len(ss) / len(js)) if js and ss else 0.0
            for j in js:
                if self.rng.random() < p_eff:
                    s = ss[int(self.rng.integers(len(ss)))]
                    gain = m.beta * max(0.0, s.h - j.h)
                    j.dh += gain
                    meet_gain += gain / j.h
        aut_gain = 0.0
        for a in workers:
            before = a.dh
            a.learn_autonomously()
            if a.exp < cfg.roles.junior_max_exp:
                aut_gain += (a.dh - before) / a.h
        for a in workers:
            a.h += a.dh

        hs = np.array([a.h for a in workers])
        self.history.append({
            "N": len(workers),
            "mean_h": float(hs.mean()),
            "mean_h_junior": float(np.mean([a.h for a in juniors])),
            "mean_h_senior": float(np.mean([a.h for a in seniors])),
            "B_meet": meet_gain / len(juniors),
            "B_aut": aut_gain / len(juniors),
        })


def run_mesa(cfg: Config, seed: int) -> dict[str, np.ndarray]:
    model = MesaSkillModel(cfg, seed)
    for _ in range(cfg.burn_in + cfg.T):
        model.step()
    rec = model.history[cfg.burn_in:]
    return {k: np.array([r[k] for r in rec]) for k in rec[0]}
