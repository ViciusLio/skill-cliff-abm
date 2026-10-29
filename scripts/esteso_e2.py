"""E2 (ramo esteso, D30-D33): un'impresa rappresentativa sceglie ogni anno quanto automatizzare i compiti junior.

Regola: phi_t = phi_max * max(0, 1 - c_t / (w_J - chi * v_t)), con c_t = c0 / A_t il costo dell'IA, w_J il salario
medio dei junior e v_t il valore formativo di un anno da junior; chi = quota del valore formativo internalizzata
(0 = impresa miope, contratti incompleti come in Ide 2026).

Confronti, tutti a numeri casuali comuni con lo scenario senza IA (N = 50.000, 30 repliche):
- percorso esogeno di phi (fase 2) contro scelta dell'impresa con chi in {0; 0,25; 0,5; 0,75; 1};
- pianificatore che sceglie una quota costante (come D15, modulo FixedShareFirm);
- valore sociale W = somma rho^(k+1) (Y + S) / somma rho^(k+1) Y_senza_IA - 1 su 50 anni, dove S sono i
  risparmi dell'impresa dall'automazione;
- contributo sull'automazione equivalente: aliquota tau sul costo dell'IA con cui l'impresa miope sceglie
  come quella che internalizza chi*: 1 + tau_t = w_J / (w_J - chi* v_t).

Produce report/numeri_e2.json e le figure (report/fig in italiano, paper/fig in inglese).
Uso: python scripts/esteso_e2.py [--reps 30] [--N 50000]
"""
from __future__ import annotations

import argparse
import functools
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_report import BLUE, INK2, ORANGE, ROOT, band, plt  # noqa: E402

from skillcliff import load_config  # noqa: E402
from skillcliff.ai import FixedShareFirm  # noqa: E402
from skillcliff.experiment import run_replications  # noqa: E402
from skillcliff.metrics import mean_ci  # noqa: E402

CHI_GRID = (0.0, 0.25, 0.5, 0.75, 1.0)
PHI_GRID = (0.0, 0.1, 0.2, 0.3, 0.4, 0.5)          # 0,6 = phi_max: l'ultimo compito costa infinito
HORIZONS = (10, 25, 49)
SEQ = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#0d366b"]


def ci(x):
    m, lo, hi = mean_ci(x)
    return {"media": float(m), "ic95": [float(lo), float(hi)]}


def welfare(run, base, start, rho):
    """Valore scontato di output più risparmi, relativo allo scenario senza IA, per replica."""
    k = np.arange(base["Y"].shape[1] - start)
    w = rho ** (k + 1)
    num = ((run["Y"][:, start:] + run["savings"][:, start:]) * w).sum(1)
    return num / (base["Y"][:, start:] * w).sum(1) - 1


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "configs" / "base.yaml"))
    ap.add_argument("--reps", type=int, default=30)
    ap.add_argument("--N", type=int, default=50_000)
    args = ap.parse_args()
    t0 = time.perf_counter()
    cfg = load_config(args.config).with_overrides({"population.N": args.N})
    start, rho = cfg.ai.start, cfg.ai.rho
    on = cfg.with_overrides({"ai.enabled": True, "ai.target": "junior"})
    firm = on.with_overrides({"ai.endogenous": True})

    base = run_replications(cfg, args.reps)
    exo = run_replications(on, args.reps)
    chis = {c: run_replications(firm.with_overrides({"ai.chi": c}), args.reps) for c in CHI_GRID}
    plan = {p: run_replications(firm, args.reps, functools.partial(FixedShareFirm, phi=p)) for p in PHI_GRID}

    def row(r, with_w=True):
        out = {"phi": {str(k): float(r["phi"][:, start + k].mean()) for k in HORIZONS},
               "H": {str(k): ci(r["H"][:, start + k] / base["H"][:, start + k] - 1) for k in HORIZONS}}
        if with_w:   # lo scenario esogeno non ha i risparmi dell'impresa: W non confrontabile
            out["risparmi_su_Y_fine"] = float((r["savings"][:, -1] / r["Y"][:, -1]).mean())
            out["W"] = ci(welfare(r, base, start, rho))
        return out

    W_plan = {p: welfare(plan[p], base, start, rho).mean() for p in PHI_GRID}
    phi_star = max(W_plan, key=W_plan.get)
    W_chi = {c: welfare(chis[c], base, start, rho).mean() for c in CHI_GRID}
    chi_star = max(W_chi, key=W_chi.get)
    r = chis[chi_star]
    sl = slice(start, None)
    tau = r["w_firm"][:, sl] / (r["w_firm"][:, sl] - chi_star * r["v_firm"][:, sl]) - 1
    num = {
        "N": args.N, "repliche": args.reps, "c0": cfg.ai.c0, "rho": rho, "anni": list(HORIZONS),
        "esogeno": row(exo, with_w=False),
        "impresa": {str(c): row(chis[c]) for c in CHI_GRID},
        "pianificatore_quota_costante": {"W": {str(p): float(W_plan[p]) for p in PHI_GRID}, "phi_ottimo": phi_star},
        "chi_ottimo": chi_star,
        "contributo_equivalente": {"media": float(tau.mean()), "a_10_anni": float(tau[:, 10].mean()),
                                   "a_49_anni": float(tau[:, -1].mean())},
        "valore_formativo_su_salario_junior": float((chis[0.0]["v_firm"][:, sl] / chis[0.0]["w_firm"][:, sl]).mean()),
    }
    (ROOT / "report" / "numeri_e2.json").write_text(json.dumps(num, indent=1, ensure_ascii=False))
    figures(num, exo, chis, base, start)
    print(json.dumps(num, ensure_ascii=False))
    print(f"E2 in {time.perf_counter() - t0:.0f}s", file=sys.stderr)


def figures(num, exo, chis, base, start):
    years = np.arange(base["H"].shape[1])
    labels = {
        "it": ("report/fig/fig14_e2_impresa.png", "anno", "quota di compiti junior automatizzata (φ)",
               "capitale umano H rispetto a nessuna IA (%)", "φ esogeno (fase 2)", "impresa, χ = {}",
               "Impresa che sceglie quanto automatizzare (E2)"),
        "en": ("paper/fig/fig14_e2_firm.pdf", "year", "share of junior tasks automated (φ)",
               "human capital H relative to no AI (%)", "exogenous φ (phase 2)", "firm, χ = {}",
               "A firm that chooses how much to automate (E2)"),
    }
    for path, xl, y1, y2, lexo, lchi, title in labels.values():
        fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.8))
        a1.plot(years, exo["phi"].mean(0), color=ORANGE, linestyle="--", label=lexo)
        band(a2, years, 100 * (exo["H"] / base["H"] - 1), ORANGE, lexo, linestyle="--")
        for c, col in zip(CHI_GRID, SEQ):
            a1.plot(years, chis[c]["phi"].mean(0), color=col, label=lchi.format(str(c).replace(".", ",") if path.endswith("png") else c))
            band(a2, years, 100 * (chis[c]["H"] / base["H"] - 1), col, lchi.format(str(c).replace(".", ",") if path.endswith("png") else c))
        for ax, yl in ((a1, y1), (a2, y2)):
            ax.axvline(start, color=INK2, linewidth=1, linestyle=":")
            ax.set_xlabel(xl); ax.set_ylabel(yl)
        a2.axhline(0, color=INK2, linewidth=.8)
        a1.legend(fontsize=7, loc="upper left")
        fig.suptitle(title, fontsize=11, fontweight="bold", x=0.01, ha="left")
        fig.tight_layout()
        out = ROOT / path
        out.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out, bbox_inches="tight")
        plt.close(fig)


if __name__ == "__main__":
    main()
