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
"""
from __future__ import annotations

from dataclasses import dataclass

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
        return {
            "junior": MeetingModifiers(p=both),
            "senior": MeetingModifiers(kappa=both),
            "qualificati": MeetingModifiers(p=(1.0, cut), kappa=(1.0, cut)),
            "non_qualificati": MeetingModifiers(p=(cut, 1.0), kappa=(cut, 1.0)),
            "complementare": MeetingModifiers(beta=(1.0 + phi, 1.0 + phi)),
        }[self.a.target]

    def output(self, t: int, sum_h: float) -> float:
        return sum_h * (1.0 + self.a.theta * (self.productivity(t) - 1.0))


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


def make_ai(cfg: Config) -> NoAI:
    return AI(cfg) if cfg.ai.enabled else NoAI(cfg)
