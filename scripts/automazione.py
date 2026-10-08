"""D15: automazione scelta dall'impresa contro automazione ottimale per la società.

Dall'anno t0 una quota costante phi dei compiti junior è automatizzata (p * (1 - phi)).
Output netto relativo allo scenario senza automazione:
    y_t(phi) = r_t(phi) * (1 + pi*phi - c*phi^2/2),   r_t(phi) = H_t(phi) / H_t(0)
- Impresa: prende il capitale umano come dato (i contratti di trasmissione della conoscenza
  sono incompleti, Ide 2026) e massimizza il termine tra parentesi: phi_impresa = pi / c.
- Pianificatore: massimizza sum_{k=0..orizzonte-1} rho^(k+1) y_{t0+k}(phi), cioè tiene conto
  di come phi abbassa il capitale umano negli anni successivi (r_t dal modello).
L'eccesso di automazione è phi_impresa - phi_pianificatore.

Uso: python scripts/automazione.py [--reps 10] [--N 50000]
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
from make_report import BLUE, INK2, ORANGE, ROOT, plt  # noqa: E402

from skillcliff import load_config  # noqa: E402
from skillcliff.ai import FixedAutomation  # noqa: E402
from skillcliff.experiment import run_replications  # noqa: E402

PI, C = 0.10, 1 / 3                    # guadagno pieno dell'automazione e costo di adozione
PHI_GRID = np.round(np.arange(0.0, 0.61, 0.05), 2)
HORIZONS = (10, 25, 50)
RHOS = (0.97, 0.99)
FINE = np.linspace(0.0, 0.6, 601)

LABELS = {
    "it": {"dir": ROOT / "report" / "fig", "file": "fig10_automazione.png",
           "title": "Automazione dei compiti junior: impresa contro pianificatore (ρ = 0,97)",
           "x": "φ (quota di compiti junior automatizzata)", "y": "valore scontato dell'output netto (relativo)",
           "firm": "scelta dell'impresa", "hz": "pianificatore, orizzonte {} anni"},
    "en": {"dir": ROOT / "paper" / "fig", "file": "fig10_automation.pdf",
           "title": "Automating junior tasks: firm versus planner (ρ = 0.97)",
           "x": "φ (share of junior tasks automated)", "y": "discounted net output (relative)",
           "firm": "firm's choice", "hz": "planner, {}-year horizon"},
}


def objective(r_fine, rho, horizon, start):
    """Valore scontato dell'output netto, normalizzato sullo scenario senza automazione."""
    k = np.arange(horizon)                 # anni t0, ..., t0 + orizzonte - 1
    w = rho ** (k + 1)
    static = 1 + PI * FINE - C * FINE ** 2 / 2
    return (w[:, None] * r_fine[start + k, :]).sum(0) * static / w.sum()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "configs" / "base.yaml"))
    ap.add_argument("--reps", type=int, default=10)
    ap.add_argument("--N", type=int, default=50_000)
    args = ap.parse_args()
    t0 = time.perf_counter()
    cfg = load_config(args.config).with_overrides({"population.N": args.N})
    start = cfg.ai.start

    runs = {phi: run_replications(cfg, args.reps, ai_factory=functools.partial(FixedAutomation, phi=float(phi)))
            for phi in PHI_GRID}
    base = runs[0.0]["H"]
    r = np.stack([(runs[phi]["H"] / base).mean(0) for phi in PHI_GRID], axis=1)   # (T, griglia)
    r_fine = np.stack([np.interp(FINE, PHI_GRID, r[t]) for t in range(r.shape[0])])

    phi_firm = PI / C
    out = {"pi": PI, "c": C, "phi_impresa": phi_firm, "N": args.N, "repliche": args.reps,
           "H_fine_per_phi": {f"{p:.2f}": float(r[-1, i] - 1) for i, p in enumerate(PHI_GRID)},
           "pianificatore": {}}
    for rho in RHOS:
        for hz in HORIZONS:
            obj = objective(r_fine, rho, hz, start)
            i_soc = int(obj.argmax())
            i_firm = int(np.abs(FINE - phi_firm).argmin())
            out["pianificatore"][f"rho={rho},orizzonte={hz}"] = {
                "phi_ottimo": float(FINE[i_soc]),
                "eccesso_di_automazione": float(phi_firm - FINE[i_soc]),
                "perdita_di_benessere_scelta_impresa": float(1 - obj[i_firm] / obj[i_soc]),
                "valore_ottimo": float(obj[i_soc] - 1),
                "valore_scelta_impresa": float(obj[i_firm] - 1),
            }
    (ROOT / "report" / "numeri_d15.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))

    colors = ["#86b6ef", BLUE, "#0d366b"]
    for L in LABELS.values():
        fig, ax = plt.subplots(figsize=(7.2, 4))
        for hz, c in zip(HORIZONS, colors):
            obj = objective(r_fine, 0.97, hz, start)
            y = 100 * (obj - 1)
            ax.plot(FINE, y, color=c, label=L["hz"].format(hz))
            i = int(obj.argmax())
            ax.plot(FINE[i], y[i], "o", color=c, markersize=8, markeredgecolor="#fcfcfb", markeredgewidth=2)
        ax.axvline(phi_firm, color=ORANGE, linewidth=2, linestyle="--", label=L["firm"])
        ax.axhline(0, color=INK2, linewidth=.8)
        ax.set_title(L["title"]); ax.set_xlabel(L["x"]); ax.set_ylabel(L["y"] + " %")
        ax.legend(fontsize=8, loc="lower left")
        L["dir"].mkdir(parents=True, exist_ok=True)
        fig.tight_layout(); fig.savefig(L["dir"] / L["file"], bbox_inches="tight"); plt.close(fig)

    print(f"D15 in {time.perf_counter() - t0:.0f}s", file=sys.stderr)
    print(json.dumps(out["pianificatore"], indent=1))
    print("H a fine orizzonte per phi:", {k: round(v, 4) for k, v in out["H_fine_per_phi"].items()})


if __name__ == "__main__":
    main()
