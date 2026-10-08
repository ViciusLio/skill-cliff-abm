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

    cfg = with_ai("junior").with_overrides({"ai.displacement": True})
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
    ai = run(with_ai("junior").with_overrides({"ai.displacement": True}))
    s = AI_CFG.ai.start
    lag = AI_CFG.roles.senior_min_exp - AI_CFG.roles.junior_max_exp
    np.testing.assert_array_equal(base["H"][: s + 1], ai["H"][: s + 1])
    np.testing.assert_array_equal(base["mean_h_senior"][: s + lag], ai["mean_h_senior"][: s + lag])
    assert ai["mean_h_junior"][s + 3] < base["mean_h_junior"][s + 3]


def test_fixed_automation_cuts_junior_meetings_from_start():
    from skillcliff.ai import FixedAutomation

    base = run_model(AI_CFG, np.random.SeedSequence(6))
    fx = run_model(AI_CFG, np.random.SeedSequence(6), FixedAutomation(AI_CFG, phi=0.4))
    s = AI_CFG.ai.start
    np.testing.assert_array_equal(base["H"][:s], fx["H"][:s])
    assert fx["phi"][s] == 0.4 and fx["phi"][s - 1] == 0.0
    assert fx["p_eff"][s + 1] == pytest.approx(0.6 * AI_CFG.meetings.p)
    assert fx["H"][-1] < base["H"][-1]
