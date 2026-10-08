"""Regole di apprendimento: incontri junior-senior e apprendimento autonomo."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from skillcliff.config import Config


def role_masks(cfg: Config, exp: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    junior = exp < cfg.roles.junior_max_exp
    senior = exp >= cfg.roles.senior_min_exp
    return junior, senior


def effective_meeting_prob(p: float, kappa: float, n_junior: int, n_senior: int) -> float:
    """p_eff = min(p, kappa * S / J).

    Incontri = min(domanda p*J, capacità kappa*S): ogni senior può seguire al massimo
    kappa junior l'anno; se la capacità non basta, gli incontri sono razionati tra i junior.
    """
    if n_junior == 0 or n_senior == 0:
        return 0.0
    return min(p, kappa * n_senior / n_junior)


@dataclass
class MeetingOutcome:
    dh: np.ndarray          # guadagno per ciascun lavoratore (zero per i non junior)
    n_meetings: int
    p_eff: float


def meeting_gains(
    cfg: Config,
    h: np.ndarray,
    junior: np.ndarray,
    senior: np.ndarray,
    rng: np.random.Generator,
    p_mult: float = 1.0,
    beta_mult: float = 1.0,
) -> MeetingOutcome:
    """dh_j = beta * max(0, h_s - h_j) per i junior che incontrano un senior estratto a caso.

    I numeri casuali vengono estratti per tutti i junior a prescindere da p, così due
    scenari con lo stesso seed restano accoppiati (common random numbers): un incontro
    che avviene con p più basso avviene anche con p più alto.
    p_mult e beta_mult sono gli agganci per la fase 2 (IA).
    """
    m = cfg.meetings
    j_idx = np.flatnonzero(junior)
    s_idx = np.flatnonzero(senior)
    u = rng.random(j_idx.size)
    partner_draw = rng.random(j_idx.size)
    p_eff = effective_meeting_prob(m.p * p_mult, m.kappa, j_idx.size, s_idx.size)
    dh = np.zeros_like(h)
    meet = u < p_eff
    if s_idx.size and meet.any():
        partner = s_idx[(partner_draw[meet] * s_idx.size).astype(np.int64)]
        learners = j_idx[meet]
        dh[learners] = m.beta * beta_mult * np.maximum(0.0, h[partner] - h[learners])
    return MeetingOutcome(dh=dh, n_meetings=int(meet.sum()), p_eff=p_eff)


def autonomous_rate(cfg: Config, exp: np.ndarray) -> np.ndarray:
    """Tasso netto delta(s) - d, con delta(s) = delta0 * max(0, 1 - s/S) (alla Ben-Porath)."""
    lc = cfg.learning
    return lc.delta0 * np.maximum(0.0, 1.0 - exp / lc.horizon) - lc.depreciation


def autonomous_gains(cfg: Config, h: np.ndarray, exp: np.ndarray) -> np.ndarray:
    return autonomous_rate(cfg, exp) * h
