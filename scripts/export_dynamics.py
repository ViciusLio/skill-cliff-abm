"""Esporta le traiettorie di un campione di agenti e i flussi di conoscenza anno per anno,
per la vista dinamica del sito (site/dinamica.html -> site/data/dinamica.json).

Una sola replica (la prima, stesso seed per tutti gli scenari): serve a vedere il
meccanismo, non a fare inferenza. Gli agenti tracciati sono quelli con uid % K == 0.

Uso: python scripts/export_dynamics.py [--every 6]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from skillcliff import load_config
from skillcliff.ai import MeetingShock
from skillcliff.experiment import replication_seeds
from skillcliff.learning import role_masks
from skillcliff.model import Model

ROOT = Path(__file__).resolve().parents[1]
SHOCK_YEAR, SHOCK_P_MULT = 10, 0.5
SENIOR_BANDS = ((15, 24), (25, 34), (35, 99))   # esperienza del senior che insegna


def r3(x: np.ndarray) -> list:
    return np.round(x, 3).tolist()


def export(cfg, ai, every: int) -> dict:
    model = Model(cfg, replication_seeds(cfg, 1)[0], ai)
    for _ in range(cfg.burn_in):
        model.step()
    years = []
    for t in range(cfg.T):
        rec = model.step()
        pop, meet = model.pop, model.last_meet
        junior, senior = role_masks(cfg, pop.exp)
        role = np.where(junior, 0, np.where(senior, 2, 1))
        tr = pop.uid % every == 0

        # Collegamenti: incontri il cui junior è tracciato (posizione del senior a fine anno).
        lt = tr[meet.learners]
        li, si = meet.learners[lt], meet.partners[lt]

        # Correnti: conoscenza trasferita (somma dh) per fascia d'esperienza del senior e qualifica del junior.
        dh_l = meet.dh[meet.learners]
        s_exp = pop.exp[meet.partners]
        q_l = pop.high[meet.learners]
        flows = {}
        for a0, a1 in SENIOR_BANDS:
            band = (s_exp >= a0) & (s_exp <= a1)
            key = f"{a0}-{a1}" if a1 < 99 else f"{a0}+"
            flows[key] = [round(float(dh_l[band & ~q_l].sum()), 3), round(float(dh_l[band & q_l].sum()), 3)]

        years.append({
            "agents": {"u": pop.uid[tr].tolist(), "a": pop.age[tr].tolist(), "h": r3(pop.h[tr]),
                       "r": role[tr].tolist(), "q": pop.high[tr].astype(int).tolist()},
            "links": {"u": pop.uid[li].tolist(), "sa": pop.age[si].tolist(), "sh": r3(pop.h[si]),
                      "dh": r3(meet.dh[li])},
            "flows": flows,
            "stats": {k: round(float(rec[k]), 5) for k in
                      ("n_junior", "n_senior", "n_meetings", "p_eff", "B", "B_meet", "mean_h_junior", "mean_h_senior")},
        })
    return {"years": years}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "configs" / "base.yaml"))
    ap.add_argument("--every", type=int, default=6, help="traccia un agente ogni K (uid %% K == 0)")
    args = ap.parse_args()
    cfg = load_config(args.config)
    out = {
        "every": args.every, "N": cfg.population.N, "retirement_age": cfg.population.retirement_age,
        "roles": {"junior_max_exp": cfg.roles.junior_max_exp, "senior_min_exp": cfg.roles.senior_min_exp},
        "shock_year": SHOCK_YEAR, "bands": [f"{a}-{b}" if b < 99 else f"{a}+" for a, b in SENIOR_BANDS],
        "scenarios": {
            "base": {"label": "Base stazionario", **export(cfg, None, args.every)},
            "shock_p": {"label": f"p dimezzato dall'anno {SHOCK_YEAR}",
                        **export(cfg, MeetingShock(cfg, SHOCK_YEAR, SHOCK_P_MULT), args.every)},
        },
    }
    path = ROOT / "site" / "data" / "dinamica.json"
    path.write_text(json.dumps(out, separators=(",", ":")))
    print(f"{path.relative_to(ROOT)}: {path.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
