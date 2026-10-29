"""Docking NetLogo vs NumPy: il gemello Netlogo/skill_cliff.nlogo contro il modello Python, scenario per scenario.

Lancia gli esperimenti BehaviorSpace del modello NetLogo senza interfaccia, legge le tabelle e confronta
le distribuzioni tra repliche con il modello NumPy (stessi test di scripts/docking.py: Welch e TOST ±1%).
Per ogni replica: media sui 60 anni registrati (livelli e B) e media degli ultimi 5 anni (H, Y, Gini).

Serve NetLogo 6.4 (https://www.netlogo.org) e Java: NETLOGO_HOME = cartella di NetLogo.
Uso: NETLOGO_HOME=/percorso/NetLogo-6.4.0-64 python scripts/docking_netlogo.py [--reps 30] [--threads 2]
     python scripts/docking_netlogo.py --csv-dir outputs/netlogo   (riusa tabelle già prodotte)
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from docking import MARGIN, equivalence  # noqa: E402

from skillcliff import load_config  # noqa: E402
from skillcliff.experiment import run_replications  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "Netlogo" / "skill_cliff.nlogo"
MODEL_ESTESO = ROOT / "Netlogo" / "skill_cliff_esteso.nlogo"     # solo sul ramo esteso (D29)
SEP = "@#$#@#$#@\n"

# esperimento NetLogo -> override della configurazione Python
SCENARIOS = {
    "base": {},
    "junior_compiti": {"ai.enabled": True, "ai.target": "junior"},
    "junior_posto": {"ai.enabled": True, "ai.target": "junior", "ai.margin_junior": "posto"},
    "senior_compiti": {"ai.enabled": True, "ai.target": "senior"},
    "senior_posto": {"ai.enabled": True, "ai.target": "senior", "ai.margin_senior": "posto"},
    "complementare": {"ai.enabled": True, "ai.target": "complementare"},
    "mentore_stabile": {"meetings.stable_mentor": True, "meetings.separation": 0.15, "meetings.beta": 0.0754},
}
# colonna NetLogo -> metrica Python
# ramo esteso (--esteso): la base con i meccanismi nuovi spenti e gli scenari di E2 ed E1
SCENARIOS_ESTESO = {
    "base": {},
    "e2_impresa_miope": {"ai.enabled": True, "ai.target": "junior", "ai.endogenous": True},
    "e2_impresa_chi_0.5": {"ai.enabled": True, "ai.target": "junior", "ai.endogenous": True, "ai.chi": 0.5},
    "e1_tutor": {"ai.enabled": True, "ai.target": "junior", "ai.tutor": True, "ai.beta_ai": 0.1},
    "e1_tutor_sforzo": {"ai.enabled": True, "ai.target": "junior", "ai.tutor": True, "ai.beta_ai": 0.1, "ai.effort": 0.25},
}
COLS = {"H-agg": "H", "Y": "Y", "B-meet": "B_meet", "B-aut": "B_aut", "mean-h": "mean_h",
        "mean-h-junior": "mean_h_junior", "mean-h-senior": "mean_h_senior", "gini-w": "gini_w",
        "F-users": "F_U", "n-out": "n_nonemployed", "n-pairs": "n_pairs", "n-junior": "n_junior"}
WHOLE = ("mean_h", "mean_h_junior", "mean_h_senior", "B_meet", "B_aut", "n_junior", "n_nonemployed", "n_pairs", "F_U",
         "phi", "B_tutor")
END = ("H", "Y", "gini_w", "savings")
COLS.update({"phi": "phi", "savings": "savings", "B-tutor": "B_tutor"})   # colonne del modello esteso


def run_netlogo(home: Path, name: str, reps: int, threads: int, out: Path, model: Path = MODEL) -> Path:
    xml = model.read_text(encoding="utf-8").split(SEP)[7].replace('repetitions="10"', f'repetitions="{reps}"')
    setup = out / "esperimenti.xml"
    setup.write_text(xml, encoding="utf-8")
    table = out / f"{name}.csv"
    cmd = ["bash", str(home / "netlogo-headless.sh"), "--model", str(model), "--setup-file", str(setup),
           "--experiment", name, "--table", str(table), "--threads", str(threads)]
    # con un errore di compilazione NetLogo non esce da solo: il timeout lo ferma
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=60 * 60)
    if res.returncode != 0 or not table.exists():
        raise RuntimeError(f"NetLogo ({name}): {res.stderr[-2000:]}")
    return table


def read_table(path: Path) -> dict[str, np.ndarray]:
    """{metrica: array (repliche, anni registrati)}; tiene solo gli anni t > 0 (gli anni 0..T-1 del modello)."""
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    head = rows[6]
    i_run, i_t = head.index("[run number]"), head.index("t")
    runs: dict[int, list[list[str]]] = {}
    for r in rows[7:]:
        if float(r[i_t]) > 0:
            runs.setdefault(int(r[i_run]), []).append(r)
    out = {}
    for col, key in COLS.items():
        if col not in head:              # colonne del modello esteso assenti nel modello base
            continue
        j = head.index(col)
        out[key] = np.array([[float(r[j]) for r in sorted(rs, key=lambda r: float(r[i_t]))]
                             for rs in runs.values()])
    return out


def compare(a: np.ndarray, b: np.ndarray) -> dict:
    """a = NumPy, b = NetLogo (una statistica per replica)."""
    if a.mean() == 0 and b.mean() == 0:
        return {"numpy": 0.0, "netlogo": 0.0, "nota": "zero in entrambi"}
    return {"numpy": float(a.mean()), "netlogo": float(b.mean()), "rel_diff": float(b.mean() / a.mean() - 1),
            "p_value": float(stats.ttest_ind(a, b, equal_var=False).pvalue), **equivalence(a, b)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=30, help="repliche NetLogo per scenario")
    ap.add_argument("--np-reps", type=int, default=30, help="repliche NumPy per scenario")
    ap.add_argument("--threads", type=int, default=os.cpu_count() or 1)
    ap.add_argument("--csv-dir", default=None, help="usa le tabelle NetLogo già prodotte in questa cartella")
    ap.add_argument("--out", default=None)
    ap.add_argument("--esteso", action="store_true", help="modello esteso (ramo esteso): base, E2 ed E1")
    args = ap.parse_args()
    model = MODEL_ESTESO if args.esteso else MODEL
    scenarios = SCENARIOS_ESTESO if args.esteso else SCENARIOS
    args.out = args.out or str(ROOT / "report" / ("numeri_netlogo_esteso.json" if args.esteso else "numeri_netlogo.json"))
    out_dir = Path(args.csv_dir or ROOT / "outputs" / ("netlogo_esteso" if args.esteso else "netlogo"))
    out_dir.mkdir(parents=True, exist_ok=True)
    cfg = load_config(ROOT / "configs" / "base.yaml").with_overrides({"population.N": 5000})

    res = {"N": 5000, "repliche_netlogo": args.reps, "repliche_numpy": args.np_reps, "margine_equivalenza": MARGIN,
           "modello": str(model.relative_to(ROOT)), "scenari": {}}
    for name, ov in scenarios.items():
        t0 = time.perf_counter()
        table = out_dir / f"{name}.csv"
        if not args.csv_dir:
            home = Path(os.environ["NETLOGO_HOME"])
            table = run_netlogo(home, name, args.reps, args.threads, out_dir, model)
        nl = read_table(table)
        npr = run_replications(cfg.with_overrides(ov), args.np_reps)
        rows = {}
        for k in WHOLE:
            if k in nl:
                rows[k] = compare(npr[k].mean(axis=1), nl[k].mean(axis=1))
        for k in END:
            if k in nl:
                rows[f"{k}_fine"] = compare(npr[k][:, -5:].mean(axis=1), nl[k][:, -5:].mean(axis=1))
        res["scenari"][name] = rows
        worst = max((abs(r["rel_diff"]) for r in rows.values() if "rel_diff" in r), default=0)
        print(f"{name:16s} repliche NetLogo {nl['H'].shape[0]:3d}  differenza massima {worst:.2%}  "
              f"({time.perf_counter() - t0:.0f}s)", file=sys.stderr)
    Path(args.out).write_text(json.dumps(res, indent=1, ensure_ascii=False))
    for name, rows in res["scenari"].items():
        print(name)
        for k, r in rows.items():
            if "rel_diff" in r:
                lo, hi = r["ic90_rel"]
                print(f"  {k:15s} numpy={r['numpy']:.4f} netlogo={r['netlogo']:.4f} diff={r['rel_diff']:+.2%} "
                      f"p(diff)={r['p_value']:.2f} IC90=[{lo:+.2%}, {hi:+.2%}] p(equiv ±{MARGIN:.0%})={r['p_tost']:.4f}")


if __name__ == "__main__":
    main()
