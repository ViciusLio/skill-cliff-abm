"""T10a (D26): sensibilità globale (indici di Sobol) dei risultati principali ai parametri scelti a mano.

Parametri (intervalli uniformi intorno ai valori di base): p, kappa, beta, sigma, delta0, S_h, d, g, phi_max.
Le soglie junior/senior restano fisse: il ritardo dipende solo da loro (Proposizione 2), non serve stimarlo.
Risultati:
  B_inc      apprendimento da incontri dei junior nella base (bersaglio della calibrazione);
  perdita_H  H con IA sui compiti dei junior / H senza IA - 1, a fine orizzonte (numeri casuali comuni);
  eccesso    automazione dell'impresa (pi/c = 0,30) meno quella del pianificatore (rho = 0,97, 50 anni),
             come in scripts/automazione.py, su una griglia di phi costanti con interpolazione.
Stimatori di Saltelli (2010) per gli indici del primo ordine e di Jansen per quelli totali, su campioni
quasi casuali di Sobol (Saltelli et al. 2008); intervalli bootstrap al 95%. Una replica per punto con N = 5.000.

Produce report/numeri_sensibilita.json e le figure (report/fig in italiano, paper/fig in inglese).
Uso: python scripts/sensibilita.py [--base 64] [--N 5000]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from scipy.stats import qmc

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_report import AQUA, BLUE, ORANGE, ROOT, plt  # noqa: E402

from skillcliff import load_config  # noqa: E402
from skillcliff.ai import FixedAutomation  # noqa: E402
from skillcliff.experiment import default_workers  # noqa: E402
from skillcliff.model import run_model  # noqa: E402

PARAMS = {                              # chiave di configurazione: (minimo, massimo)
    "meetings.p": (0.3, 0.9),
    "meetings.kappa": (0.1, 0.4),
    "meetings.beta": (0.05, 0.15),
    "population.h0_sigma": (0.1, 0.3),
    "learning.delta0": (0.03, 0.05),
    "learning.horizon": (40.0, 60.0),
    "learning.depreciation": (0.008, 0.016),
    "ai.g": (0.01, 0.05),
    "ai.phi_max": (0.4, 0.8),
}
SYMBOLS = ["p", "κ", "β", "σ", "δ₀", "S_h", "d", "g", "φ_max"]
OUTPUTS = ("B_inc", "perdita_H", "eccesso")
PI, C, RHO, HORIZON = 0.10, 1 / 3, 0.97, 50
PHI_GRID = np.array([0.0, 0.1, 0.2, 0.3, 0.4])
FINE = np.linspace(0.0, 0.4, 401)


def evaluate(args):
    """I tre risultati per un punto dello spazio dei parametri (una replica, seed fissato)."""
    cfg0, values = args
    cfg = cfg0.with_overrides(dict(zip(PARAMS, values)))
    seed = lambda: np.random.SeedSequence(cfg.seed)   # noqa: E731  copia fresca per ogni modello
    base = run_model(cfg, seed())
    ai = run_model(cfg.with_overrides({"ai.enabled": True, "ai.target": "junior"}), seed())
    start = cfg.ai.start
    r = [np.ones(cfg.T)] + [run_model(cfg, seed(), FixedAutomation(cfg, phi=float(phi)))["H"] / base["H"]
                            for phi in PHI_GRID[1:]]
    r = np.stack(r, axis=1)                                         # (anni, griglia di phi)
    k = np.arange(min(HORIZON, cfg.T - start))
    w = RHO ** (k + 1)
    r_fine = np.stack([np.interp(FINE, PHI_GRID, r[start + kk]) for kk in k])
    value = (w[:, None] * r_fine).sum(0) * (1 + PI * FINE - C * FINE ** 2 / 2) / w.sum()
    return (float(base["B_meet"].mean()), float(ai["H"][-1] / base["H"][-1] - 1),
            float(PI / C - FINE[int(np.argmax(value))]))


def sobol_indices(fA, fB, fAB, rng, n_boot=500):
    """Primo ordine (Saltelli 2010) e totale (Jansen), con intervalli bootstrap al 95%."""
    def est(idx):
        a, b, ab = fA[idx], fB[idx], fAB[:, idx]
        v = np.var(np.concatenate([a, b]), ddof=1)
        s1 = np.mean(b * (ab - a), axis=1) / v
        st = 0.5 * np.mean((a - ab) ** 2, axis=1) / v
        return s1, st
    n = fA.size
    s1, st = est(np.arange(n))
    boot = [est(rng.integers(0, n, n)) for _ in range(n_boot)]
    b1, bt = np.array([b[0] for b in boot]), np.array([b[1] for b in boot])
    q = lambda x: np.percentile(x, [2.5, 97.5], axis=0)   # noqa: E731
    return s1, st, q(b1), q(bt)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "configs" / "base.yaml"))
    ap.add_argument("--base", type=int, default=64, help="punti base (potenza di 2)")
    ap.add_argument("--N", type=int, default=5000)
    args = ap.parse_args()
    t0 = time.perf_counter()
    cfg = load_config(args.config).with_overrides({"population.N": args.N})
    d = len(PARAMS)
    lo, hi = np.array([v[0] for v in PARAMS.values()]), np.array([v[1] for v in PARAMS.values()])
    u = qmc.Sobol(d=2 * d, scramble=True, seed=cfg.seed).random(args.base)
    A, B = lo + u[:, :d] * (hi - lo), lo + u[:, d:] * (hi - lo)
    AB = np.stack([np.where(np.arange(d) == i, B, A) for i in range(d)])        # (d, base, d)
    points = [A, B] + list(AB)
    jobs = [(cfg, row) for M in points for row in M]
    with ProcessPoolExecutor(max_workers=default_workers()) as ex:
        res = np.array(list(ex.map(evaluate, jobs, chunksize=4)))                # (punti, risultati)
    n = args.base
    fA, fB = res[:n], res[n:2 * n]
    fAB = res[2 * n:].reshape(d, n, -1)
    rng = np.random.default_rng(cfg.seed)
    num = {"N": args.N, "punti_base": n, "valutazioni": len(jobs), "intervalli": PARAMS, "risultati": {}}
    for j, name in enumerate(OUTPUTS):
        s1, st, c1, ct = sobol_indices(fA[:, j], fB[:, j], fAB[:, :, j], rng)
        allv = np.concatenate([fA[:, j], fB[:, j]])
        num["risultati"][name] = {
            "media": float(allv.mean()), "intervallo_90": [float(np.percentile(allv, 5)), float(np.percentile(allv, 95))],
            "minimo": float(res[:, j].min()), "massimo": float(res[:, j].max()),
            "quota_positiva": float((res[:, j] > 0).mean()), "punti": int(res.shape[0]),
            "indici": {k: {"S1": float(s1[i]), "S1_ic95": [float(c1[0, i]), float(c1[1, i])],
                           "ST": float(st[i]), "ST_ic95": [float(ct[0, i]), float(ct[1, i])]}
                       for i, k in enumerate(PARAMS)},
        }
    (ROOT / "report" / "numeri_sensibilita.json").write_text(json.dumps(num, indent=1, ensure_ascii=False))
    figures(num)
    print(json.dumps(num, ensure_ascii=False))
    print(f"sensibilità in {time.perf_counter() - t0:.0f}s ({len(jobs)} punti)", file=sys.stderr)


def figures(num):
    labels = {
        "it": ("report/fig/fig13_sensibilita_sobol.png",
               {"B_inc": "B da incontri (base)", "perdita_H": "perdita di H con IA (junior, compiti)",
                "eccesso": "eccesso di automazione (D15)"}, "indice totale di Sobol"),
        "en": ("paper/fig/fig13_sobol.pdf",
               {"B_inc": "$B^{inc}$ (baseline)", "perdita_H": "loss of H with AI (junior tasks)",
                "eccesso": "excess automation"}, "total Sobol index"),
    }
    for path, titles, ylab in labels.values():
        fig, axes = plt.subplots(1, 3, figsize=(11, 3.4), sharey=True)
        for ax, (name, c) in zip(axes, zip(OUTPUTS, (AQUA, BLUE, ORANGE))):
            idx = num["risultati"][name]["indici"]
            st = np.array([idx[k]["ST"] for k in PARAMS])
            err = np.abs(np.array([idx[k]["ST_ic95"] for k in PARAMS]).T - st)
            ax.bar(range(len(PARAMS)), st, color=c, yerr=err, capsize=2)
            ax.set_xticks(range(len(PARAMS)), SYMBOLS, fontsize=8)
            ax.set_title(titles[name], fontsize=9)
            ax.axhline(0, color="#52514e", linewidth=.8)
        axes[0].set_ylabel(ylab)
        fig.tight_layout()
        out = ROOT / path
        out.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out, bbox_inches="tight")
        plt.close(fig)


if __name__ == "__main__":
    main()
