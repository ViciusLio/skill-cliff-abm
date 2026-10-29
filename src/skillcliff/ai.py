"""Intelligenza artificiale (fase 2) e moduli che modificano gli incontri.

Produttività dell'IA:            A_t = (1+g)^(t - t0) per t >= t0, altrimenti 1
Quota di compiti automatizzati:  phi_t = phi_max * (1 - 1/A_t)        (0 all'introduzione, satura a phi_max)
Output (D18):                    Y_t = H_t * (1 + theta * (A_t - 1) * F_t),  H_t = somma di h
                                 F_t = media di f pesata con h tra gli utenti U dell'IA
Salari (D18):                    w_i = h_i * (1 + theta (A_t - 1) f_i)  per i in U,  w_i = h_i altrimenti
Rendita dell'IA (D18):           R_t = Y_t - somma dei salari = theta (A_t - 1) F_t (H_t - H_U) >= 0: il guadagno
                                 sui compiti svolti dall'IA al posto del bersaglio va a chi possiede l'IA
Familiarità f_i (D18):           chi entra con l'IA già arrivata ha f = 1; chi c'era parte da 0 e, per ogni
                                 anno da occupato con l'IA, f <- f + gamma (1 - f)
Utenti U: gli occupati che lavorano con l'IA al posto del bersaglio. junior: i non junior;
senior: i non senior; qualificati / non_qualificati: gli occupati del gruppo; complementare: tutti.
Con ai.familiarity = false: F = 1 e w = h (versione precedente).

Il bersaglio decide chi viene sostituito; ai.margin_junior e ai.margin_senior (D16) decidono che cosa
vuol dire "sostituire". Tabella 2x2, con phi_t come intensità:

              compiti (resta al lavoro, perde compiti)     posto (perde il posto)
  junior      p     * (1 - phi)  meno affiancamento         una quota phi dei junior è non occupata (D13)
  senior      beta  * (1 - phi)  trasmette meno (D17)       kappa * (1 - phi)  meno mentori

  junior           riga junior, entrambe le qualifiche
  senior           riga senior, entrambe le qualifiche
  qualificati      righe junior e senior, solo gruppo H
  non_qualificati  righe junior e senior, solo gruppo L
  complementare    beta * (1 + phi) per entrambe              (l'IA rende più efficace l'insegnamento)

Con margine "compiti" su entrambe le righe p e beta entrano come prodotto nell'apprendimento medio
(Proposizione 1): junior e senior hanno lo stesso effetto medio, cambia la dispersione.
Le versioni precedenti si riottengono così: bersaglio senior di prima = senior con margin_senior
"posto"; qualificati/non_qualificati di prima = margin_junior "compiti", margin_senior "posto";
ai.displacement di prima (D13) = margin_junior "posto".

Un junior non occupato non incontra senior e non impara sul lavoro (resta solo l'obsolescenza d);
i suoi compiti li svolge l'IA, quindi l'output corrente non cambia e la perdita passa solo per il suo
capitale umano. Con D19 l'anno da non occupato non conta come esperienza: il junior resta junior più
a lungo e arriva più tardi (e con meno anni di carriera) a senior.
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

    def output(self, t: int, sum_h: float, F: float = 1.0) -> float:
        return sum_h

    def observe(self, t: int, h: np.ndarray, junior: np.ndarray, gain_prev: float) -> None:
        """Osserva lo stato all'inizio dell'anno t (E2: salario dei junior e valore formativo). Base: nulla."""

    def savings(self, t: int, n_junior: int) -> float:
        """Risparmio dell'impresa dall'automazione nell'anno t (E2). Base: zero."""
        return 0.0

    def tutor(self, t, h, f, junior, senior, high, out):
        """E1: (guadagno dall'IA tutor, fattore sull'apprendimento autonomo dei junior). Base: (None, None)."""
        return None, None

    def entrant_familiarity(self, t: int) -> float:
        return 0.0

    def update_familiarity(self, t: int, f: np.ndarray, employed: np.ndarray) -> None:
        """Aggiorna f sul posto per chi è stato occupato nell'anno t - 1 (D18)."""

    def users(self, junior: np.ndarray, senior: np.ndarray, high: np.ndarray,
              out: np.ndarray | None) -> np.ndarray | None:
        """Maschera degli utenti dell'IA (None: nessun peso per familiarità)."""
        return None

    def familiarity_weight(self, h: np.ndarray, f: np.ndarray, users: np.ndarray | None) -> float:
        """F: media di f pesata con h tra gli utenti; 1 se non c'è peso per familiarità."""
        if users is None:
            return 1.0
        h_u = h[users].sum()
        return float((h[users] * f[users]).sum() / h_u) if h_u > 0 else 0.0

    def wages(self, t: int, h: np.ndarray, f: np.ndarray, users: np.ndarray | None) -> np.ndarray:
        return h

    def nonemployed(self, t: int, junior: np.ndarray, high: np.ndarray, rng,
                    exp: np.ndarray | None = None) -> np.ndarray | None:
        """Maschera dei junior non occupati nell'anno t (None: nessuno). exp serve agli shock di coorte."""
        return None


# Gruppi colpiti per bersaglio: (L, H), e se il bersaglio colpisce junior e senior.
HIT_GROUPS = {"junior": (True, True), "senior": (True, True),
              "qualificati": (False, True), "non_qualificati": (True, False)}
HITS_JUNIOR = ("junior", "qualificati", "non_qualificati")
HITS_SENIOR = ("senior", "qualificati", "non_qualificati")


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
        if self.a.endogenous:
            return self._phi if t >= self.a.start else 0.0
        return self.a.phi_max * (1.0 - 1.0 / self.productivity(t))

    # --- E1: l'IA come tutor ----------------------------------------------------------
    def tutor(self, t, h, f, junior, senior, high, out):
        a = self.a
        if not a.tutor or t < a.start:
            return None, None
        learners = junior if out is None else junior & ~out
        gain = np.zeros_like(h)
        for g in (False, True):                       # l'IA ha imparato dai senior della stessa qualifica
            s_g, j_g = senior & (high == g), learners & (high == g)
            if s_g.any() and j_g.any():
                target = a.codifiable * h[s_g].mean()
                gain[j_g] = a.beta_ai * f[j_g] * np.maximum(0.0, target - h[j_g])
        factor = np.where(learners, 1.0 - a.effort * f, 1.0) if a.effort > 0 else None
        return gain, factor

    # --- E2: l'impresa sceglie phi ----------------------------------------------------
    _phi, _w_j, _cost = 0.0, 1.0, 1.0

    def training_value(self, gain_prev: float) -> float:
        """Valore formativo di un anno da junior: guadagno medio dagli incontri, scontato sulla carriera."""
        k = np.arange(1, self.a.career + 1)
        return gain_prev * float((self.a.rho ** k).sum())

    def observe(self, t, h, junior, gain_prev):
        if not self.a.endogenous:
            return
        w_j = float(h[junior].mean()) if junior.any() else 0.0
        cost = self.a.c0 / self.productivity(t)
        perceived = w_j - self.a.chi * self.training_value(gain_prev)
        self._w_j, self._cost = w_j, cost
        self._phi = self.a.phi_max * max(0.0, 1.0 - cost / perceived) if perceived > 0 else 0.0

    def savings(self, t, n_junior):
        """Compiti automatizzabili x in [0, 1] con costo dell'IA c_t / (1 - x): si automatizzano quelli con
        x < x* = phi / phi_max; risparmio = J * phi_max * integrale di (w_J - c_t / (1 - x)) su [0, x*]."""
        if not self.a.endogenous or t < self.a.start or self._phi <= 0:
            return 0.0
        x = self._phi / self.a.phi_max
        return n_junior * self.a.phi_max * (self._w_j * x + self._cost * np.log(1.0 - x))

    def meeting_modifiers(self, t: int) -> MeetingModifiers:
        phi = self.automation_share(t)
        a = self.a
        if a.target == "complementare":
            return MeetingModifiers(beta=(1.0 + phi, 1.0 + phi))
        cut = tuple(1.0 - phi if hit else 1.0 for hit in HIT_GROUPS[a.target])
        mods = {}
        if a.target in HITS_JUNIOR and a.margin_junior == "compiti":
            mods["p"] = cut           # con "posto" i junior colpiti escono dal pool (vedi nonemployed)
        if a.target in HITS_SENIOR:
            mods["beta" if a.margin_senior == "compiti" else "kappa"] = cut
        return MeetingModifiers(**mods)

    def output(self, t: int, sum_h: float, F: float = 1.0) -> float:
        return sum_h * (1.0 + self.a.theta * (self.productivity(t) - 1.0) * F)

    def entrant_familiarity(self, t: int) -> float:
        return 1.0 if self.a.familiarity and t >= self.a.start else 0.0

    def update_familiarity(self, t: int, f: np.ndarray, employed: np.ndarray) -> None:
        if self.a.familiarity and t - 1 >= self.a.start:
            f[employed] += self.a.gamma * (1.0 - f[employed])

    def users(self, junior, senior, high, out):
        if not self.a.familiarity:
            return None
        employed = np.ones_like(junior) if out is None else ~out
        return employed & {"junior": ~junior, "senior": ~senior, "qualificati": high,
                           "non_qualificati": ~high, "complementare": True}[self.a.target]

    def wages(self, t, h, f, users):
        if users is None:
            return h
        w = h.copy()
        w[users] *= 1.0 + self.a.theta * (self.productivity(t) - 1.0) * f[users]
        return w

    def nonemployed(self, t: int, junior: np.ndarray, high: np.ndarray, rng,
                    exp: np.ndarray | None = None) -> np.ndarray | None:
        if not (self.a.target in HITS_JUNIOR and self.a.margin_junior == "posto"):
            return None
        hit_low, hit_high = HIT_GROUPS[self.a.target]
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


class CohortShock(NoAI):
    """Esperimento di validazione (T6, non è IA): una recessione dall'anno `year` per `duration` anni.
    In quegli anni chi cerca il primo lavoro (junior con esperienza 0) resta non occupato con
    probabilità u; con D19 l'anno perso non conta come esperienza, quindi chi resta fuori ritenta
    l'anno dopo. Nessun'altra regola cambia: misura il costo di un ingresso ritardato."""

    def __init__(self, cfg: Config, year: int, duration: int, u: float) -> None:
        super().__init__(cfg)
        self.year, self.duration, self.u = year, duration, u

    def nonemployed(self, t, junior, high, rng, exp=None):
        if not self.year <= t < self.year + self.duration:
            return None
        draw = rng.random(junior.size)       # stream dell'IA: gli altri restano allineati con la base
        return junior & (exp == 0) & (draw < self.u)


class Policy(AI):
    """Esperimento di politica (T9): l'IA della configurazione più una leva che dall'arrivo dell'IA
    cambia del fattore (1 + size) un parametro esistente. Leve: "p" (apprendistati), "kappa"
    (capacità di mentoring), "beta" (IA che aiuta a insegnare), "phi" (contributo sull'automazione
    dei compiti d'ingresso: phi * (1 - size)). Nessuna regola nuova."""

    LEVERS = ("p", "kappa", "beta", "phi")

    def __init__(self, cfg: Config, lever: str, size: float) -> None:
        super().__init__(cfg)
        if lever not in self.LEVERS:
            raise ValueError(f"lever deve essere uno di {self.LEVERS}")
        self.lever, self.size = lever, size

    def automation_share(self, t: int) -> float:
        phi = super().automation_share(t)
        return phi * (1.0 - self.size) if self.lever == "phi" else phi

    def meeting_modifiers(self, t: int) -> MeetingModifiers:
        m = super().meeting_modifiers(t)
        if self.lever == "phi" or t < self.a.start:
            return m
        scaled = tuple(x * (1.0 + self.size) for x in getattr(m, self.lever))
        return MeetingModifiers(**{**{k: getattr(m, k) for k in ("p", "kappa", "beta")}, self.lever: scaled})


class FixedShareFirm(AI):
    """E2, pianificatore (D33): quota phi costante dall'arrivo dell'IA, con salari, costi e risparmi
    calcolati come per l'impresa di E2. Serve a trovare la quota costante socialmente ottima."""

    def __init__(self, cfg: Config, phi: float) -> None:
        super().__init__(cfg)
        self.phi_const = phi

    def observe(self, t, h, junior, gain_prev):
        super().observe(t, h, junior, gain_prev)
        self._phi = self.phi_const if t >= self.a.start else 0.0


def make_ai(cfg: Config) -> NoAI:
    return AI(cfg) if cfg.ai.enabled else NoAI(cfg)
