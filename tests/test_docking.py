import numpy as np
import pytest

pytest.importorskip("mesa")

from test_model import BASE  # noqa: E402

from skillcliff.experiment import run_replications  # noqa: E402
from skillcliff.mesa_twin import run_mesa  # noqa: E402


def test_mesa_twin_matches_numpy_model():
    cfg = BASE.with_overrides({"population.N": 400, "burn_in": 60, "T": 10})
    reps = 6
    a = run_replications(cfg, n_reps=reps)
    b = [run_mesa(cfg, seed=100 + r) for r in range(reps)]
    assert all((m["N"] == 400).all() for m in b)
    for k in ("mean_h", "mean_h_junior", "mean_h_senior", "B_meet", "B_aut"):
        x = a[k].mean(axis=1)
        y = np.array([m[k].mean() for m in b])
        se = np.sqrt(x.var(ddof=1) / reps + y.var(ddof=1) / reps)
        # differenza delle medie entro 4 errori standard (falsi allarmi ~1e-4)
        assert abs(x.mean() - y.mean()) < 4 * se + 1e-12, k
