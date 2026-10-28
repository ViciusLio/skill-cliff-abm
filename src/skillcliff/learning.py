"""Regole di apprendimento: incontri junior-senior e apprendimento autonomo."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from skillcliff.config import Config


def role_masks(cfg: Config, exp: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    junior = exp < cfg.roles.junior_max_exp
    senior = exp >= cfg.roles.senior_min_exp
    return junior, senior


def effective_meeting_prob(p: float, kappa: float, n_junior: int, n_senior: int, occupied: int = 0) -> float:
    """p_eff = min(p, kappa * S / J).

    Incontri = min(domanda p*J, capacità kappa*S): ogni senior può seguire al massimo
    kappa junior l'anno; se la capacità non basta, gli incontri sono razionati tra i junior.
    Con il mentore stabile (D20) le coppie in corso occupano `occupied` posti di capacità.
    """
    if n_junior == 0 or n_senior == 0:
        return 0.0
    if occupied:
        return min(p, max(0.0, kappa * n_senior - occupied) / n_junior)
    return min(p, kappa * n_senior / n_junior)


@dataclass
class MeetingOutcome:
    dh: np.ndarray          # guadagno per ciascun lavoratore (zero per i non junior)
    n_meetings: int
    p_eff: float
    learners: np.ndarray    # indici dei junior che hanno incontrato un senior
    partners: np.ndarray    # indici dei senior incontrati (stesso ordine)


def meeting_gains(
    cfg: Config,
    h: np.ndarray,
    junior: np.ndarray,
    senior: np.ndarray,
    rng: np.random.Generator,
    mods=None,
    high: np.ndarray | None = None,
    pairs: tuple[np.ndarray, np.ndarray] | None = None,
) -> MeetingOutcome:
    """dh_j = beta * max(0, h_s - h_j) per i junior che incontrano un senior estratto a caso.

    Con meetings.same_qual il senior è estratto tra quelli della stessa qualifica del junior
    (si impara da chi fa il proprio mestiere) e il vincolo di capacità vale per gruppo:
    p_eff_g = min(p, kappa * S_g / J_g). Altrimenti l'estrazione è sull'intero pool.

    I numeri casuali vengono estratti per tutti i junior a prescindere da p, così due
    scenari con lo stesso seed restano accoppiati (common random numbers): un incontro
    che avviene con p più basso avviene anche con p più alto.
    mods (MeetingModifiers) moltiplica p, kappa e beta per gruppo di qualifica: è l'aggancio
    dell'IA (fase 2) e degli esperimenti di meccanismo.
    pairs (D20) = (junior, mentore) delle coppie stabili in corso: i junior abbinati imparano dal
    proprio mentore e non cercano; le coppie occupano capacità; `junior` sono solo quelli che cercano.
    """
    m = cfg.meetings
    p_mult, k_mult, b_mult = (mods.p, mods.kappa, mods.beta) if mods is not None else ((1.0, 1.0),) * 3
    j_idx = np.flatnonzero(junior)
    u = rng.random(j_idx.size)
    partner_draw = rng.random(j_idx.size)
    if m.same_qual:
        if high is None:
            raise ValueError("meetings.same_qual richiede la qualifica dei lavoratori")
        groups = [(0, ~high[j_idx], np.flatnonzero(senior & ~high)), (1, high[j_idx], np.flatnonzero(senior & high))]
    else:
        groups = [(0, np.ones(j_idx.size, dtype=bool), np.flatnonzero(senior))]

    dh = np.zeros_like(h)
    learners, partners, p_weighted = [], [], 0.0
    if pairs is not None and pairs[0].size:
        pj, ps = pairs
        g_pair = high[pj].astype(np.int64) if m.same_qual else np.zeros(pj.size, dtype=np.int64)
        b_pair = np.where(g_pair == 1, b_mult[1], b_mult[0])
        dh[pj] = m.beta * b_pair * np.maximum(0.0, h[ps] - h[pj])
        learners.append(pj)
        partners.append(ps)
        occupied = np.bincount(g_pair, minlength=2)
    else:
        occupied = np.zeros(2, dtype=np.int64)
    for g, in_group, s_idx in groups:
        p_g = effective_meeting_prob(m.p * p_mult[g], m.kappa * k_mult[g], int(in_group.sum()), s_idx.size,
                                     int(occupied[g]) if m.same_qual else int(occupied.sum()))
        p_weighted += p_g * in_group.sum()
        meet = in_group & (u < p_g)
        if s_idx.size and meet.any():
            l_g = j_idx[meet]
            s_g = s_idx[(partner_draw[meet] * s_idx.size).astype(np.int64)]
            dh[l_g] = m.beta * b_mult[g] * np.maximum(0.0, h[s_g] - h[l_g])
            learners.append(l_g)
            partners.append(s_g)
    learners = np.concatenate(learners) if learners else np.empty(0, dtype=np.int64)
    partners = np.concatenate(partners) if partners else np.empty(0, dtype=np.int64)
    p_eff = p_weighted / j_idx.size if j_idx.size else 0.0
    return MeetingOutcome(dh=dh, n_meetings=int(learners.size), p_eff=float(p_eff),
                          learners=learners, partners=partners)


def autonomous_rate(cfg: Config, exp: np.ndarray) -> np.ndarray:
    """Tasso netto delta(s) - d, con delta(s) = delta0 * max(0, 1 - s/S) (alla Ben-Porath)."""
    lc = cfg.learning
    return lc.delta0 * np.maximum(0.0, 1.0 - exp / lc.horizon) - lc.depreciation


def autonomous_gains(cfg: Config, h: np.ndarray, exp: np.ndarray) -> np.ndarray:
    return autonomous_rate(cfg, exp) * h
