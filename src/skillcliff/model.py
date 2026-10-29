"""Dinamica annuale del modello.

Ordine degli eventi nell'anno t:
  1. invecchiamento (età +1; esperienza +1 e aggiornamento della familiarità con l'IA solo per
     chi era occupato, D19 e D18)
  2. pensionamento (età >= retirement_age)
  3. ingresso dei nuovi junior
  4. incontri junior-senior e apprendimento autonomo, calcolati sullo stesso h (aggiornamento simultaneo)
  5. registrazione delle metriche
"""
from __future__ import annotations

import numpy as np

from skillcliff.ai import make_ai
from skillcliff.config import Config
from skillcliff.learning import autonomous_gains, autonomous_rate, meeting_gains, role_masks
from skillcliff.metrics import SCALARS, by_age, gini, masked_mean
from skillcliff.population import initial_population, n_entrants, new_entrants


class Model:
    def __init__(self, cfg: Config, seed_seq: np.random.SeedSequence, ai=None) -> None:
        self.cfg = cfg
        # Stream separati: le estrazioni demografiche non dipendono da quelle degli incontri.
        # Il quarto stream serve solo all'IA (non occupazione): i primi tre restano identici.
        ss_init, ss_demo, ss_meet, ss_ai = seed_seq.spawn(4)
        self.rng_demo = np.random.default_rng(ss_demo)
        self.rng_meet = np.random.default_rng(ss_meet)
        self.rng_ai = np.random.default_rng(ss_ai)
        # D20: le separazioni dal mentore usano uno stream figlio di `ai`, così gli altri non si spostano.
        self.rng_pair = np.random.default_rng(ss_ai.spawn(1)[0])
        self.pop = initial_population(cfg, np.random.default_rng(ss_init))
        self.next_uid = len(self.pop)
        self.last_meet = None   # esito degli incontri dell'ultimo anno (per le visualizzazioni)
        self.last_dh_aut = None
        self.ai = ai if ai is not None else make_ai(cfg)
        self.t = -cfg.burn_in
        self.gain_prev = 0.0     # E2: guadagno medio dei junior dagli incontri nell'anno precedente
        self.gain_prev_obs = 0.0

    def step(self, record: bool = True) -> dict[str, np.ndarray | float] | None:
        """Un anno di simulazione. Con record=False (burn-in) non calcola le metriche."""
        cfg, pop = self.cfg, self.pop

        # 1-3. demografia
        pop.age += 1
        pop.exp += ~pop.out           # D19: l'esperienza cresce solo lavorando
        self.ai.update_familiarity(self.t, pop.f, ~pop.out)
        n_before = len(pop)
        pop.keep(pop.age < cfg.population.retirement_age)
        n_new = n_entrants(cfg, n_before, len(pop))
        entrants = new_entrants(cfg, n_new, self.rng_demo, self.next_uid)
        entrants.f[:] = self.ai.entrant_familiarity(self.t)
        pop.append(entrants)
        self.next_uid += n_new

        # 4. apprendimento
        junior, senior = role_masks(cfg, pop.exp)
        self.ai.observe(self.t, pop.h, junior, self.gain_prev)     # E2: base, nulla
        self.gain_prev_obs = self.gain_prev
        mods = self.ai.meeting_modifiers(self.t)
        out = self.ai.nonemployed(self.t, junior, pop.high, self.rng_ai, pop.exp)
        seekers = junior if out is None else junior & ~out      # i non occupati non incontrano
        pairs, self.n_pairs_cont = None, 0
        if cfg.meetings.stable_mentor:                            # D20: coppie in corso
            pairs = self._stable_pairs(junior, out)
            seekers = seekers & (pop.mentor < 0)
        meet = meeting_gains(cfg, pop.h, seekers, senior, self.rng_meet, mods, pop.high, pairs)
        if pairs is not None:                                     # i nuovi abbinamenti diventano coppie
            n_cont = pairs[0].size
            pop.mentor[meet.learners[n_cont:]] = pop.uid[meet.partners[n_cont:]]
            self.n_pairs_cont = n_cont
        dh_aut = autonomous_gains(cfg, pop.h, pop.exp)
        dh_tutor, effort = self.ai.tutor(self.t, pop.h, pop.f, junior, senior, pop.high, out)   # E1: base, None
        if effort is not None:                                    # meno sforzo: si riduce solo delta(s)
            delta = autonomous_rate(cfg, pop.exp) + cfg.learning.depreciation
            dh_aut = dh_aut - (1.0 - effort) * delta * pop.h
        if out is not None:                                       # niente apprendimento sul lavoro
            dh_aut[out] = -cfg.learning.depreciation * pop.h[out]
        self.n_out = 0 if out is None else int(out.sum())
        pop.out = np.zeros(len(pop), dtype=bool) if out is None else out
        h_prev = pop.h
        pop.h = h_prev + meet.dh + dh_aut
        if dh_tutor is not None:
            pop.h = pop.h + dh_tutor
        self.last_tutor = dh_tutor

        self.last_meet, self.last_dh_aut, self.last_out = meet, dh_aut, out
        self.gain_prev = float(meet.dh[junior].mean()) if junior.any() else 0.0
        rec = self._record(h_prev, meet, dh_aut, junior, senior) if record else None
        self.t += 1
        return rec

    def _stable_pairs(self, junior: np.ndarray, out: np.ndarray | None) -> tuple[np.ndarray, np.ndarray]:
        """D20: tiene le coppie in cui il junior è ancora junior e occupato, il mentore è ancora in
        servizio e non c'è separazione (probabilità lambda). Ritorna (indici junior, indici mentore)."""
        pop = self.pop
        has = pop.mentor >= 0
        idx = np.minimum(np.searchsorted(pop.uid, pop.mentor), len(pop) - 1)   # uid ordinati
        u = self.rng_pair.random(len(pop))          # estratto per tutti: numeri allineati tra scenari
        keep = has & (pop.uid[idx] == pop.mentor) & junior & (u >= self.cfg.meetings.separation)
        if out is not None:
            keep &= ~out
        pop.mentor[~keep] = -1
        return np.flatnonzero(keep), idx[keep]

    def _record(self, h_prev, meet, dh_aut, junior, senior) -> dict[str, np.ndarray | float]:
        pop, n_ages = self.pop, self.cfg.max_age
        mid = ~junior & ~senior
        users = self.ai.users(junior, senior, pop.high, self.last_out)
        F = self.ai.familiarity_weight(pop.h, pop.f, users)
        w = self.ai.wages(self.t, pop.h, pop.f, users)   # senza IA: salario = prodotto marginale = h
        j = np.flatnonzero(junior)           # tassi di crescita calcolati solo sui junior
        g_meet, g_aut = meet.dh[j] / h_prev[j], dh_aut[j] / h_prev[j]
        rec: dict[str, np.ndarray | float] = {
            "N": len(pop),
            "n_junior": int(junior.sum()),
            "n_mid": int(mid.sum()),
            "n_senior": int(senior.sum()),
            "n_meetings": meet.n_meetings,
            "n_nonemployed": self.n_out,
            "n_pairs": self.n_pairs_cont,
            "p_eff": meet.p_eff,
            "H": float(pop.h.sum()),
            "Y": self.ai.output(self.t, float(pop.h.sum()), F),
            "F_U": F,
            "rent_ai": float(self.ai.output(self.t, float(pop.h.sum()), F) - w.sum()),
            "A": self.ai.productivity(self.t),
            "phi": self.ai.automation_share(self.t),
            "savings": self.ai.savings(self.t, int(junior.sum())),
            "w_firm": self.ai._w_j if getattr(self.ai, "a", None) is not None and self.ai.a.endogenous else 0.0,
            "v_firm": self.ai.training_value(self.gain_prev_obs) if getattr(self.ai, "a", None) is not None and self.ai.a.endogenous else 0.0,
            "mean_h": float(pop.h.mean()),
            "mean_h_junior": masked_mean(pop.h, junior),
            "mean_h_mid": masked_mean(pop.h, mid),
            "mean_h_senior": masked_mean(pop.h, senior),
            "B_meet": float(g_meet.mean()) if j.size else np.nan,
            "B_aut": float(g_aut.mean()) if j.size else np.nan,
            "gini_w": gini(w),
        }
        rec["B_tutor"] = (float((self.last_tutor[j] / h_prev[j]).mean()) if j.size else np.nan) \
            if self.last_tutor is not None else 0.0
        rec["B"] = rec["B_meet"] + rec["B_aut"]
        if self.last_tutor is not None:
            rec["B"] += rec["B_tutor"]
        rec["h_by_age"], rec["n_by_age"] = by_age(pop.h, pop.age, n_ages)
        rec["h_by_age_high"], _ = by_age(pop.h[pop.high], pop.age[pop.high], n_ages)
        rec["h_by_age_low"], _ = by_age(pop.h[~pop.high], pop.age[~pop.high], n_ages)
        return rec


ARRAYS = ("h_by_age", "n_by_age", "h_by_age_high", "h_by_age_low")


def run_model(cfg: Config, seed_seq: np.random.SeedSequence, ai=None) -> dict[str, np.ndarray]:
    """Burn-in e poi T anni registrati. Ritorna serie di lunghezza T (o T x età).

    `ai` sostituisce il modulo IA di default (oggetto con meeting_modifiers, output e nonemployed);
    serve per esperimenti di meccanismo e, nella fase 2, per gli scenari.
    """
    model = Model(cfg, seed_seq, ai)
    for _ in range(cfg.burn_in):
        model.step(record=False)
    records = [model.step() for _ in range(cfg.T)]
    out = {k: np.array([r[k] for r in records], dtype=float) for k in SCALARS + ARRAYS}
    return out
