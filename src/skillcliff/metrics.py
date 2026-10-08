"""Metriche annuali e statistiche tra repliche."""
from __future__ import annotations

import numpy as np
from scipy import stats

# Serie scalari registrate ogni anno.
SCALARS = (
    "N", "n_junior", "n_mid", "n_senior", "n_meetings", "p_eff",
    "Y", "mean_h", "mean_h_junior", "mean_h_mid", "mean_h_senior",
    "B", "B_meet", "B_aut", "gini_w",
)


def gini(x: np.ndarray) -> float:
    """Indice di Gini (x >= 0)."""
    n = x.size
    if n == 0 or x.sum() <= 0:
        return 0.0
    xs = np.sort(x)
    i = np.arange(1, n + 1)
    return float(2.0 * np.sum(i * xs) / (n * xs.sum()) - (n + 1) / n)


def masked_mean(x: np.ndarray, mask: np.ndarray) -> float:
    return float(x[mask].mean()) if mask.any() else np.nan


def by_age(values: np.ndarray, age: np.ndarray, n_ages: int) -> tuple[np.ndarray, np.ndarray]:
    """Media e numerosità di values per età (indice = età)."""
    cnt = np.bincount(age, minlength=n_ages)[:n_ages]
    tot = np.bincount(age, weights=values, minlength=n_ages)[:n_ages]
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(cnt > 0, tot / cnt, np.nan), cnt


def mean_ci(x: np.ndarray, axis: int = 0, level: float = 0.95) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Media e intervallo di confidenza t di Student lungo l'asse delle repliche."""
    n = np.sum(~np.isnan(x), axis=axis)
    m = np.nanmean(x, axis=axis)
    se = np.nanstd(x, axis=axis, ddof=1) / np.sqrt(n)
    half = stats.t.ppf(0.5 + level / 2, df=np.maximum(n - 1, 1)) * se
    return m, m - half, m + half
