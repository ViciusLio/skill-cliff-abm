"""T9: politiche quantificate. Quattro leve che usano parametri esistenti, applicate dall'arrivo dell'IA con la
stessa intensità (10% del proprio parametro), confrontate con una metrica comune: la quota della perdita di
capitale umano dovuta all'IA che la leva recupera dopo 10, 25 e 50 anni.

Leve (modulo Policy):  p     apprendistati, più occasioni di lavorare accanto a un senior
                       kappa capacità di mentoring riservata nelle imprese
                       beta  IA che aiuta i senior a insegnare
                       phi   contributo sull'automazione dei compiti d'ingresso (phi * 0,9)
Contesti: l'IA toglie compiti ai junior con mentori abbondanti (base); i senior perdono il posto con mentori
scarsi (kappa = 0,1).

Nel modello non ci sono prezzi: stessa intensità non vuol dire stesso costo. L'output non dipende da phi, quindi
il costo in output del contributo sull'automazione si legge nell'esercizio D15 (scripts/automazione.py).
Uso: python scripts/politiche.py [--reps 30] [--N 50000]
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
from make_report import AQUA, BLUE, ORANGE, ROOT, plt  # noqa: E402

from skillcliff import load_config  # noqa: E402
from skillcliff.ai import Policy  # noqa: E402
from skillcliff.experiment import run_replications  # noqa: E402
from skillcliff.metrics import mean_ci  # noqa: E402

SIZE = 0.10
LEVERS = ("p", "kappa", "beta", "phi")
HORIZONS = (10, 25, 49)
CONTEXTS = {
    "junior_compiti": {"overrides": {}, "ai": {"ai.target": "junior"}},
    "senior_posto_kappa_0.1": {"overrides": {"meetings.kappa": 0.1},
                               "ai": {"ai.target": "senior", "ai.margin_senior": "posto"}},
}
YELLOW = "#eda100"


def ci(x):
    m, lo, hi = mean_ci(x)
    return {"media": float(m), "ic95": [float(lo), float(hi)]}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "configs" / "base.yaml"))
    ap.add_argument("--reps", type=int, default=30)
    ap.add_argument("--N", type=int, default=50_000)
    args = ap.parse_args()
    t0 = time.perf_counter()
    cfg0 = load_config(args.config).with_overrides({"population.N": args.N})
    start = cfg0.ai.start
    num = {"N": args.N, "repliche": args.reps, "intensita": SIZE, "anni": list(HORIZONS), "contesti": {}}
    for name, c in CONTEXTS.items():
        cfg = cfg0.with_overrides(c["overrides"])
        cfg_ai = cfg.with_overrides({"ai.enabled": True, **c["ai"]})
        no_ai = run_replications(cfg, args.reps)
        ai = run_replications(cfg_ai, args.reps)
        loss = {k: no_ai["H"][:, start + k] - ai["H"][:, start + k] for k in HORIZONS}
        row = {"perdita_H_senza_politiche": {str(k): ci(ai["H"][:, start + k] / no_ai["H"][:, start + k] - 1)
                                             for k in HORIZONS}, "leve": {}}
        for lever in LEVERS:
            pol = run_replications(cfg_ai, args.reps, functools.partial(Policy, lever=lever, size=SIZE))
            row["leve"][lever] = {
                "quota_recuperata": {str(k): ci((pol["H"][:, start + k] - ai["H"][:, start + k]) / loss[k])
                                     for k in HORIZONS},
                "H_rispetto_a_IA_senza_politiche": {str(k): ci(pol["H"][:, start + k] / ai["H"][:, start + k] - 1)
                                                    for k in HORIZONS},
            }
        num["contesti"][name] = row
        print(f"{name}: {time.perf_counter() - t0:.0f}s", file=sys.stderr)
    (ROOT / "report" / "numeri_politiche.json").write_text(json.dumps(num, indent=1, ensure_ascii=False))
    figures(num)
    print(json.dumps(num, ensure_ascii=False))


def figures(num):
    labels = {
        "it": ("report/fig/fig12_politiche.png",
               {"junior_compiti": "IA toglie compiti ai junior (mentori abbondanti)",
                "senior_posto_kappa_0.1": "i senior perdono il posto (mentori scarsi, κ = 0,1)"},
               {"p": "apprendistati\n(p +10%)", "kappa": "mentoring\n(κ +10%)", "beta": "IA che insegna\n(β +10%)",
                "phi": "contributo\nautomazione\n(φ −10%)"},
               "quota della perdita di H recuperata", "dopo {} anni"),
        "en": ("paper/fig/fig12_policies.pdf",
               {"junior_compiti": "AI removes junior tasks (abundant mentors)",
                "senior_posto_kappa_0.1": "seniors lose their jobs (scarce mentors, κ = 0.1)"},
               {"p": "apprenticeships\n(p +10%)", "kappa": "mentoring\n(κ +10%)", "beta": "AI that teaches\n(β +10%)",
                "phi": "automation\ncontribution\n(φ −10%)"},
               "share of the loss of H recovered", "after {} years"),
    }
    for path, ctx_lab, lev_lab, ylab, hlab in labels.values():
        fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
        for ax, (ctx, row) in zip(axes, num["contesti"].items()):
            x = np.arange(len(LEVERS))
            for j, (k, c) in enumerate(zip(HORIZONS, (AQUA, BLUE, ORANGE))):
                vals = [100 * row["leve"][lv]["quota_recuperata"][str(k)]["media"] for lv in LEVERS]
                ax.bar(x + (j - 1) * 0.26, vals, width=0.26, color=c, label=hlab.format(k + 1 if k == 49 else k))
            ax.set_xticks(x, [lev_lab[lv] for lv in LEVERS], fontsize=8)
            ax.axhline(0, color="#52514e", linewidth=.8)
            ax.set_title(ctx_lab[ctx], fontsize=9)
        axes[0].set_ylabel(ylab + " (%)")
        axes[0].legend(fontsize=8)
        fig.tight_layout()
        out = ROOT / path
        out.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out, bbox_inches="tight")
        plt.close(fig)


if __name__ == "__main__":
    main()
