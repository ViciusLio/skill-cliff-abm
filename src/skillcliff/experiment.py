"""Repliche, salvataggio e caricamento dei risultati."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from skillcliff.config import Config, from_dict
from skillcliff.model import run_model


def replication_seeds(cfg: Config, n_reps: int | None = None) -> list[np.random.SeedSequence]:
    """La replica r ha lo stesso seed in ogni scenario: confronti a numeri casuali comuni."""
    return np.random.SeedSequence(cfg.seed).spawn(n_reps or cfg.n_reps)


def run_replications(cfg: Config, n_reps: int | None = None, ai_factory=None) -> dict[str, np.ndarray]:
    """Ritorna {metrica: array (repliche, T[, età])}. ai_factory(cfg) crea un modulo IA per replica."""
    runs = [
        run_model(cfg, ss, ai_factory(cfg) if ai_factory else None)
        for ss in replication_seeds(cfg, n_reps)
    ]
    return {k: np.stack([r[k] for r in runs]) for k in runs[0]}


def save_results(path: str | Path, cfg: Config, results: dict[str, np.ndarray]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, config=json.dumps(cfg.to_dict()), **results)


def load_results(path: str | Path) -> tuple[Config, dict[str, np.ndarray]]:
    with np.load(path) as data:
        cfg = from_dict(json.loads(str(data["config"])))
        return cfg, {k: data[k] for k in data.files if k != "config"}
