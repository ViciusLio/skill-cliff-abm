"""Il risultato dipende dalla dimensione della popolazione? Esegue il modello base a scale
crescenti (fino a quella degli occupati italiani, ~24 milioni) e confronta medie, intervalli
di confidenza e tempi. Salva outputs/scala.json e report/numeri_scala.json.

Uso: python scripts/scale_check.py [--max-n 5000000] [--real]   (--real aggiunge N = 24 milioni, 1 replica)
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from skillcliff import load_config
from skillcliff.experiment import run_replications
from skillcliff.metrics import mean_ci

ROOT = Path(__file__).resolve().parents[1]
PLAN = [(5_000, 30), (50_000, 30), (500_000, 10), (5_000_000, 3)]
REAL_N = 24_000_000   # occupati in Italia, ordine di grandezza (ISTAT)
METRICS = ("B", "B_meet", "mean_h_junior", "mean_h_senior", "gini_w")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "configs" / "base.yaml"))
    ap.add_argument("--max-n", type=int, default=5_000_000)
    ap.add_argument("--real", action="store_true", help="aggiunge una replica a scala reale (24 milioni)")
    args = ap.parse_args()
    base = load_config(args.config)
    plan = [(n, r) for n, r in PLAN if n <= args.max_n] + ([(REAL_N, 1)] if args.real else [])
    rows = []
    for n, reps in plan:
        cfg = base.with_overrides({"population.N": n})
        t0 = time.perf_counter()
        res = run_replications(cfg, n_reps=reps)
        dt = time.perf_counter() - t0
        row = {"N": n, "repliche": reps, "secondi": round(dt, 1)}
        for k in METRICS:
            m, lo, hi = mean_ci(res[k].mean(axis=1)) if reps > 1 else (res[k].mean(),) * 3
            row[k] = [float(m), float(lo), float(hi)]
        rows.append(row)
        print(f"N={n:>11,} rep={reps:>2} {dt:7.1f}s  B={row['B'][0]:.5f}  "
              f"B_inc={row['B_meet'][0]:.5f}  h_sen={row['mean_h_senior'][0]:.4f}  gini={row['gini_w'][0]:.4f}", flush=True)
    out = ROOT / "report" / "numeri_scala.json"
    out.write_text(json.dumps(rows, indent=1))
    print(f"-> {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
