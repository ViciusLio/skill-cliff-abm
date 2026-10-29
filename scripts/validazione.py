"""T6 (D24): validazione sulle coorti che entrano nel mercato del lavoro durante una recessione.

Esperimento (scripts/validazione.py, modulo CohortShock): una recessione di `duration` anni dall'anno 10;
in quegli anni chi cerca il primo lavoro resta non occupato con probabilità u e, con D19, ritenta l'anno
dopo. Nessuna regola del modello cambia. Le coorti si identificano con l'identificativo d'ingresso e, a
numeri casuali comuni, sono le stesse persone con e senza recessione: il confronto è persona per persona.

Bersaglio non usato nella calibrazione: la persistenza della perdita salariale, cioè quanto ne resta dopo
10 e 15 anni rispetto alla perdita iniziale. Riferimenti: Oreopoulos, von Wachter e Heisz (2012), perdite che
svaniscono dopo 8-10 anni (Canada); Kahn (2010), 6-7% iniziale per punto di disoccupazione e ancora 2,5%
dopo 15 anni (Stati Uniti), cioè circa il 40% della perdita iniziale.

Produce report/numeri_validazione.json e le figure in italiano (report/fig) e inglese (paper/fig).
Uso: python scripts/validazione.py [--reps 30] [--N 50000]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_report import AQUA, BLUE, INK2, ORANGE, ROOT, band, plt  # noqa: E402

from skillcliff import load_config  # noqa: E402
from skillcliff.ai import CohortShock  # noqa: E402
from skillcliff.experiment import default_workers, replication_seeds  # noqa: E402
from skillcliff.metrics import mean_ci  # noqa: E402
from skillcliff.model import Model  # noqa: E402

YEAR, DURATION = 10, 2                 # recessione negli anni 10 e 11 del periodo registrato
U_GRID = (0.1, 0.2, 0.4)               # quota di entranti non occupati in ciascun anno di recessione
HORIZON = 40                           # anni seguiti dopo l'ingresso
LIT = {"kahn_15": 2.5 / 6.5, "oreopoulos_10": 0.0}   # quota della perdita iniziale rimasta


def cohort_paths(cfg, seed_seq, u):
    """Salario medio (= h, senza IA) delle coorti entrate negli anni di recessione, con e senza shock.
    Ritorna (anni dall'ingresso, rapporto shock/base - 1) per coorte media, e la quota della coorte rimasta
    fuori almeno un anno."""
    # copia fresca del seme per ciascun modello: Model ne deriva i flussi con spawn(), che consuma il seme
    fresh = lambda: np.random.SeedSequence(seed_seq.entropy, spawn_key=seed_seq.spawn_key)  # noqa: E731
    runs = {"base": Model(cfg, fresh()), "shock": Model(cfg, fresh(), CohortShock(cfg, YEAR, DURATION, u))}
    for m in runs.values():
        for _ in range(cfg.burn_in):
            m.step(record=False)
    cohorts = {}                       # anno d'ingresso -> intervallo di uid (uguale nei due run)
    paths = {y: {"base": [], "shock": []} for y in range(YEAR, YEAR + DURATION)}
    ever_out = {y: set() for y in paths}
    for t in range(cfg.T):
        for name, m in runs.items():
            first = m.next_uid
            m.step(record=False)
            if name == "base":
                cohorts[t] = (first, m.next_uid)
        for y, (lo, hi) in cohorts.items():
            if y not in paths or t < y or t - y >= HORIZON:
                continue
            for name, m in runs.items():
                inside = (m.pop.uid >= lo) & (m.pop.uid < hi)
                paths[y][name].append(m.pop.h[inside].mean())
                if name == "shock":
                    ever_out[y].update(m.pop.uid[inside & m.pop.out].tolist())
    gaps = [np.array(paths[y]["shock"]) / np.array(paths[y]["base"]) - 1 for y in paths]
    k = min(len(g) for g in gaps)
    size = np.mean([cohorts[y][1] - cohorts[y][0] for y in paths])
    return np.mean([g[:k] for g in gaps], axis=0), np.mean([len(ever_out[y]) for y in paths]) / size


def _job(args):
    cfg, ss, u = args
    return cohort_paths(cfg, ss, u)


def figures(res, years):
    labels = {
        "it": ("report/fig/fig11_coorti_recessione.png", "Coorti entrate in una recessione: salario rispetto alla stessa coorte senza recessione",
               "anni dall'ingresso", "variazione %", "quota della perdita massima",
               "entranti non occupati: {}%", "Oreopoulos et al. (2012): svanisce in 8–10 anni", "Kahn (2010): ~40% dopo 15 anni"),
        "en": ("paper/fig/fig11_recession_cohorts.pdf", "Cohorts entering in a recession: wages relative to the same cohort without recession",
               "years since entry", "% change", "share of the largest loss",
               "non-employed entrants: {}%", "Oreopoulos et al. (2012): fades in 8–10 years", "Kahn (2010): ~40% after 15 years"),
    }
    for path, title, xl, yl, yl2, lab, oreo, kahn in labels.values():
        fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.8))
        for u, c in zip(U_GRID, (AQUA, BLUE, ORANGE)):
            band(a1, years, 100 * res[u]["gap"], c, lab.format(int(100 * u)))
            m = res[u]["gap"].mean(axis=0)
            a2.plot(years, m / m.min(), color=c, label=lab.format(int(100 * u)))
        a1.axhline(0, color=INK2, linewidth=.8)
        a1.set_xlabel(xl); a1.set_ylabel(yl); a1.legend(fontsize=8, loc="lower right")
        a2.axhline(0, color=INK2, linewidth=.8)
        a2.plot([10], [LIT["oreopoulos_10"]], "s", color="#0b0b0b", label=oreo)
        a2.plot([15], [LIT["kahn_15"]], "D", color="#52514e", label=kahn)
        a2.set_xlabel(xl); a2.set_ylabel(yl2); a2.legend(fontsize=7, loc="upper right")
        fig.suptitle(title, fontsize=11, fontweight="bold", x=0.01, ha="left")
        fig.tight_layout()
        out = ROOT / path
        out.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out, bbox_inches="tight")
        plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "configs" / "base.yaml"))
    ap.add_argument("--reps", type=int, default=30)
    ap.add_argument("--N", type=int, default=50_000)
    args = ap.parse_args()
    t0 = time.perf_counter()
    cfg = load_config(args.config).with_overrides({"population.N": args.N})
    seeds = replication_seeds(cfg, args.reps)
    res = {}
    with ProcessPoolExecutor(max_workers=default_workers()) as ex:
        for u in U_GRID:
            out = list(ex.map(_job, [(cfg, ss, u) for ss in seeds]))
            k = min(len(g) for g, _ in out)
            res[u] = {"gap": np.array([g[:k] for g, _ in out]), "fuori": np.array([f for _, f in out])}
    years = np.arange(res[U_GRID[0]]["gap"].shape[1])

    def ci(x):
        m, lo, hi = mean_ci(x)
        return {"media": float(m), "ic95": [float(lo), float(hi)]}

    num = {"N": args.N, "repliche": args.reps, "recessione": {"anno": YEAR, "durata": DURATION},
           "riferimenti_quota_rimasta": {"Kahn2010_15_anni": LIT["kahn_15"], "Oreopoulos2012_10_anni": LIT["oreopoulos_10"]},
           "scenari": {}}
    for u in U_GRID:
        g = res[u]["gap"]
        m = g.mean(axis=0)
        k_max = int(np.argmin(m))     # la perdita cresce finché dura la recessione
        num["scenari"][str(u)] = {
            "quota_coorte_rimasta_fuori_almeno_un_anno": ci(res[u]["fuori"]),
            "perdita_per_anni_dall_ingresso": {str(k): ci(g[:, k]) for k in (0, 1, 2, 5, 10, 15, 20, 30) if k < g.shape[1]},
            "anni_alla_perdita_massima": k_max,
            # rapporto tra medie (per replica il denominatore è rumoroso)
            "quota_rimasta_della_perdita_massima": {str(k): float(m[k] / m[k_max]) for k in (5, 10, 15, 20, 30) if k < g.shape[1]},
        }
    (ROOT / "report" / "numeri_validazione.json").write_text(json.dumps(num, indent=1, ensure_ascii=False))
    figures(res, years)
    print(json.dumps(num, ensure_ascii=False))
    print(f"validazione in {time.perf_counter() - t0:.0f}s", file=sys.stderr)


if __name__ == "__main__":
    main()
