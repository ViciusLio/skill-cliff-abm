from pathlib import Path

import numpy as np
import pytest

from skillcliff import load_config
from skillcliff.experiment import run_replications
from skillcliff.learning import effective_meeting_prob, meeting_gains
from skillcliff.metrics import gini
from skillcliff.model import Model, run_model

BASE = load_config(Path(__file__).parents[1] / "configs" / "base.yaml")
SMALL = BASE.with_overrides({"population.N": 600, "burn_in": 50, "T": 15})


def run(cfg=SMALL, seed=7):
    return run_model(cfg, np.random.SeedSequence(seed))


# --- invarianti richiesti -------------------------------------------------

def test_agent_count_conserved_every_year():
    model = Model(SMALL, np.random.SeedSequence(1))
    for _ in range(SMALL.burn_in + SMALL.T):
        model.step()
        assert len(model.pop) == SMALL.population.N
    assert (model.pop.age < SMALL.population.retirement_age).all()


@pytest.mark.parametrize("dep", [0.012, 0.5, 0.99])
def test_h_never_negative(dep):
    cfg = SMALL.with_overrides({"learning.depreciation": dep})
    model = Model(cfg, np.random.SeedSequence(2))
    for _ in range(cfg.burn_in + cfg.T):
        model.step()
        assert (model.pop.h >= 0).all()


def test_p_zero_means_no_learning_from_meetings():
    r = run(SMALL.with_overrides({"meetings.p": 0.0}))
    assert (r["n_meetings"] == 0).all()
    assert (r["B_meet"] == 0).all()
    # stessa traiettoria di un modello in cui gli incontri avvengono ma non insegnano nulla
    r_beta0 = run(SMALL.with_overrides({"meetings.beta": 0.0}))
    np.testing.assert_array_equal(r["h_by_age"], r_beta0["h_by_age"])


def test_same_seed_identical_results():
    a, b = run(seed=11), run(seed=11)
    for k in a:
        np.testing.assert_array_equal(a[k], b[k])
    c = run(seed=12)
    assert not np.array_equal(a["mean_h"], c["mean_h"])


def test_replications_reproducible():
    a = run_replications(SMALL, n_reps=3, workers=1)
    b = run_replications(SMALL, n_reps=3, workers=3)   # in parallelo: stessi risultati
    np.testing.assert_array_equal(a["Y"], b["Y"])
    assert a["Y"].shape == (3, SMALL.T)


# --- regole del modello ---------------------------------------------------

def test_common_random_numbers_demography_independent_of_meetings():
    a = run(SMALL.with_overrides({"meetings.p": 0.9}))
    b = run(SMALL.with_overrides({"meetings.p": 0.1}))
    np.testing.assert_array_equal(a["n_by_age"], b["n_by_age"])
    assert (a["mean_h"] > b["mean_h"]).all()


def test_meeting_rule_is_beta_times_positive_gap():
    cfg = SMALL.with_overrides({"meetings.p": 1.0, "meetings.kappa": 10.0, "meetings.beta": 0.25,
                                "meetings.same_qual": False})
    h = np.array([1.0, 3.0, 0.5, 2.0])
    junior = np.array([True, True, False, False])
    senior = np.array([False, False, False, True])
    out = meeting_gains(cfg, h, junior, senior, np.random.default_rng(0))
    # junior 0 impara 0.25*(2-1); junior 1 è più bravo del senior e non impara nulla
    np.testing.assert_allclose(out.dh, [0.25, 0.0, 0.0, 0.0])
    assert out.n_meetings == 2


def test_capacity_rationing():
    assert effective_meeting_prob(0.6, 1.0, n_junior=100, n_senior=200) == 0.6
    assert effective_meeting_prob(0.6, 0.2, n_junior=100, n_senior=200) == pytest.approx(0.4)
    assert effective_meeting_prob(0.6, 1.0, n_junior=100, n_senior=0) == 0.0


def test_gini():
    assert gini(np.ones(10)) == pytest.approx(0.0)
    assert gini(np.array([0.0, 0.0, 0.0, 1.0])) == pytest.approx(0.75)


def test_uids_unique_and_meeting_pairs_are_junior_senior():
    from skillcliff.learning import role_masks

    model = Model(SMALL, np.random.SeedSequence(3))
    for _ in range(SMALL.burn_in + 5):
        model.step()
        pop, meet = model.pop, model.last_meet
        assert np.unique(pop.uid).size == len(pop)
        junior, senior = role_masks(SMALL, pop.exp)
        assert junior[meet.learners].all() and senior[meet.partners].all()
        assert meet.learners.size == meet.partners.size == meet.n_meetings
        # D1: ogni junior incontra un senior della propria qualifica
        assert (pop.high[meet.learners] == pop.high[meet.partners]).all()
