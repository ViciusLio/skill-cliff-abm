"""Docking NumPy vs Mesa: stesse regole, implementazioni indipendenti, confronto statistico.

Uso: python scripts/docking.py [--config configs/base.yaml] [--reps 20] [--N 1000]
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
from scipy import stats

from skillcliff import load_config
from skillcliff.experiment import run_replications
from skillcliff.mesa_twin import run_mesa

METRICS = ("mean_h", "mean_h_junior", "mean_h_senior", "B_meet", "B_aut")


def docking(cfg, reps: int) -> dict:
    t0 = time.perf_counter()
    np_res = run_replications(cfg, n_reps=reps)
    t_np = time.perf_counter() - t0
    t0 = time.perf_counter()
    mesa_res = [run_mesa(cfg, seed=cfg.seed + 10_000 + r) for r in range(reps)]
    t_mesa = time.perf_counter() - t0
    rows = {}
    for k in METRICS:
        a = np_res[k].mean(axis=1)                   # media temporale per replica
        b = np.array([m[k].mean() for m in mesa_res])
        rows[k] = {
            "numpy": float(a.mean()), "mesa": float(b.mean()),
            "rel_diff": float(b.mean() / a.mean() - 1),
            "p_value": float(stats.ttest_ind(a, b, equal_var=False).pvalue),
        }
    return {"N": cfg.population.N, "reps": reps, "seconds_numpy": t_np,
            "seconds_mesa": t_mesa, "metrics": rows}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/base.yaml")
    ap.add_argument("--reps", type=int, default=20)
    ap.add_argument("--N", type=int, default=1000)
    ap.add_argument("--out", default="outputs/docking.json")
    args = ap.parse_args()
    cfg = load_config(args.config).with_overrides({"population.N": args.N})
    res = docking(cfg, args.reps)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(res, indent=2))
    print(f"N={res['N']} repliche={res['reps']}  NumPy {res['seconds_numpy']:.1f}s  Mesa {res['seconds_mesa']:.1f}s")
    for k, r in res["metrics"].items():
        print(f"{k:15s} numpy={r['numpy']:.4f} mesa={r['mesa']:.4f} diff={r['rel_diff']:+.2%} p={r['p_value']:.2f}")


if __name__ == "__main__":
    main()
