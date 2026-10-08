"""Fase 2: l'IA. Confronta i bersagli della sostituzione con lo scenario senza IA (stesso seed)
e studia la corsa tra la crescita della produttività dell'IA e l'erosione del capitale umano.

Produce figure in report/fig (italiano) e paper/fig (inglese), report/numeri_fase2.json
e site/data/fase2.json.

Uso: python scripts/fase2.py [--reps 30] [--N 50000]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_report import AQUA, BLUE, INK2, ORANGE, ROOT, band, plt  # noqa: E402

from skillcliff import load_config  # noqa: E402
from skillcliff.ai import TARGETS  # noqa: E402
from skillcliff.experiment import run_replications, save_results  # noqa: E402
from skillcliff.metrics import mean_ci  # noqa: E402

YELLOW, MAGENTA = "#eda100", "#e87ba4"
TARGET_COLORS = dict(zip(TARGETS, (BLUE, ORANGE, AQUA, YELLOW, MAGENTA)))
G_GRID = (0.01, 0.02, 0.03, 0.04, 0.05, 0.06)
THETA_GRID = (0.0, 0.01, 0.02, 0.05, 0.1, 0.2)
THETA_LINES = (0.0, 0.02, 0.05, 0.1)

LABELS = {
    "it": {
        "dir": ROOT / "report" / "fig", "year": "anno",
        "targets": {"junior": "junior", "senior": "senior", "qualificati": "qualificati",
                    "non_qualificati": "non qualificati", "complementare": "complementare"},
        "H": "Capitale umano aggregato H rispetto a nessuna IA", "senior": "h medio dei senior rispetto a nessuna IA",
        "rel": "variazione %", "race": "La corsa: output Y rispetto a nessuna IA (bersaglio junior, g = 3%)",
        "map": "Output a fine orizzonte rispetto a nessuna IA (bersaglio junior)",
        "g": "g (crescita annua di A)", "theta": "θ (peso dell'IA nell'output)", "intro": "introduzione IA",
        "files": ("fig6_scenari_H.png", "fig7_scenari_senior.png", "fig8_corsa.png", "fig9_mappa_corsa.png"),
    },
    "en": {
        "dir": ROOT / "paper" / "fig", "year": "year",
        "targets": {"junior": "junior", "senior": "senior", "qualificati": "high-skilled",
                    "non_qualificati": "low-skilled", "complementare": "complementary"},
        "H": "Aggregate human capital H relative to no AI", "senior": "Mean senior h relative to no AI",
        "rel": "% change", "race": "The race: output Y relative to no AI (junior target, g = 3%)",
        "map": "End-of-horizon output relative to no AI (junior target)",
        "g": "g (annual growth of A)", "theta": "θ (weight of AI in output)", "intro": "AI introduced",
        "files": ("fig6_scenarios_H.pdf", "fig7_scenarios_senior.pdf", "fig8_race.pdf", "fig9_race_map.pdf"),
    },
}


def rel(res, base, key):
    """Variazione relativa per replica (accoppiata per seed): (repliche, T)."""
    return res[key] / base[key] - 1.0


def ci(x):
    m, lo, hi = mean_ci(x)
    return {"media": float(m), "ic95": [float(lo), float(hi)]}


def first_effect(res, base, key, start):
    gap = np.abs(res[key] - base[key]).max(axis=0)
    after = np.flatnonzero(gap[start:] > 0)
    return int(after[0]) if after.size else None


def save(fig, L, i):
    L["dir"].mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(L["dir"] / L["files"][i], bbox_inches="tight")
    plt.close(fig)


def figures(L, years, start, scen, base, race_rel, A_path, num):
    for i, key, title in ((0, "H", L["H"]), (1, "mean_h_senior", L["senior"])):
        fig, ax = plt.subplots(figsize=(7.2, 4))
        for t in TARGETS:
            band(ax, years, 100 * rel(scen[t], base, key), TARGET_COLORS[t], L["targets"][t])
        ax.axvline(start, color=INK2, linewidth=1, linestyle=":")
        ax.axhline(0, color=INK2, linewidth=.8)
        ax.set_title(title); ax.set_xlabel(L["year"]); ax.set_ylabel(L["rel"])
        ax.legend(fontsize=8, loc="lower left")
        save(fig, L, i)

    fig, ax = plt.subplots(figsize=(7.2, 4))
    seq = ["#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]
    for th, c in zip(THETA_LINES, seq):
        y = 100 * ((1 + race_rel[0.03]) * (1 + th * (A_path[0.03] - 1)) - 1)
        band(ax, years, y, c, f"θ = {th}")
    ax.axvline(start, color=INK2, linewidth=1, linestyle=":")
    ax.axhline(0, color=INK2, linewidth=.8)
    ax.set_title(L["race"]); ax.set_xlabel(L["year"]); ax.set_ylabel(L["rel"])
    ax.legend(fontsize=8, loc="upper left")
    save(fig, L, 2)

    grid = np.array(num["corsa"]["mappa_Y_fine"]) * 100
    fig, ax = plt.subplots(figsize=(6.4, 4))
    lim = max(1.0, np.abs(grid).max())
    from matplotlib.colors import LinearSegmentedColormap, SymLogNorm
    cmap = LinearSegmentedColormap.from_list("div", ["#d95926", "#e4e3df", "#2a78d6"])
    im = ax.imshow(grid, origin="lower", aspect="auto", cmap=cmap,
                   norm=SymLogNorm(linthresh=1.0, vmin=-lim, vmax=lim))
    ax.set_xticks(range(len(THETA_GRID)), [str(t) for t in THETA_GRID])
    ax.set_yticks(range(len(G_GRID)), [f"{g:.0%}" for g in G_GRID])
    for (r, c), v in np.ndenumerate(grid):
        ax.text(c, r, f"{v:+.1f}%", ha="center", va="center", fontsize=7, color="#0b0b0b")
    ax.set_xlabel(L["theta"]); ax.set_ylabel(L["g"]); ax.set_title(L["map"])
    ax.grid(False)
    fig.colorbar(im, ax=ax, label=L["rel"])
    save(fig, L, 3)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "configs" / "base.yaml"))
    ap.add_argument("--reps", type=int, default=30)
    ap.add_argument("--race-reps", type=int, default=10)
    ap.add_argument("--N", type=int, default=50_000)
    args = ap.parse_args()
    t0 = time.perf_counter()

    cfg = load_config(args.config).with_overrides({"population.N": args.N})
    start, years = cfg.ai.start, np.arange(cfg.T)
    on = lambda target, **kw: cfg.with_overrides({"ai.enabled": True, "ai.target": target,  # noqa: E731
                                                  **{f"ai.{k}": v for k, v in kw.items()}})

    base = run_replications(cfg, args.reps)
    scen = {t: run_replications(on(t), args.reps) for t in TARGETS}
    save_results(ROOT / "outputs" / "fase2" / "base.npz", cfg, base)
    for t, r in scen.items():
        save_results(ROOT / "outputs" / "fase2" / f"{t}.npz", on(t), r)

    # La corsa (bersaglio junior): theta non entra nella dinamica, quindi Y/Y_base si calcola
    # per qualsiasi theta da H/H_base e da A(t).
    base_r = run_replications(cfg, args.race_reps)
    race_rel, A_path = {}, {}
    for g in G_GRID:
        r = scen["junior"] if (g == cfg.ai.g and args.race_reps == args.reps) else \
            run_replications(on("junior", g=g), args.race_reps)
        b = base if r is scen["junior"] else base_r
        race_rel[g] = rel(r, b, "H")
        A_path[g] = r["A"][0]
    end = cfg.T - 1
    mappa = [[float(((1 + race_rel[g][:, end]) * (1 + th * (A_path[g][end] - 1)) - 1).mean())
              for th in THETA_GRID] for g in G_GRID]
    breakeven = {f"{g:.2f}": float((1 / (1 + race_rel[g][:, end].mean()) - 1) / (A_path[g][end] - 1)) for g in G_GRID}

    num = {
        "N": args.N, "repliche": args.reps, "anni": cfg.T, "introduzione": start,
        "parametri_ia": {"g": cfg.ai.g, "phi_max": cfg.ai.phi_max, "theta": cfg.ai.theta},
        "phi_dopo_10_anni": float(scen["junior"]["phi"][0, start + 10]),
        "scenari": {
            t: {
                "H_fine": ci(rel(scen[t], base, "H")[:, end]),
                "h_senior_fine": ci(rel(scen[t], base, "mean_h_senior")[:, end]),
                "h_junior_fine": ci(rel(scen[t], base, "mean_h_junior")[:, end]),
                "B_inc_fine": ci(scen[t]["B_meet"][:, -5:].mean(1) / base["B_meet"][:, -5:].mean(1) - 1),
                "Y_fine_theta_0.02": ci(rel(scen[t], base, "Y")[:, end]),
                "gini_fine": ci(scen[t]["gini_w"][:, -5:].mean(1)),
                "primo_effetto_senior_anni_dopo": first_effect(scen[t], base, "mean_h_senior", start),
                "primo_effetto_H_anni_dopo": first_effect(scen[t], base, "H", start),
            }
            for t in TARGETS
        },
        "gini_base_fine": ci(base["gini_w"][:, -5:].mean(1)),
        "corsa": {"g": list(G_GRID), "theta": list(THETA_GRID), "mappa_Y_fine": mappa,
                  "theta_pareggio_fine": breakeven,
                  "H_fine_per_g": {f"{g:.2f}": ci(race_rel[g][:, end]) for g in G_GRID}},
    }
    (ROOT / "report" / "numeri_fase2.json").write_text(json.dumps(num, indent=1, ensure_ascii=False))

    for L in LABELS.values():
        figures(L, years, start, scen, base, race_rel, A_path, num)

    def series(x):
        m, lo, hi = mean_ci(x)
        return {"m": np.round(m, 6).tolist(), "lo": np.round(lo, 6).tolist(), "hi": np.round(hi, 6).tolist()}

    site = {
        "years": years.tolist(), "start": start, "numbers": num,
        "labels": LABELS["it"]["targets"],
        "targets": {t: {k: series(rel(scen[t], base, k)) for k in ("H", "mean_h_senior", "mean_h_junior", "B_meet")}
                    for t in TARGETS},
        "race": {f"{g:.2f}": {"H": series(race_rel[g]), "A": np.round(A_path[g], 6).tolist()} for g in G_GRID},
    }
    (ROOT / "site" / "data" / "fase2.json").write_text(json.dumps(site, ensure_ascii=False))
    print(f"fase 2 in {time.perf_counter() - t0:.0f}s", file=sys.stderr)
    print(json.dumps({k: v for k, v in num.items() if k != "corsa"}, ensure_ascii=False))
    print(json.dumps(num["corsa"]["theta_pareggio_fine"]))


if __name__ == "__main__":
    main()
