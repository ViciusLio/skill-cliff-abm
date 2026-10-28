"""D20: mentore stabile. Il junior resta con lo stesso senior finché è junior, il mentore è in
servizio e la coppia non si scioglie (probabilità annua lambda). lambda = 1 è il modello base.

Per ogni lambda della griglia beta è ricalibrato in modo che l'apprendimento medio da incontri dei
junior (B da incontri) sia quello della fase 1. Poi, al lambda centrale:
- profilo salariale, quota di B dagli incontri, Gini;
- Proposizione 1: identità con la quota realizzata di junior che imparano al posto di p_eff;
- Proposizione 2: ritardo dopo il dimezzamento di p;
- p dimezzato contro beta dimezzato (la simmetria della fase 1 regge?);
- IA (fase 2): compiti junior, compiti senior, junior che perdono il posto.

Numeri in report/numeri_d20.json. Uso: python scripts/mentore_stabile.py [--reps 30]
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
from make_report import ROOT, SHOCK_YEAR, ci_dict, first_senior_effect, profile_stats  # noqa: E402

from skillcliff import load_config  # noqa: E402
from skillcliff.ai import MeetingShock  # noqa: E402
from skillcliff.experiment import replication_seeds, run_replications  # noqa: E402
from skillcliff.learning import role_masks  # noqa: E402
from skillcliff.model import Model  # noqa: E402

LAMBDAS = (0.1, 0.15, 0.2, 0.5, 1.0)
LAMBDA_C = 0.15          # centrale: separazione annua dei giovani (turnover 10-20%)
AI_SCEN = {"junior": {"ai.target": "junior"}, "senior": {"ai.target": "senior"},
           "junior_posto": {"ai.target": "junior", "ai.margin_junior": "posto"}}


def b_meet(cfg, reps):
    return float(run_replications(cfg, reps)["B_meet"].mean())


def calibrate_beta(cfg, target, reps, tol=2e-5):
    """Bisezione su beta: B da incontri cresce con beta."""
    lo, hi = 0.01, cfg.meetings.beta
    if b_meet(cfg.with_overrides({"meetings.beta": hi}), reps) <= target:
        return hi
    for _ in range(20):
        mid = 0.5 * (lo + hi)
        b = b_meet(cfg.with_overrides({"meetings.beta": mid}), reps)
        if abs(b - target) < tol:
            return mid
        lo, hi = (mid, hi) if b < target else (lo, mid)
    return 0.5 * (lo + hi)


def proposition_1(cfg, years=30):
    """Identità della Proposizione 1 con la quota realizzata m_g di junior che imparano (coppie in
    corso e nuovi abbinamenti) al posto di p_eff, e la distribuzione di tutti i senior del gruppo.
    Con il mentore stabile gli abbinati non sono un campione casuale: l'errore lo misura."""
    m = Model(cfg, replication_seeds(cfg, 1)[0])
    for _ in range(cfg.burn_in):
        m.step()
    sim, formula = [], []
    for _ in range(years):
        rec = m.step()
        pop, meet = m.pop, m.last_meet
        h0 = pop.h - meet.dh - m.last_dh_aut
        junior, senior = role_masks(cfg, pop.exp)
        J, f = junior.sum(), 0.0
        for g in (~pop.high, pop.high):
            hJ, hS = h0[junior & g], h0[senior & g]
            m_g = g[meet.learners].sum() / hJ.size
            omega = np.mean(np.maximum(0, hJ[:, None] - hS[None, :]) / hJ[:, None])
            f += hJ.size / J * cfg.meetings.beta * m_g * (hS.mean() * np.mean(1 / hJ) - 1 + omega)
        sim.append(rec["B_meet"]); formula.append(f)
    return {"B_meet_simulato": float(np.mean(sim)), "identita_con_abbinamento_casuale": float(np.mean(formula)),
            "errore_relativo": float(np.mean(formula) / np.mean(sim) - 1)}


def summary(cfg, base):
    ea = cfg.population.entry_age
    return {"B": ci_dict(base["B"].mean(1)), "B_meet": ci_dict(base["B_meet"].mean(1)),
            "quota_B_da_incontri": float(base["B_meet"].mean() / base["B"].mean()),
            "gini": ci_dict(base["gini_w"].mean(1)), "mean_h_senior": ci_dict(base["mean_h_senior"].mean(1)),
            "quota_junior_in_coppia": float((base["n_pairs"] / base["n_junior"]).mean()),
            "quota_junior_che_imparano": float((base["n_meetings"] / base["n_junior"]).mean()),
            "profilo_non_qualificati": profile_stats(base, "h_by_age_low", ea.low),
            "profilo_qualificati": profile_stats(base, "h_by_age_high", ea.high)}


def shocks(cfg, base, reps):
    late = slice(SHOCK_YEAR + 25, cfg.T)
    out = {}
    for name, kw in (("p_dimezzato", {"p_mult": 0.5}), ("beta_dimezzato", {"beta_mult": 0.5})):
        r = run_replications(cfg, reps, functools.partial(MeetingShock, year=SHOCK_YEAR, **kw))
        out[name] = {"H_fine": ci_dict(r["H"][:, -1] / base["H"][:, -1] - 1),
                     "h_senior_lungo": ci_dict(r["mean_h_senior"][:, late].mean(1) / base["mean_h_senior"][:, late].mean(1) - 1),
                     "B_meet_fine": ci_dict(r["B_meet"][:, -5:].mean(1) / base["B_meet"][:, -5:].mean(1) - 1),
                     "gini_fine": ci_dict(r["gini_w"][:, -1]),
                     "ritardo_osservato": first_senior_effect(base, r)}
    out["ritardo_previsto"] = cfg.roles.senior_min_exp - cfg.roles.junior_max_exp + 1
    return out


def ai_scenarios(cfg, reps):
    base = run_replications(cfg, reps)
    end, out = cfg.T - 1, {}
    for name, ov in AI_SCEN.items():
        r = run_replications(cfg.with_overrides({"ai.enabled": True, **ov}), reps)
        out[name] = {"H_fine": ci_dict(r["H"][:, end] / base["H"][:, end] - 1),
                     "h_senior_fine": ci_dict(r["mean_h_senior"][:, end] / base["mean_h_senior"][:, end] - 1),
                     "B_meet_fine": ci_dict(r["B_meet"][:, -5:].mean(1) / base["B_meet"][:, -5:].mean(1) - 1),
                     "gini_fine": ci_dict(r["gini_w"][:, -5:].mean(1))}
        out[name]["_H"] = r["H"][:, end] / base["H"][:, end] - 1
    out["H_junior_meno_senior"] = ci_dict(out["junior"].pop("_H") - out["senior"].pop("_H"))
    out["junior_posto"].pop("_H")
    out["gini_base"] = ci_dict(base["gini_w"][:, -5:].mean(1))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "configs" / "base.yaml"))
    ap.add_argument("--reps", type=int, default=30)
    ap.add_argument("--calib-reps", type=int, default=10)
    ap.add_argument("--N", type=int, default=5000)
    ap.add_argument("--N-ai", type=int, default=50_000)
    args = ap.parse_args()
    t0 = time.perf_counter()
    cfg = load_config(args.config).with_overrides({"population.N": args.N})
    target = b_meet(cfg, args.reps)

    calib = {}
    for lam in LAMBDAS:
        c = cfg.with_overrides({"meetings.stable_mentor": True, "meetings.separation": lam})
        beta = cfg.meetings.beta if lam == 1.0 else calibrate_beta(c, target, args.calib_reps)
        c = c.with_overrides({"meetings.beta": beta})
        base = run_replications(c, args.reps)
        calib[str(lam)] = {"beta": beta, **summary(c, base)}
        print(f"lambda={lam}: beta={beta:.4f}  B_meet={calib[str(lam)]['B_meet']['media']:.5f} (obiettivo {target:.5f})",
              file=sys.stderr)

    central = cfg.with_overrides({"meetings.stable_mentor": True, "meetings.separation": LAMBDA_C,
                                  "meetings.beta": calib[str(LAMBDA_C)]["beta"]})
    base_c = run_replications(central, args.reps)
    random_base = run_replications(cfg, args.reps)
    num = {
        "N": args.N, "repliche": args.reps, "lambda_centrale": LAMBDA_C, "B_meet_obiettivo": target,
        "calibrazione": calib,
        "proposizione_1": {"base": proposition_1(cfg), "mentore_stabile": proposition_1(central)},
        "shock": {"base": shocks(cfg, random_base, args.reps), "mentore_stabile": shocks(central, base_c, args.reps)},
        "ia": {"N": args.N_ai,
               "base": ai_scenarios(cfg.with_overrides({"population.N": args.N_ai}), args.reps),
               "mentore_stabile": ai_scenarios(central.with_overrides({"population.N": args.N_ai}), args.reps)},
    }
    (ROOT / "report" / "numeri_d20.json").write_text(json.dumps(num, indent=1, ensure_ascii=False))
    print(f"D20 in {time.perf_counter() - t0:.0f}s", file=sys.stderr)
    print(json.dumps(num, ensure_ascii=False))


if __name__ == "__main__":
    main()
