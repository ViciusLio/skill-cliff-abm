"""Aggancio per la fase 2 (IA). Nella fase 1 l'IA è disattivata: moltiplicatori neutri.

Nella fase 2 questo modulo fornirà A(t) = A0 * (1+g)^t, la regola `target` che decide
chi viene sostituito, i moltiplicatori di p e beta in funzione di A(t) e Y = f(sum h, A).
"""
from __future__ import annotations

from skillcliff.config import Config


class NoAI:
    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg

    def meeting_multipliers(self, t: int) -> tuple[float, float]:
        """(moltiplicatore di p, moltiplicatore di beta) nell'anno t."""
        return 1.0, 1.0

    def output(self, t: int, sum_h: float) -> float:
        """Y = sum h nella fase 1."""
        return sum_h


class MeetingShock(NoAI):
    """Esperimento di meccanismo (non è IA): dall'anno `year` p e beta sono moltiplicati
    per costanti. Isola l'effetto di una riduzione permanente degli incontri."""

    def __init__(self, cfg: Config, year: int, p_mult: float = 1.0, beta_mult: float = 1.0) -> None:
        super().__init__(cfg)
        self.year, self.p_mult, self.beta_mult = year, p_mult, beta_mult

    def meeting_multipliers(self, t: int) -> tuple[float, float]:
        return (self.p_mult, self.beta_mult) if t >= self.year else (1.0, 1.0)


def make_ai(cfg: Config) -> NoAI:
    if cfg.ai.enabled:
        raise NotImplementedError("L'IA arriva nella fase 2")
    return NoAI(cfg)
