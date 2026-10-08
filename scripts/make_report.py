"""Fase 1: esegue gli esperimenti, produce le figure in report/fig/ (italiano) e paper/fig/ (inglese, PDF), i numeri chiave in
report/numeri_fase1.json e i dati per il report interattivo in site/data/fase1.json.

Uso: python scripts/make_report.py [--reps 30] [--sens-reps 10]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from skillcliff import load_config  # noqa: E402
from skillcliff.ai import MeetingShock  # noqa: E402
from skillcliff.experiment import run_replications, save_results  # noqa: E402
from skillcliff.metrics import mean_ci  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "report" / "fig"

# Palette di riferimento (validata per daltonismo): slot categoriali e rampa sequenziale blu.
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
SEQ = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#0d366b"]
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
AGE_CLASSES = [(20, 29), (30, 39), (40, 49), (50, 59), (60, 64)]
SHOCK_YEAR, SHOCK_P_MULT = 10, 0.5

plt.rcParams.update({
    "figure.dpi": 110, "savefig.dpi": 150, "font.size": 10,
    "axes.edgecolor": GRID, "axes.labelcolor": INK2, "axes.titlecolor": INK,
    "axes.titlesize": 11, "axes.titleweight": "bold", "axes.titlelocation": "left",
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    "xtick.color": INK2, "ytick.color": INK2, "lines.linewidth": 2,
    "legend.frameon": False, "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb",
})


def band(ax, x, samples, color, label, **kw):
    """Linea = media tra repliche, banda = IC 95%."""
    m, lo, hi = mean_ci(samples)
    ax.fill_between(x, lo, hi, color=color, alpha=0.18, linewidth=0)
    ax.plot(x, m, color=color, label=label, **kw)
    return m


def age_class_means(res, a0, a1):
    """h medio della classe d'età [a0, a1] per replica e anno, pesato per numerosità."""
    h, n = res["h_by_age"][..., a0:a1 + 1], res["n_by_age"][..., a0:a1 + 1]
    return np.nansum(h * n, axis=-1) / n.sum(axis=-1)


def profile(res, key):
    """Profilo per età mediato sugli anni: (repliche, età)."""
    return np.nanmean(res[key], axis=1)


# Etichette delle figure: italiano per report/fig, inglese per l'articolo (paper/fig).
LABELS = {
    "it": {
        "dir": FIG, "base": "(a) Base stazionario", "shock": f"(b) p dimezzato dall'anno {SHOCK_YEAR}",
        "year": "anno", "age": "età", "years_old": "anni", "mean_h": "h medio",
        "B": "B totale", "B_meet": "da incontri", "B_aut": "autonomo",
        "B_y": "crescita media annua di h dei junior", "low": "non qualificati", "high": "qualificati",
        "all": "tutti", "profile": "Profilo salariale per età (w = h)", "wage": "salario medio",
        "base_short": "base", "shock_short": f"p dimezzato dall'anno {SHOCK_YEAR}", "gini": "Gini dei salari",
        "kappa_base": " (base; uguale per kappa > 0.2)", "sens_a": "(a) B da incontri",
        "sens_b": "(b) h medio dei senior", "p": "p (probabilità d'incontro)",
        "files": ("fig1_h_per_classe_eta.png", "fig2_B_emergente.png", "fig3_profilo_salariale.png",
                  "fig4_gini.png", "fig5_sensibilita_p_kappa.png"),
    },
    "en": {
        "dir": ROOT / "paper" / "fig", "base": "(a) Stationary baseline",
        "shock": f"(b) p halved from year {SHOCK_YEAR}", "year": "year", "age": "age", "years_old": "years",
        "mean_h": "mean h", "B": "total B", "B_meet": "from meetings", "B_aut": "autonomous",
        "B_y": "mean annual growth of junior h", "low": "low-skilled", "high": "high-skilled", "all": "all",
        "profile": "Age-wage profile (w = h)", "wage": "mean wage", "base_short": "baseline",
        "shock_short": f"p halved from year {SHOCK_YEAR}", "gini": "Wage Gini",
        "kappa_base": " (baseline; same for kappa > 0.2)", "sens_a": "(a) B from meetings",
        "sens_b": "(b) mean senior h", "p": "p (meeting probability)",
        "files": ("fig1_h_by_age_class.pdf", "fig2_emergent_B.pdf", "fig3_age_wage_profile.pdf",
                  "fig4_gini.pdf", "fig5_sensitivity_p_kappa.pdf"),
    },
}


def savefig(fig, L, i):
    L["dir"].mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(L["dir"] / L["files"][i], bbox_inches="tight")
    plt.close(fig)


def fig_cohorts(base, shock, years, L):
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
    for ax, res, title in ((axes[0], base, L["base"]), (axes[1], shock, L["shock"])):
        for (a0, a1), c in zip(AGE_CLASSES, SEQ):
            band(ax, years, age_class_means(res, a0, a1), c, f"{a0}-{a1} {L['years_old']}")
        ax.set_title(title)
        ax.set_xlabel(L["year"])
    axes[1].axvline(SHOCK_YEAR, color=INK2, linewidth=1, linestyle=":")
    axes[0].set_ylabel(L["mean_h"])
    axes[1].legend(loc="lower left", ncol=2, fontsize=8)
    savefig(fig, L, 0)


def fig_B(base, shock, years, L):
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6), sharey=True)
    for ax, res, title in ((axes[0], base, L["base"]), (axes[1], shock, L["shock"])):
        band(ax, years, res["B"], BLUE, L["B"])
        band(ax, years, res["B_meet"], ORANGE, L["B_meet"])
        band(ax, years, res["B_aut"], AQUA, L["B_aut"])
        ax.set_title(title)
        ax.set_xlabel(L["year"])
    axes[1].axvline(SHOCK_YEAR, color=INK2, linewidth=1, linestyle=":")
    axes[0].set_ylabel(L["B_y"])
    axes[0].legend(loc="lower right", fontsize=8)
    axes[0].set_ylim(bottom=0)
    savefig(fig, L, 1)


def fig_profile(base, cfg, L):
    ages = np.arange(cfg.max_age)
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    for key, c, lab, a0 in (("h_by_age_low", BLUE, L["low"], cfg.population.entry_age.low),
                            ("h_by_age_high", ORANGE, L["high"], cfg.population.entry_age.high),
                            ("h_by_age", INK2, L["all"], cfg.population.entry_age.low)):
        p = profile(base, key)[:, a0:]
        band(ax, ages[a0:], p, c, lab, linewidth=2 if key != "h_by_age" else 1.2)
    ax.set_title(L["profile"])
    ax.set_xlabel(L["age"])
    ax.set_ylabel(L["wage"])
    ax.legend(loc="lower right", fontsize=8)
    savefig(fig, L, 2)


def fig_gini(base, shock, years, L):
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    band(ax, years, base["gini_w"], BLUE, L["base_short"])
    band(ax, years, shock["gini_w"], ORANGE, L["shock_short"])
    ax.axvline(SHOCK_YEAR, color=INK2, linewidth=1, linestyle=":")
    ax.set_title(L["gini"])
    ax.set_xlabel(L["year"])
    ax.legend(fontsize=8)
    savefig(fig, L, 3)


def fig_sensitivity(sens, L):
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6))
    colors = [BLUE, ORANGE, AQUA]
    for (kappa, rows), c in zip(sens.items(), colors):
        ps = [r["p"] for r in rows]
        for ax, key in zip(axes, ("B_meet", "mean_h_senior")):
            m = np.array([r[key][0] for r in rows])
            lo = np.array([r[key][1] for r in rows])
            hi = np.array([r[key][2] for r in rows])
            ax.fill_between(ps, lo, hi, color=c, alpha=0.18, linewidth=0)
            lab = f"kappa = {kappa}" + (L["kappa_base"] if kappa == 0.2 else "")
            ax.plot(ps, m, color=c, marker="o", markersize=4, label=lab)
    axes[0].set_title(L["sens_a"])
    axes[1].set_title(L["sens_b"])
    for ax in axes:
        ax.set_xlabel(L["p"])
    axes[0].legend(fontsize=8)
    savefig(fig, L, 4)


def profile_stats(base, key, entry_age):
    """Statistiche del profilo medio: età di picco, rapporto picco/ingresso, calo finale."""
    p = np.nanmean(profile(base, key), axis=0)
    seg = p[entry_age:]
    peak = int(np.nanargmax(seg)) + entry_age
    return {"eta_picco": peak, "esperienza_picco": peak - entry_age,
            "picco_su_ingresso": float(p[peak] / p[entry_age]),
            "calo_finale": float(p[-1] / p[peak] - 1)}


def ci_dict(samples):
    m, lo, hi = mean_ci(samples)
    return {"media": float(m), "ic95": [float(lo), float(hi)]}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "configs" / "base.yaml"))
    ap.add_argument("--reps", type=int, default=None)
    ap.add_argument("--sens-reps", type=int, default=10)
    args = ap.parse_args()
    FIG.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()

    cfg = load_config(args.config)
    base = run_replications(cfg, args.reps)
    shock = run_replications(cfg, args.reps, ai_factory=lambda c: MeetingShock(c, SHOCK_YEAR, SHOCK_P_MULT))
    save_results(ROOT / "outputs" / "base" / "results.npz", cfg, base)
    save_results(ROOT / "outputs" / "shock_p" / "results.npz", cfg, shock)
    years = np.arange(cfg.T)

    sens_cfg = cfg.with_overrides({"T": 20})
    sens = {}
    for kappa in (0.05, 0.1, 0.2):
        rows = []
        for p in np.round(np.linspace(0, 1, 11), 2):
            r = run_replications(sens_cfg.with_overrides({"meetings.p": float(p), "meetings.kappa": kappa}),
                                 n_reps=args.sens_reps)
            rows.append({"p": float(p),
                         "B_meet": [float(v) for v in mean_ci(r["B_meet"].mean(1))],
                         "mean_h_senior": [float(v) for v in mean_ci(r["mean_h_senior"].mean(1))],
                         "p_eff": float(r["p_eff"].mean())})
        sens[kappa] = rows

    for L in LABELS.values():
        fig_cohorts(base, shock, years, L)
        fig_B(base, shock, years, L)
        fig_profile(base, cfg, L)
        fig_gini(base, shock, years, L)
        fig_sensitivity(sens, L)

    ea = cfg.population.entry_age
    tm = lambda res, k: res[k].mean(axis=1)  # noqa: E731  media temporale per replica
    late = slice(SHOCK_YEAR + 25, cfg.T)
    numbers = {
        "repliche": int(base["Y"].shape[0]),
        "profilo": {
            "non_qualificati": profile_stats(base, "h_by_age_low", ea.low),
            "qualificati": profile_stats(base, "h_by_age_high", ea.high),
        },
        "B": ci_dict(tm(base, "B")), "B_meet": ci_dict(tm(base, "B_meet")),
        "B_aut": ci_dict(tm(base, "B_aut")), "gini": ci_dict(tm(base, "gini_w")),
        "p_eff": ci_dict(tm(base, "p_eff")),
        "quota_junior": ci_dict(tm(base, "n_junior") / cfg.population.N),
        "quota_senior": ci_dict(tm(base, "n_senior") / cfg.population.N),
        "rapporto_S_su_J": ci_dict(tm(base, "n_senior") / tm(base, "n_junior")),
        "mean_h": ci_dict(tm(base, "mean_h")),
        "shock": {
            "anno": SHOCK_YEAR, "p_mult": SHOCK_P_MULT,
            "var_h_junior_dopo_4": ci_dict(shock["mean_h_junior"][:, SHOCK_YEAR + 4] / base["mean_h_junior"][:, SHOCK_YEAR + 4] - 1),
            "var_h_senior_dopo_5": ci_dict(shock["mean_h_senior"][:, SHOCK_YEAR + 5] / base["mean_h_senior"][:, SHOCK_YEAR + 5] - 1),
            "var_h_senior_dopo_25": ci_dict(shock["mean_h_senior"][:, SHOCK_YEAR + 25] / base["mean_h_senior"][:, SHOCK_YEAR + 25] - 1),
            "var_h_senior_lungo": ci_dict(shock["mean_h_senior"][:, late].mean(1) / base["mean_h_senior"][:, late].mean(1) - 1),
            "var_Y_lungo": ci_dict(shock["Y"][:, late].mean(1) / base["Y"][:, late].mean(1) - 1),
        },
        "sensibilita": {str(k): v for k, v in sens.items()},
    }
    docking = ROOT / "outputs" / "docking.json"
    if docking.exists():
        numbers["docking"] = json.loads(docking.read_text())
    (ROOT / "report" / "numeri_fase1.json").write_text(json.dumps(numbers, indent=2, ensure_ascii=False))

    # Dati per il report interattivo (medie e IC per anno/età).
    def series(res, k):
        m, lo, hi = mean_ci(res[k])
        return {"m": np.round(m, 5).tolist(), "lo": np.round(lo, 5).tolist(), "hi": np.round(hi, 5).tolist()}

    def classes(res):
        out = {}
        for a0, a1 in AGE_CLASSES:
            m, lo, hi = mean_ci(age_class_means(res, a0, a1))
            out[f"{a0}-{a1}"] = {"m": np.round(m, 5).tolist(), "lo": np.round(lo, 5).tolist(), "hi": np.round(hi, 5).tolist()}
        return out

    def prof(res, key, a0):
        m, lo, hi = mean_ci(profile(res, key)[:, a0:])
        return {"age": list(range(a0, cfg.max_age)), "m": np.round(m, 5).tolist(),
                "lo": np.round(lo, 5).tolist(), "hi": np.round(hi, 5).tolist()}

    site = {
        "config": cfg.to_dict(), "numbers": numbers, "years": years.tolist(),
        "scenarios": {
            name: {
                "label": label,
                "series": {k: series(res, k) for k in ("B", "B_meet", "B_aut", "gini_w", "mean_h",
                                                       "mean_h_junior", "mean_h_senior", "n_meetings", "Y")},
                "classes": classes(res),
                "profile": {"low": prof(res, "h_by_age_low", ea.low), "high": prof(res, "h_by_age_high", ea.high)},
            }
            for name, label, res in (("base", "Base stazionario", base),
                                     ("shock_p", f"p dimezzato dall'anno {SHOCK_YEAR}", shock))
        },
    }
    out = ROOT / "site" / "data" / "fase1.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(site, ensure_ascii=False))
    print(f"report fase 1 generato in {time.perf_counter() - t0:.1f}s", file=sys.stderr)
    print(json.dumps({k: v for k, v in numbers.items() if k not in ("sensibilita", "docking")}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
