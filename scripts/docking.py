"""Docking NumPy vs Mesa: stesse regole, implementazioni indipendenti, confronto statistico.

Due test per ogni statistica:
- test t di Welch sulla differenza (p grande = nessun segnale di differenza);
- test di equivalenza TOST entro ±1% (p piccolo = equivalenza dimostrata), con IC al 90%
  della differenza relativa.

Uso: python scripts/docking.py [--config configs/base.yaml] [--reps 30] [--N 5000]
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
MARGIN = 0.01   # margine di equivalenza: differenza relativa massima accettata (±1%)


def equivalence(a: np.ndarray, b: np.ndarray, margin: float = MARGIN) -> dict:
    """Test di equivalenza TOST (due test t di Welch unilaterali) sulla differenza delle medie.

    H0: |media_b - media_a| >= margin * media_a. Un p piccolo (< 0,05) dimostra l'equivalenza
    entro il margine. Riporta anche l'IC al 90% della differenza relativa: l'equivalenza al 5%
    vale per ogni margine che contiene l'intervallo.
    """
    na, nb = a.size, b.size
    va, vb = a.var(ddof=1) / na, b.var(ddof=1) / nb
    se = np.sqrt(va + vb)
    df = (va + vb) ** 2 / (va ** 2 / (na - 1) + vb ** 2 / (nb - 1))
    diff, delta = b.mean() - a.mean(), margin * a.mean()
    p_low = stats.t.sf((diff + delta) / se, df)      # H0: diff <= -delta
    p_high = stats.t.cdf((diff - delta) / se, df)    # H0: diff >= +delta
    half = stats.t.ppf(0.95, df) * se
    return {"p_tost": float(max(p_low, p_high)),
            "ic90_rel": [float((diff - half) / a.mean()), float((diff + half) / a.mean())]}


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
            **equivalence(a, b),
        }
    return {"N": cfg.population.N, "reps": reps, "margine_equivalenza": MARGIN, "seconds_numpy": t_np,
            "seconds_mesa": t_mesa, "metrics": rows}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/base.yaml")
    ap.add_argument("--reps", type=int, default=30)
    ap.add_argument("--N", type=int, default=5000)
    ap.add_argument("--out", default="outputs/docking.json")
    args = ap.parse_args()
    cfg = load_config(args.config).with_overrides({"population.N": args.N})
    res = docking(cfg, args.reps)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(res, indent=2))
    print(f"N={res['N']} repliche={res['reps']}  NumPy {res['seconds_numpy']:.1f}s  Mesa {res['seconds_mesa']:.1f}s")
    for k, r in res["metrics"].items():
        lo, hi = r["ic90_rel"]
        print(f"{k:15s} numpy={r['numpy']:.4f} mesa={r['mesa']:.4f} diff={r['rel_diff']:+.2%} "
              f"p(diff)={r['p_value']:.2f}  IC90=[{lo:+.2%}, {hi:+.2%}]  p(equiv ±{MARGIN:.0%})={r['p_tost']:.4f}")


if __name__ == "__main__":
    main()
