"""Esegue le repliche di uno scenario e salva outputs/<nome>/results.npz.

Esempi:
  python scripts/run_scenario.py --name base
  python scripts/run_scenario.py --name p03 --set meetings.p=0.3 --reps 10
"""
from __future__ import annotations

import argparse
import time

import yaml

from skillcliff import load_config
from skillcliff.experiment import run_replications, save_results
from skillcliff.metrics import mean_ci


def parse_overrides(items: list[str]) -> dict:
    out = {}
    for item in items:
        key, _, value = item.partition("=")
        out[key] = yaml.safe_load(value)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/base.yaml")
    ap.add_argument("--name", default="base")
    ap.add_argument("--reps", type=int, default=None)
    ap.add_argument("--set", nargs="*", default=[], metavar="CHIAVE=VALORE")
    args = ap.parse_args()

    cfg = load_config(args.config).with_overrides(parse_overrides(args.set))
    t0 = time.perf_counter()
    res = run_replications(cfg, n_reps=args.reps)
    path = f"outputs/{args.name}/results.npz"
    save_results(path, cfg, res)
    n = res["Y"].shape[0]
    print(f"{args.name}: {n} repliche in {time.perf_counter() - t0:.1f}s -> {path}")
    for k in ("mean_h", "mean_h_junior", "mean_h_senior", "B", "B_meet", "gini_w", "n_meetings"):
        m, lo, hi = mean_ci(res[k].mean(axis=1))
        print(f"  {k:14s} {m:9.4f}  IC95 [{lo:.4f}, {hi:.4f}]")


if __name__ == "__main__":
    main()
