from __future__ import annotations

"""Anomaly detection pipeline for NMEA 2000 traffic."""

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple
import math

from .markov_model import MarkovChain
from .parser import Message
from . import features


@dataclass
class Anomaly:
    timestamp: float
    pgn: int
    value: float
    score: float
    reason: str


class AnomalyDetector:
    """Combines Markov and statistical checks for anomaly detection."""

    def __init__(self, transition_threshold: float = 5.0, range_k: float = 3.0):
        self.transition_threshold = transition_threshold
        self.range_k = range_k
        self.models: Dict[int, MarkovChain] = {}
        self.stats: Dict[Tuple[int, str], Tuple[float, float]] = {}
        self.corr_model: MarkovChain | None = None

    def _update_stats(self, values: List[float]) -> Tuple[float, float]:
        mean = sum(values) / len(values)
        var = sum((v - mean) ** 2 for v in values) / len(values)
        std = math.sqrt(var)
        return mean, std

    def train(self, steps: Iterable[Dict[int, Message]]) -> None:
        sequences: Dict[int, List[str]] = {}
        values: Dict[Tuple[int, str], List[float]] = {}
        corr_sequence: List[str] = []

        for step in steps:
            for pgn, msg in step.items():
                state = features.message_state(msg)
                sequences.setdefault(pgn, []).append(state)
                for k, v in msg.fields.items():
                    values.setdefault((pgn, k), []).append(v)
            if features.PGN_ENGINE in step and features.PGN_SPEED in step:
                corr_sequence.append(
                    features.rpm_speed_state(
                        step[features.PGN_ENGINE], step[features.PGN_SPEED]
                    )
                )

        for pgn, seq in sequences.items():
            states = sorted(set(seq))
            model = MarkovChain(states)
            model.fit(seq)
            self.models[pgn] = model

        for key, vals in values.items():
            self.stats[key] = self._update_stats(vals)

        if corr_sequence:
            states = sorted(set(corr_sequence))
            self.corr_model = MarkovChain(states)
            self.corr_model.fit(corr_sequence)

    def score(self, steps: Iterable[Dict[int, Message]]) -> List[Anomaly]:
        anomalies: List[Anomaly] = []
        prev_state: Dict[int, str] = {}
        prev_corr: str | None = None

        for step in steps:
            # Transition and range checks
            for pgn, msg in step.items():
                if pgn not in self.models:
                    continue
                state = features.message_state(msg)
                model = self.models[pgn]
                if state not in model.states:
                    anomalies.append(
                        Anomaly(
                            timestamp=msg.timestamp,
                            pgn=pgn,
                            value=list(msg.fields.values())[0],
                            score=float("inf"),
                            reason="unknown_state",
                        )
                    )
                else:
                    if pgn in prev_state:
                        prob = model.transition_prob(prev_state[pgn], state)
                        score = -math.log(prob)
                        if score > self.transition_threshold:
                            anomalies.append(
                                Anomaly(
                                    timestamp=msg.timestamp,
                                    pgn=pgn,
                                    value=list(msg.fields.values())[0],
                                    score=score,
                                    reason="transition",
                                )
                            )
                    prev_state[pgn] = state
                for k, v in msg.fields.items():
                    mean, std = self.stats.get((pgn, k), (0.0, 0.0))
                    if std and abs(v - mean) > self.range_k * std:
                        anomalies.append(
                            Anomaly(
                                timestamp=msg.timestamp,
                                pgn=pgn,
                                value=v,
                                score=abs(v - mean) / std,
                                reason=f"range_{k}",
                            )
                        )

            # Correlation check
            if self.corr_model and features.PGN_ENGINE in step and features.PGN_SPEED in step:
                corr_state = features.rpm_speed_state(
                    step[features.PGN_ENGINE], step[features.PGN_SPEED]
                )
                if corr_state not in self.corr_model.states:
                    anomalies.append(
                        Anomaly(
                            timestamp=step[features.PGN_ENGINE].timestamp,
                            pgn=features.PGN_ENGINE,
                            value=step[features.PGN_ENGINE].fields["rpm"],
                            score=float("inf"),
                            reason="unknown_corr_state",
                        )
                    )
                else:
                    if prev_corr is not None:
                        prob = self.corr_model.transition_prob(prev_corr, corr_state)
                        score = -math.log(prob)
                        if score > self.transition_threshold:
                            anomalies.append(
                                Anomaly(
                                    timestamp=step[features.PGN_ENGINE].timestamp,
                                    pgn=features.PGN_ENGINE,
                                    value=step[features.PGN_ENGINE].fields["rpm"],
                                    score=score,
                                    reason="correlation_rpm_speed",
                                )
                            )
                    prev_corr = corr_state

        return anomalies
