import numpy as np
import pytest

from test_model import SMALL

from skillcliff.ai import AI, TARGETS
from skillcliff.model import run_model

AI_CFG = SMALL.with_overrides({"T": 30, "ai.start": 5, "ai.g": 0.05, "ai.phi_max": 0.6, "ai.theta": 0.1})


def run(cfg, seed=4):
    return run_model(cfg, np.random.SeedSequence(seed))


def with_ai(target, cfg=AI_CFG):
    return cfg.with_overrides({"ai.enabled": True, "ai.target": target})


def test_productivity_share_and_output_formulas():
    ai = AI(with_ai("junior"))
    assert ai.productivity(4) == 1.0 and ai.automation_share(4) == 0.0
    assert ai.productivity(7) == pytest.approx(1.05 ** 2)
    assert ai.automation_share(7) == pytest.approx(0.6 * (1 - 1 / 1.05 ** 2))
    assert ai.output(7, 100.0) == pytest.approx(100.0 * (1 + 0.1 * (1.05 ** 2 - 1)))


@pytest.mark.parametrize("target", TARGETS)
def test_identical_to_baseline_before_introduction(target):
    base, ai = run(AI_CFG), run(with_ai(target))
    start = AI_CFG.ai.start
    for k in ("H", "B", "mean_h_senior", "gini_w"):
        np.testing.assert_array_equal(base[k][:start], ai[k][:start])
    assert (ai["A"][:start] == 1).all() and ai["A"][start + 1] > 1


def test_junior_target_seniors_untouched_for_lag_years():
    base, ai = run(AI_CFG), run(with_ai("junior"))
    lag = AI_CFG.roles.senior_min_exp - AI_CFG.roles.junior_max_exp   # anni senza effetto
    s = AI_CFG.ai.start
    np.testing.assert_array_equal(base["mean_h_senior"][: s + lag], ai["mean_h_senior"][: s + lag])
    assert ai["mean_h_junior"][s + 3] < base["mean_h_junior"][s + 3]
    assert ai["mean_h_senior"][-1] < base["mean_h_senior"][-1]


# --- D16-D17: tabella 2x2 (compiti / posto) -----------------------------------

@pytest.mark.parametrize("target,mj,ms,expected", [
    ("junior", "compiti", "compiti", {"p": (0.5, 0.5)}),
    ("junior", "posto", "compiti", {}),
    ("senior", "compiti", "compiti", {"beta": (0.5, 0.5)}),
    ("senior", "compiti", "posto", {"kappa": (0.5, 0.5)}),
    ("qualificati", "compiti", "compiti", {"p": (1.0, 0.5), "beta": (1.0, 0.5)}),
    ("non_qualificati", "posto", "posto", {"kappa": (0.5, 1.0)}),
])
def test_margin_table(target, mj, ms, expected):
    ai = AI(with_ai(target).with_overrides({"ai.margin_junior": mj, "ai.margin_senior": ms}))
    t = next(t for t in range(200) if ai.automation_share(t) > 0)
    phi = ai.automation_share(t)
    want = {k: tuple(1 - phi if v == 0.5 else 1.0 for v in vals) for k, vals in expected.items()}
    assert ai.meeting_modifiers(t) == ai.meeting_modifiers(t).__class__(**want)
    junior = np.ones(1000, dtype=bool)
    out = ai.nonemployed(t, junior, np.zeros(1000, dtype=bool), np.random.default_rng(0))
    assert (out is not None) == (mj == "posto" and target != "qualificati")


def test_margin_must_be_known():
    with pytest.raises(ValueError):
        AI_CFG.with_overrides({"ai.margin_senior": "licenziato"})


def test_task_substitution_junior_and_senior_same_mean_effect():
    """Proposizione 1: p e beta entrano come prodotto, quindi 'compiti' sui junior (p giù) e sui
    senior (beta giù) spostano H quasi allo stesso modo."""
    base = run(AI_CFG)
    dj = run(with_ai("junior"))["H"][-1] / base["H"][-1] - 1
    ds = run(with_ai("senior"))["H"][-1] / base["H"][-1] - 1
    assert dj < 0 and ds < 0
    assert abs(dj - ds) < 0.15 * abs(dj)


def test_complementary_ai_raises_learning():
    base, ai = run(AI_CFG), run(with_ai("complementare"))
    s = AI_CFG.ai.start
    assert ai["B_meet"][s + 3:].mean() > base["B_meet"][s + 3:].mean()
    assert ai["H"][-1] > base["H"][-1]


def test_skill_targets_hit_only_their_group():
    base, ai = run(AI_CFG), run(with_ai("qualificati"))
    s = AI_CFG.ai.start
    a = 30   # età in cui tutti hanno almeno 5 anni di esperienza
    assert ai["h_by_age_high"][-1, a] < base["h_by_age_high"][-1, a]
    np.testing.assert_allclose(ai["h_by_age_low"][s:, a], base["h_by_age_low"][s:, a])


def test_skill_targets_require_same_qual():
    with pytest.raises(ValueError):
        AI(with_ai("qualificati", AI_CFG.with_overrides({"meetings.same_qual": False})))


# --- D13: junior sostituiti non occupati ------------------------------------

def test_displacement_share_and_no_learning_for_nonemployed():
    from skillcliff.model import Model

    cfg = with_ai("junior").with_overrides({"ai.margin_junior": "posto"})
    m = Model(cfg, np.random.SeedSequence(5))
    for _ in range(cfg.burn_in):
        m.step(record=False)
    shares = []
    for _ in range(cfg.T):
        rec = m.step()
        phi = m.ai.automation_share(m.t - 1)
        shares.append((rec["n_nonemployed"], phi * rec["n_junior"]))
        h_prev = m.pop.h - m.last_meet.dh - m.last_dh_aut
        junior = m.pop.exp < cfg.roles.junior_max_exp
        # nessun incontro e solo obsolescenza (un junior occupato ha sempre delta(s) > d)
        out = junior & (m.last_meet.dh == 0) & np.isclose(m.last_dh_aut, -cfg.learning.depreciation * h_prev)
        if rec["n_nonemployed"]:
            assert out.sum() >= rec["n_nonemployed"]       # i non occupati perdono solo per obsolescenza
    obs, exp_ = np.array(shares).T
    assert obs[: cfg.ai.start + 1].sum() == 0
    np.testing.assert_allclose(obs[-10:].sum(), exp_[-10:].sum(), rtol=0.15)


def test_displacement_identical_before_start_and_keeps_senior_lag():
    base = run(AI_CFG)
    ai = run(with_ai("junior").with_overrides({"ai.margin_junior": "posto"}))
    s = AI_CFG.ai.start
    lag = AI_CFG.roles.senior_min_exp - AI_CFG.roles.junior_max_exp
    np.testing.assert_array_equal(base["H"][: s + 1], ai["H"][: s + 1])
    np.testing.assert_array_equal(base["mean_h_senior"][: s + lag], ai["mean_h_senior"][: s + lag])
    # su H, non su h medio dei junior: con D19 chi resta fuori resta junior più a lungo (composizione)
    assert ai["H"][s + 3] < base["H"][s + 3]


def test_fixed_automation_cuts_junior_meetings_from_start():
    from skillcliff.ai import FixedAutomation

    base = run_model(AI_CFG, np.random.SeedSequence(6))
    fx = run_model(AI_CFG, np.random.SeedSequence(6), FixedAutomation(AI_CFG, phi=0.4))
    s = AI_CFG.ai.start
    np.testing.assert_array_equal(base["H"][:s], fx["H"][:s])
    assert fx["phi"][s] == 0.4 and fx["phi"][s - 1] == 0.0
    assert fx["p_eff"][s + 1] == pytest.approx(0.6 * AI_CFG.meetings.p)
    assert fx["H"][-1] < base["H"][-1]


def test_experience_grows_only_when_employed():
    """D19: un anno da non occupato non conta come esperienza; senza IA s = età - età d'ingresso."""
    from skillcliff.model import Model
    from skillcliff.population import entry_age

    base = Model(AI_CFG, np.random.SeedSequence(8))
    cfg = with_ai("junior").with_overrides({"ai.margin_junior": "posto"})
    m = Model(cfg, np.random.SeedSequence(8))
    n_out = 0
    for _ in range(cfg.burn_in + cfg.T):
        base.step(record=False)
        np.testing.assert_array_equal(base.pop.exp, base.pop.age - entry_age(AI_CFG, base.pop.high))
        uid, exp, out = m.pop.uid.copy(), m.pop.exp.copy(), m.pop.out.copy()
        m.step(record=False)
        stay = np.isin(uid, m.pop.uid)                  # chi non è andato in pensione
        exp_new = m.pop.exp[np.searchsorted(m.pop.uid, uid[stay])]
        np.testing.assert_array_equal(exp_new, exp[stay] + ~out[stay])
        n_out += out.sum()
    assert n_out > 0
    lost = m.pop.age - entry_age(cfg, m.pop.high) - m.pop.exp   # anni persi da non occupati
    assert (lost >= 0).all() and lost.max() > 0


# --- D18: familiarità con l'IA ----------------------------------------------

def test_familiarity_dynamics():
    """Chi entra con l'IA già arrivata ha f = 1; chi c'era parte da 0 e da occupato si aggiorna."""
    from skillcliff.model import Model

    cfg = with_ai("junior").with_overrides({"ai.margin_junior": "posto", "ai.gamma": 0.2})
    m = Model(cfg, np.random.SeedSequence(9))
    for _ in range(cfg.burn_in + cfg.ai.start):
        m.step(record=False)
    assert m.t == cfg.ai.start and (m.pop.f == 0).all()             # prima dell'IA nessuna familiarità
    m.step(record=False)        # anno dell'arrivo: entrano lavoratori con f = 1, gli altri non cambiano
    assert set(np.unique(m.pop.f)) == {0.0, 1.0}
    for _ in range(8):
        uid, f, out = m.pop.uid.copy(), m.pop.f.copy(), m.pop.out.copy()
        m.step(record=False)
        stay = np.isin(uid, m.pop.uid)
        new = m.pop.f[np.searchsorted(m.pop.uid, uid[stay])]
        want = np.where(out[stay], f[stay], f[stay] + 0.2 * (1 - f[stay]))
        np.testing.assert_allclose(new, want)
        assert (m.pop.f[~np.isin(m.pop.uid, uid)] == 1).all()        # entranti


def test_wages_rent_and_off_switch():
    on = with_ai("senior")
    r = run(on)
    s = AI_CFG.ai.start
    assert (r["F_U"][:s + 2] < 1).all() and r["F_U"][-1] > r["F_U"][s + 2]
    from skillcliff.model import Model

    m = Model(on, np.random.SeedSequence(4))
    for _ in range(on.burn_in + on.T):
        m.step(record=False)
    from skillcliff.learning import role_masks
    junior, senior = role_masks(on, m.pop.exp)
    users = m.ai.users(junior, senior, m.pop.high, m.last_out)
    F = m.ai.familiarity_weight(m.pop.h, m.pop.f, users)
    w = m.ai.wages(m.t - 1, m.pop.h, m.pop.f, users)
    A, h = m.ai.productivity(m.t - 1), m.pop.h
    rent = m.ai.output(m.t - 1, h.sum(), F) - w.sum()             # rendita dell'IA: Y meno salari
    assert rent == pytest.approx(0.1 * (A - 1) * F * (h.sum() - h[users].sum()))
    assert rent > 0 and r["rent_ai"][-1] > 0
    off = run(on.with_overrides({"ai.familiarity": False}))
    np.testing.assert_array_equal(off["H"], r["H"])                   # f non tocca la dinamica di h
    np.testing.assert_allclose(off["Y"], off["H"] * (1 + 0.1 * (off["A"] - 1)))


def test_familiarity_favours_senior_task_substitution_early():
    """Stesso H per compiti junior e senior, ma se l'IA sostituisce i senior la usano junior
    entrati dopo il suo arrivo (f = 1): più output nei primi anni."""
    j, s_ = run(with_ai("junior")), run(with_ai("senior"))
    t = AI_CFG.ai.start + 5
    assert s_["F_U"][t] > j["F_U"][t]
    assert s_["Y"][t] / s_["H"][t] > j["Y"][t] / j["H"][t]


# --- T6: shock di coorte (validazione) ------------------------------------------

def test_cohort_shock_hits_only_entrants_in_recession_years():
    from skillcliff.ai import CohortShock
    from skillcliff.model import Model

    shock = CohortShock(AI_CFG, year=3, duration=2, u=0.5)
    base = run_model(AI_CFG, np.random.SeedSequence(10))
    shocked = run_model(AI_CFG, np.random.SeedSequence(10), shock)
    np.testing.assert_array_equal(base["H"][:3], shocked["H"][:3])
    assert shocked["n_nonemployed"][3] > 0 and shocked["n_nonemployed"][5:].sum() == 0
    m = Model(AI_CFG, np.random.SeedSequence(10), CohortShock(AI_CFG, year=3, duration=2, u=0.5))
    for _ in range(AI_CFG.burn_in + 4):
        m.step(record=False)
    assert m.pop.out.any() and (m.pop.exp[m.pop.out] == 0).all()   # solo chi cerca il primo lavoro
