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
from skillcliff.experiment import run_replications, save_results  # noqa: E402
from skillcliff.metrics import mean_ci  # noqa: E402

YELLOW, MAGENTA = "#eda100", "#e87ba4"
GREEN, VIOLET = "#008300", "#7b5cd6"
# Scenari (D16): bersaglio e margine della sostituzione. "compiti" è il default per junior e senior;
# "posto" vuol dire junior non occupati (D13) o senior che escono (meno mentori, kappa giù).
SCENARIOS = {
    "junior": {"target": "junior"},
    "junior_posto": {"target": "junior", "margin_junior": "posto"},
    "senior": {"target": "senior"},
    "senior_posto": {"target": "senior", "margin_senior": "posto"},
    "qualificati": {"target": "qualificati"},
    "non_qualificati": {"target": "non_qualificati"},
    "complementare": {"target": "complementare"},
}
TARGET_COLORS = dict(zip(SCENARIOS, (BLUE, GREEN, ORANGE, VIOLET, AQUA, YELLOW, MAGENTA)))
KAPPA_GRID = (0.05, 0.1, 0.2)
G_GRID = (0.01, 0.02, 0.03, 0.04, 0.05, 0.06)
THETA_GRID = (0.0, 0.01, 0.02, 0.05, 0.1, 0.2)
THETA_LINES = (0.0, 0.02, 0.05, 0.1)
GAMMA_GRID = (0.05, 0.1, 0.2, 1.0)      # D18: aggiornamento della familiarità
HORIZONS = (10, 25, 49)                 # anni dopo l'introduzione (49 = fine orizzonte)

LABELS = {
    "it": {
        "dir": ROOT / "report" / "fig", "year": "anno",
        "targets": {"junior": "junior, compiti (p)", "junior_posto": "junior, posto (non occupati)",
                    "senior": "senior, compiti (β)", "senior_posto": "senior, posto (κ)",
                    "qualificati": "qualificati", "non_qualificati": "non qualificati",
                    "complementare": "complementare"},
        "H": "Capitale umano aggregato H rispetto a nessuna IA", "senior": "h medio dei senior rispetto a nessuna IA",
        "rel": "variazione %", "race": "La corsa: output Y rispetto a nessuna IA (bersaglio junior, g = 3%)",
        "map": "Output a fine orizzonte rispetto a nessuna IA (bersaglio junior)",
        "g": "g (crescita annua di A)", "theta": "θ (peso dell'IA nell'output)", "intro": "introduzione IA",
        "files": ("fig6_scenari_H.png", "fig7_scenari_senior.png", "fig8_corsa.png", "fig9_mappa_corsa.png"),
    },
    "en": {
        "dir": ROOT / "paper" / "fig", "year": "year",
        "targets": {"junior": "junior, tasks (p)", "junior_posto": "junior, jobs (non-employed)",
                    "senior": "senior, tasks (β)", "senior_posto": "senior, jobs (κ)",
                    "qualificati": "high-skilled", "non_qualificati": "low-skilled",
                    "complementare": "complementary"},
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


def y_rel(h_rel, A, F, theta):
    """Y / Y_base - 1 per un theta qualsiasi: Y = H (1 + theta (A - 1) F), Y_base = H_base (D18)."""
    return (1 + h_rel) * (1 + theta * (A - 1) * F) - 1


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


def figures(L, years, start, scen, base, race_rel, A_path, race_F, num):
    for i, key, title in ((0, "H", L["H"]), (1, "mean_h_senior", L["senior"])):
        fig, ax = plt.subplots(figsize=(7.2, 4))
        for t in SCENARIOS:
            band(ax, years, 100 * rel(scen[t], base, key), TARGET_COLORS[t], L["targets"][t],
                 linestyle="--" if t == "senior" else "-")   # coincide quasi con junior (Prop. 1)
        ax.axvline(start, color=INK2, linewidth=1, linestyle=":")
        ax.axhline(0, color=INK2, linewidth=.8)
        ax.set_title(title); ax.set_xlabel(L["year"]); ax.set_ylabel(L["rel"])
        ax.legend(fontsize=8, loc="lower left")
        save(fig, L, i)

    fig, ax = plt.subplots(figsize=(7.2, 4))
    seq = ["#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]
    for th, c in zip(THETA_LINES, seq):
        y = 100 * y_rel(race_rel[0.03], A_path[0.03], race_F[0.03], th)
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
    ap.add_argument("--race-reps", type=int, default=30)
    ap.add_argument("--N", type=int, default=50_000)
    args = ap.parse_args()
    t0 = time.perf_counter()

    cfg = load_config(args.config).with_overrides({"population.N": args.N})
    start, years = cfg.ai.start, np.arange(cfg.T)
    on = lambda target, **kw: cfg.with_overrides({"ai.enabled": True, "ai.target": target,  # noqa: E731
                                                  **{f"ai.{k}": v for k, v in kw.items()}})

    base = run_replications(cfg, args.reps)
    scen = {name: run_replications(on(**kw), args.reps) for name, kw in SCENARIOS.items()}
    save_results(ROOT / "outputs" / "fase2" / "base.npz", cfg, base)
    for t, r in scen.items():
        save_results(ROOT / "outputs" / "fase2" / f"{t}.npz", cfg, r)

    # La corsa (bersaglio junior): theta non entra nella dinamica, quindi Y/Y_base si calcola
    # per qualsiasi theta da H/H_base e da A(t).
    base_r = run_replications(cfg, args.race_reps)
    race_rel, A_path, race_F = {}, {}, {}
    for g in G_GRID:
        r = scen["junior"] if (g == cfg.ai.g and args.race_reps == args.reps) else \
            run_replications(on("junior", g=g), args.race_reps)
        b = base if r is scen["junior"] else base_r
        race_rel[g] = rel(r, b, "H")
        A_path[g] = r["A"][0]
        race_F[g] = r["F_U"]
    end = cfg.T - 1
    mappa = [[float(y_rel(race_rel[g][:, end], A_path[g][end], race_F[g][:, end], th).mean())
              for th in THETA_GRID] for g in G_GRID]
    breakeven = {f"{g:.2f}": float(((1 / (1 + race_rel[g][:, end]) - 1)
                                    / ((A_path[g][end] - 1) * race_F[g][:, end])).mean()) for g in G_GRID}
    # Quota del guadagno dell'IA assorbita dalla perdita di capitale umano (bersaglio junior, g e theta di base).
    th0, g0 = cfg.ai.theta, cfg.ai.g
    absorbed = {}
    for k in HORIZONS:
        t = start + k
        pure = th0 * (A_path[g0][t] - 1) * race_F[g0][:, t]
        y = y_rel(race_rel[g0][:, t], A_path[g0][t], race_F[g0][:, t], th0)
        absorbed[str(k)] = {"Y_solo_IA": float(pure.mean()), "Y": float(y.mean()),
                            "quota_assorbita": float(1 - y.mean() / pure.mean())}

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
                "Y_per_orizzonte": {str(k): ci(rel(scen[t], base, "Y")[:, start + k]) for k in HORIZONS},
                "F_U_per_orizzonte": {str(k): float(scen[t]["F_U"][:, start + k].mean()) for k in HORIZONS},
                "gini_fine": ci(scen[t]["gini_w"][:, -5:].mean(1)),
                "primo_effetto_senior_anni_dopo": first_effect(scen[t], base, "mean_h_senior", start),
                "primo_effetto_H_anni_dopo": first_effect(scen[t], base, "H", start),
            }
            for t in SCENARIOS
        },
        "gini_base_fine": ci(base["gini_w"][:, -5:].mean(1)),
        "corsa": {"g": list(G_GRID), "theta": list(THETA_GRID), "mappa_Y_fine": mappa,
                  "theta_pareggio_fine": breakeven, "assorbimento": absorbed,
                  "H_fine_per_g": {f"{g:.2f}": ci(race_rel[g][:, end]) for g in G_GRID}},
    }
    # D17: "compiti" sui junior (p giù) e sui senior (beta giù), differenze accoppiate per replica.
    num["simmetria_compiti"] = {
        "H_junior_meno_senior": ci(rel(scen["junior"], base, "H")[:, end] - rel(scen["senior"], base, "H")[:, end]),
        "gini_junior_meno_senior": ci(scen["junior"]["gini_w"][:, -5:].mean(1) - scen["senior"]["gini_w"][:, -5:].mean(1)),
    }
    # D18: sensibilità a gamma. h non dipende da gamma, cambia solo F e quindi Y.
    sens_g = {}
    for gm in GAMMA_GRID:
        sens_g[str(gm)] = {}
        for name in ("junior", "senior"):
            r = run_replications(on(**SCENARIOS[name], gamma=gm), args.race_reps)
            sens_g[str(gm)][name] = {str(k): ci(rel(r, base_r, "Y")[:, start + k]) for k in HORIZONS}
    num["sensibilita_gamma"] = sens_g
    # senza familiarità (versione precedente di Y), per confronto
    noF = {name: run_replications(on(**SCENARIOS[name], familiarity=False), args.race_reps)
           for name in ("junior", "senior")}
    num["senza_familiarita"] = {name: {"Y_per_orizzonte": {str(k): ci(rel(r, base_r, "Y")[:, start + k]) for k in HORIZONS},
                                       "gini_fine": ci(r["gini_w"][:, -5:].mean(1))}
                                for name, r in noF.items()}
    # D14: i senior che escono (margine "posto", kappa giù) contano solo se i mentori sono scarsi.
    sens_k = {}
    for k in KAPPA_GRID:
        ck = cfg.with_overrides({"meetings.kappa": k})
        bk = run_replications(ck, args.race_reps)
        sk = run_replications(ck.with_overrides({"ai.enabled": True, "ai.target": "senior",
                                                 "ai.margin_senior": "posto"}), args.race_reps)
        sens_k[str(k)] = {"H_fine": ci(rel(sk, bk, "H")[:, end]),
                          "h_senior_fine": ci(rel(sk, bk, "mean_h_senior")[:, end]),
                          "primo_effetto_H_anni_dopo": first_effect(sk, bk, "H", start),
                          "p_eff_base": float(bk["p_eff"].mean())}
    num["sensibilita_kappa_senior"] = sens_k
    (ROOT / "report" / "numeri_fase2.json").write_text(json.dumps(num, indent=1, ensure_ascii=False))

    for L in LABELS.values():
        figures(L, years, start, scen, base, race_rel, A_path, race_F, num)

    def series(x):
        m, lo, hi = mean_ci(x)
        return {"m": np.round(m, 6).tolist(), "lo": np.round(lo, 6).tolist(), "hi": np.round(hi, 6).tolist()}

    site = {
        "years": years.tolist(), "start": start, "numbers": num,
        "labels": LABELS["it"]["targets"],
        "targets": {t: {k: series(rel(scen[t], base, k)) for k in ("H", "mean_h_senior", "mean_h_junior", "B_meet")}
                    for t in SCENARIOS},
        "race": {f"{g:.2f}": {"H": series(race_rel[g]), "A": np.round(A_path[g], 6).tolist(),
                              "F": np.round(race_F[g].mean(0), 6).tolist()} for g in G_GRID},
    }
    (ROOT / "site" / "data" / "fase2.json").write_text(json.dumps(site, ensure_ascii=False))
    print(f"fase 2 in {time.perf_counter() - t0:.0f}s", file=sys.stderr)
    print(json.dumps({k: v for k, v in num.items() if k != "corsa"}, ensure_ascii=False))
    print(json.dumps(num["corsa"]["theta_pareggio_fine"]))


if __name__ == "__main__":
    main()
