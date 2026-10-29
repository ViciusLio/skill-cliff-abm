"""E1 (ramo esteso, D34-D36): l'IA come tutor. Quando compensa la perdita di incontri?

Il junior occupato impara anche dall'IA: beta_ai * f_j * max(0, codifiable * hbar_S - h_j), con hbar_S il capitale
umano medio dei senior della sua qualifica; l'apprendimento autonomo dei junior si riduce di (1 - effort * f_j).
Griglia beta_ai in {0; 0,05; 0,10} e effort in {0; 0,25; 0,5} (quota codificabile 0,5), più quota codificabile
0,75 e 1 senza calo dello sforzo, in tre scenari di sostituzione (compiti dei junior,
posto dei junior, compiti dei senior). Metrica: H rispetto allo scenario senza IA e quota della perdita dovuta all'IA
che il tutor compensa, a numeri casuali comuni. N = 50.000, 30 repliche.

Produce report/numeri_e1.json e le figure (report/fig in italiano, paper/fig in inglese).
Uso: python scripts/esteso_e1.py [--reps 30] [--N 50000]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_report import AQUA, BLUE, INK2, ORANGE, ROOT, plt  # noqa: E402

from skillcliff import load_config  # noqa: E402
from skillcliff.experiment import run_replications  # noqa: E402
from skillcliff.metrics import mean_ci  # noqa: E402

BETAS = (0.0, 0.05, 0.10)
EFFORTS = (0.0, 0.25, 0.5)
CODIFIABLE = (0.75, 1.0)          # oltre al valore centrale 0,5
HORIZONS = (10, 25, 49)
SCENARIOS = {
    "junior_compiti": {"ai.target": "junior"},
    "junior_posto": {"ai.target": "junior", "ai.margin_junior": "posto"},
    "senior_compiti": {"ai.target": "senior"},
}


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
    cfg = load_config(args.config).with_overrides({"population.N": args.N})
    start = cfg.ai.start
    base = run_replications(cfg, args.reps)
    num = {"N": args.N, "repliche": args.reps, "codifiable": cfg.ai.codifiable, "anni": list(HORIZONS), "scenari": {}}
    for name, ov in SCENARIOS.items():
        on = cfg.with_overrides({"ai.enabled": True, **ov})
        no_tutor = run_replications(on, args.reps)
        loss = base["H"][:, -1] - no_tutor["H"][:, -1]
        grid = {}
        for b in BETAS:
            for e in EFFORTS:
                if b == 0 and e == 0:
                    r = no_tutor
                else:
                    r = run_replications(on.with_overrides({"ai.tutor": True, "ai.beta_ai": b, "ai.effort": e}), args.reps)
                grid[f"{b}_{e}"] = {
                    "beta_ai": b, "effort": e,
                    "H": {str(k): ci(r["H"][:, start + k] / base["H"][:, start + k] - 1) for k in HORIZONS},
                    "quota_perdita_compensata_fine": ci((r["H"][:, -1] - no_tutor["H"][:, -1]) / loss),
                    "B_tutor_fine": float(r["B_tutor"][:, -5:].mean()),
                    "B_meet_fine": float(r["B_meet"][:, -5:].mean()),
                    "B_aut_fine": float(r["B_aut"][:, -5:].mean()),
                }
        num["scenari"][name] = grid
        # quota codificabile: da essa dipende se il tutor arriva sopra il livello dei junior (estensione di D36)
        sens = {}
        for c in CODIFIABLE:
            for b in (0.05, 0.10):
                r = run_replications(on.with_overrides({"ai.tutor": True, "ai.beta_ai": b, "ai.codifiable": c}), args.reps)
                sens[f"{c}_{b}"] = {"codifiable": c, "beta_ai": b,
                                    "H_fine": ci(r["H"][:, -1] / base["H"][:, -1] - 1),
                                    "quota_perdita_compensata_fine": ci((r["H"][:, -1] - no_tutor["H"][:, -1]) / loss)}
        num["sensibilita_codificabile"] = num.get("sensibilita_codificabile", {})
        num["sensibilita_codificabile"][name] = sens
        print(f"{name}: {time.perf_counter() - t0:.0f}s", file=sys.stderr)
    (ROOT / "report" / "numeri_e1.json").write_text(json.dumps(num, indent=1, ensure_ascii=False))
    figures(num)
    print(json.dumps(num, ensure_ascii=False))


def figures(num):
    labels = {
        "it": ("report/fig/fig15_e1_tutor.png",
               {"junior_compiti": "IA toglie compiti ai junior", "junior_posto": "i junior perdono il posto",
                "senior_compiti": "IA toglie compiti ai senior"},
               "efficacia del tutor β_IA", "H dopo 50 anni rispetto a nessuna IA (%)", "calo dello sforzo ε = {}",
               "L'IA come tutor (E1)", lambda x: str(x).replace(".", ",")),
        "en": ("paper/fig/fig15_e1_tutor.pdf",
               {"junior_compiti": "AI removes junior tasks", "junior_posto": "juniors lose their jobs",
                "senior_compiti": "AI removes senior tasks"},
               "tutor effectiveness β_AI", "H after 50 years relative to no AI (%)", "effort reduction ε = {}",
               "AI as a tutor (E1)", str),
    }
    for path, titles, xl, yl, leg, title, fmt in labels.values():
        fig, axes = plt.subplots(1, 3, figsize=(11, 3.6), sharey=True)
        for ax, (name, grid) in zip(axes, num["scenari"].items()):
            x = np.arange(len(BETAS))
            for j, (e, c) in enumerate(zip(EFFORTS, (AQUA, BLUE, ORANGE))):
                vals = [100 * grid[f"{b}_{e}"]["H"]["49"]["media"] for b in BETAS]
                ax.bar(x + (j - 1) * 0.26, vals, width=0.26, color=c, label=leg.format(fmt(e)))
            ax.set_xticks(x, [fmt(b) for b in BETAS])
            ax.axhline(0, color=INK2, linewidth=.8)
            ax.set_title(titles[name], fontsize=9); ax.set_xlabel(xl)
        axes[0].set_ylabel(yl); axes[0].legend(fontsize=7)
        fig.suptitle(title, fontsize=11, fontweight="bold", x=0.01, ha="left")
        fig.tight_layout()
        out = ROOT / path
        out.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out, bbox_inches="tight")
        plt.close(fig)


if __name__ == "__main__":
    main()
