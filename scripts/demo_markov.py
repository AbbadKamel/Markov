"""Train a simple Markov chain on AIS speed data and report anomalies."""

from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import List

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from markov_model import MarkovChain

# Discretization of speed over ground (SOG) into qualitative states
BINS = [0.0, 1.0, 5.0, 15.0, float("inf")]
LABELS = ["stopped", "slow", "medium", "fast"]


def discretize_sog(sog: float) -> str:
    for i in range(len(BINS) - 1):
        if BINS[i] <= sog < BINS[i + 1]:
            return LABELS[i]
        
    return LABELS[-1]


def load_states(path: str, limit: int | None = None) -> List[str]:
    """Read ``limit`` rows from ``path`` and return discretized states."""
    states: List[str] = []
    with open(path, newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) <= 5:
                continue
            try:
                sog = float(row[5])
            except ValueError:
                continue
            states.append(discretize_sog(sog))
            if limit is not None and len(states) >= limit:
                break
    return states


def main() -> None:
    # Load up to 60k states to keep runtime reasonable
    states = load_states("data/houston_data_small.csv", limit=60000)
    train, test = states[:50000], states[50000:]

    model = MarkovChain(LABELS)
    model.fit(train)

    scores = model.anomaly_scores(test)
    threshold = 5.0  # equivalent to probability < exp(-5) ≈ 0.0067
    anomalies = [(i, s) for i, s in enumerate(scores) if s > threshold]

    print(f"Loaded {len(states)} states: {len(train)} train, {len(test)} test")
    print(f"Found {len(anomalies)} anomalies with score > {threshold}")

    for i, score in anomalies[:5]:
        a, b = test[i], test[i + 1]
        prob = model.transition_prob(a, b)
        print(f"{i}: {a}->{b}, prob={prob:.5f}, score={score:.2f}")

    avg = sum(scores) / len(scores) if scores else 0.0
    print(f"Average score: {avg:.3f}")


if __name__ == "__main__":
    main()
