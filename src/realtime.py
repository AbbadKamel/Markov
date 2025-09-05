from __future__ import annotations

"""Real-time adapter for the anomaly detector."""

from typing import Iterable

from .detector import AnomalyDetector
from .parser import Message


def process_stream(detector: AnomalyDetector, stream: Iterable[Message]):
    """Process an iterable ``stream`` of messages and yield anomalies."""

    buffer = []
    for msg in stream:
        buffer.append(msg)
        # Grouping is simplified: we assume messages arrive in timestamp order
        if len(buffer) > 1000:
            steps = [{m.pgn: m} for m in buffer]
            for anomaly in detector.score(steps):
                yield anomaly
            buffer.clear()
