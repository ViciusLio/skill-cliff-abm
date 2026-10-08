"""Intelligenza artificiale (fase 2) e moduli che modificano gli incontri.

Produttività dell'IA:            A_t = (1+g)^(t - t0) per t >= t0, altrimenti 1
Quota di compiti automatizzati:  phi_t = phi_max * (1 - 1/A_t)        (0 all'introduzione, satura a phi_max)
Output:                          Y_t = H_t * (1 + theta * (A_t - 1)),  H_t = somma di h

Il bersaglio decide quali parametri degli incontri vengono ridotti (o aumentati):
  junior           p   * (1 - phi) per entrambe le qualifiche   (meno lavoro junior, meno affiancamento)
  senior           kappa * (1 - phi) per entrambe              (meno senior disponibili come mentori)
  qualificati      p e kappa del gruppo H * (1 - phi)
  non_qualificati  p e kappa del gruppo L * (1 - phi)
  complementare    beta * (1 + phi) per entrambe               (l'IA rende più efficace l'insegnamento)

Con ai.displacement (decisione D13) i bersagli junior, qualificati e non_qualificati non riducono p:
ogni anno una quota phi dei junior del gruppo colpito è non occupata. Un junior non occupato non
incontra senior e non impara sul lavoro (resta solo l'obsolescenza d); i suoi compiti li svolge
l'IA, quindi l'output corrente non cambia e la perdita passa solo per il suo capitale umano.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from skillcliff.config import Config

TARGETS = ("junior", "senior", "qualificati", "non_qualificati", "complementare")


@dataclass(frozen=True)
class MeetingModifiers:
    """Moltiplicatori di p, kappa e beta per gruppo di qualifica (indice 0 = L, 1 = H)."""
    p: tuple[float, float] = (1.0, 1.0)
    kappa: tuple[float, float] = (1.0, 1.0)
    beta: tuple[float, float] = (1.0, 1.0)


NEUTRAL = MeetingModifiers()


class NoAI:
    """Nessuna IA: incontri invariati, Y = H."""

    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg

    def productivity(self, t: int) -> float:
        return 1.0

    def automation_share(self, t: int) -> float:
        return 0.0

    def meeting_modifiers(self, t: int) -> MeetingModifiers:
        return NEUTRAL

    def output(self, t: int, sum_h: float) -> float:
        return sum_h

    def nonemployed(self, t: int, junior: np.ndarray, high: np.ndarray, rng) -> np.ndarray | None:
        """Maschera dei junior non occupati nell'anno t (None: nessuno)."""
        return None


# Gruppi di junior colpiti dalla non occupazione (D13), per bersaglio: (L, H).
DISPLACED_GROUPS = {"junior": (True, True), "qualificati": (False, True), "non_qualificati": (True, False)}


class AI(NoAI):
    def __init__(self, cfg: Config) -> None:
        super().__init__(cfg)
        a = cfg.ai
        if a.target not in TARGETS:
            raise ValueError(f"ai.target deve essere uno di {TARGETS}")
        if a.target in ("qualificati", "non_qualificati") and not cfg.meetings.same_qual:
            raise ValueError("i bersagli per qualifica richiedono meetings.same_qual")
        self.a = a

    def productivity(self, t: int) -> float:
        return (1.0 + self.a.g) ** (t - self.a.start) if t >= self.a.start else 1.0

    def automation_share(self, t: int) -> float:
        return self.a.phi_max * (1.0 - 1.0 / self.productivity(t))

    def meeting_modifiers(self, t: int) -> MeetingModifiers:
        phi = self.automation_share(t)
        cut, both = 1.0 - phi, (1.0 - phi, 1.0 - phi)
        if self.a.displacement and self.a.target in DISPLACED_GROUPS:
            # i junior colpiti escono dal pool (vedi nonemployed); restano i tagli sui mentori
            return {"junior": NEUTRAL,
                    "qualificati": MeetingModifiers(kappa=(1.0, cut)),
                    "non_qualificati": MeetingModifiers(kappa=(cut, 1.0))}[self.a.target]
        return {
            "junior": MeetingModifiers(p=both),
            "senior": MeetingModifiers(kappa=both),
            "qualificati": MeetingModifiers(p=(1.0, cut), kappa=(1.0, cut)),
            "non_qualificati": MeetingModifiers(p=(cut, 1.0), kappa=(cut, 1.0)),
            "complementare": MeetingModifiers(beta=(1.0 + phi, 1.0 + phi)),
        }[self.a.target]

    def output(self, t: int, sum_h: float) -> float:
        return sum_h * (1.0 + self.a.theta * (self.productivity(t) - 1.0))

    def nonemployed(self, t: int, junior: np.ndarray, high: np.ndarray, rng) -> np.ndarray | None:
        if not (self.a.displacement and self.a.target in DISPLACED_GROUPS):
            return None
        hit_low, hit_high = DISPLACED_GROUPS[self.a.target]
        in_group = np.where(high, hit_high, hit_low)
        u = rng.random(junior.size)          # estratto per tutti: numeri casuali allineati tra anni
        return junior & in_group & (u < self.automation_share(t))


class MeetingShock(NoAI):
    """Esperimento di meccanismo (non è IA): dall'anno `year` p e beta sono moltiplicati
    per costanti. Isola l'effetto di una riduzione permanente degli incontri."""

    def __init__(self, cfg: Config, year: int, p_mult: float = 1.0, beta_mult: float = 1.0) -> None:
        super().__init__(cfg)
        self.year, self.p_mult, self.beta_mult = year, p_mult, beta_mult

    def meeting_modifiers(self, t: int) -> MeetingModifiers:
        if t < self.year:
            return NEUTRAL
        return MeetingModifiers(p=(self.p_mult,) * 2, beta=(self.beta_mult,) * 2)


class FixedAutomation(NoAI):
    """D15: dall'anno `start` una quota costante phi dei compiti junior è automatizzata
    (p * (1 - phi) per entrambe le qualifiche). Serve a confrontare la scelta dell'impresa
    con quella del pianificatore: phi è la variabile di scelta, l'output è calcolato fuori."""

    def __init__(self, cfg: Config, phi: float, start: int | None = None) -> None:
        super().__init__(cfg)
        self.phi = phi
        self.start = cfg.ai.start if start is None else start

    def automation_share(self, t: int) -> float:
        return self.phi if t >= self.start else 0.0

    def meeting_modifiers(self, t: int) -> MeetingModifiers:
        cut = 1.0 - self.automation_share(t)
        return MeetingModifiers(p=(cut, cut))


def make_ai(cfg: Config) -> NoAI:
    return AI(cfg) if cfg.ai.enabled else NoAI(cfg)
