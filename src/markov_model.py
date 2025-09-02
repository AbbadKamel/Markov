from __future__ import annotations

"""Simple discrete-time Markov chain with Laplace smoothing.

This module implements a first-order Markov chain that can be trained on a
sequence of discrete states.  After fitting, transition probabilities and
anomaly scores can be computed for new sequences.
"""

from collections import defaultdict
import math
from typing import Iterable, List


class MarkovChain:
    """First-order Markov chain for discrete states.

    Parameters
    ----------
    states:
        Iterable of all possible state labels.  The order is preserved and used
        to build the transition matrix.
    """

    def __init__(self, states: Iterable[str]):
        self.states: List[str] = list(states)
        # Count transitions from state i to j
        self._counts = {s: defaultdict(int) for s in self.states}
        # Probabilities P(j|i); start with Laplace smoothing (1 everywhere)
        self._probs = {s: {t: 1.0 for t in self.states} for s in self.states}

    def fit(self, sequence: Iterable[str]) -> None:
        """Estimate transition probabilities from a sequence of states."""
        seq = list(sequence)
        for a, b in zip(seq[:-1], seq[1:]):
            if a in self._counts and b in self._counts:
                self._counts[a][b] += 1
        # Convert counts to probabilities with Laplace smoothing
        for a in self.states:
            total = sum(self._counts[a][b] + 1 for b in self.states)
            self._probs[a] = {
                b: (self._counts[a][b] + 1) / total for b in self.states
            }

    def transition_prob(self, a: str, b: str) -> float:
        """Return probability of transitioning from ``a`` to ``b``."""
        return self._probs[a][b]

    def sequence_loglik(self, sequence: Iterable[str]) -> float:
        """Log-likelihood of a sequence under the model."""
        seq = list(sequence)
        loglik = 0.0
        for a, b in zip(seq[:-1], seq[1:]):
            loglik += math.log(self.transition_prob(a, b))
        return loglik

    def anomaly_scores(self, sequence: Iterable[str]) -> List[float]:
        """Negative log-probability for each transition in ``sequence``."""
        seq = list(sequence)
        scores = []
        for a, b in zip(seq[:-1], seq[1:]):
            scores.append(-math.log(self.transition_prob(a, b)))
        return scores
