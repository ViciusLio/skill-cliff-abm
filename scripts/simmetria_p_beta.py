"""Dimezzare p (meno incontri) o beta (meno trasferimento per incontro): stesso effetto medio?

Base contro due shock dall'anno 10, a numeri casuali comuni. Stampa le variazioni a fine orizzonte.
Uso: python scripts/simmetria_p_beta.py [--reps 10]
"""
from __future__ import annotations

import argparse
import functools
from pathlib import Path

from skillcliff import load_config
from skillcliff.ai import MeetingShock
from skillcliff.experiment import run_replications

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "configs" / "base.yaml"))
    ap.add_argument("--reps", type=int, default=10)
    args = ap.parse_args()
    cfg = load_config(args.config)
    base = run_replications(cfg, args.reps)
    print(f"p_eff di base: {base['p_eff'][:, 0].mean():.3f} (p = {cfg.meetings.p})")
    print(f"Gini di base a fine orizzonte: {base['gini_w'][:, -1].mean():.4f}")
    for name, kw in (("p dimezzato", {"p_mult": 0.5}), ("beta dimezzato", {"beta_mult": 0.5})):
        r = run_replications(cfg, args.reps, functools.partial(MeetingShock, year=10, **kw))
        rel = {k: (r[k][:, -1] / base[k][:, -1] - 1).mean() for k in ("H", "mean_h_senior", "B_meet")}
        print(f"{name:15s} H {rel['H']:+.2%}  h senior {rel['mean_h_senior']:+.2%}  "
              f"B_meet {rel['B_meet']:+.2%}  Gini {r['gini_w'][:, -1].mean():.4f}")


if __name__ == "__main__":
    main()
