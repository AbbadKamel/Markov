from __future__ import annotations

"""Synthetic NMEA 2000 traffic generation for proof of concept."""

from dataclasses import dataclass
from datetime import datetime, timedelta
import random
from typing import Dict, List

from .parser import Message
from . import features


@dataclass
class Step:
    timestamp: float
    messages: Dict[int, Message]


def _next_timestamp(ts: datetime) -> datetime:
    return ts + timedelta(seconds=1)


def generate_normal(n_steps: int, seed: int = 0) -> List[Step]:
    random.seed(seed)
    steps: List[Step] = []
    ts = datetime(2024, 1, 1)
    heading = 0.0
    speed = 8.0
    rpm = 800.0
    wind_speed = 10.0
    wind_dir = 90.0

    for _ in range(n_steps):
        heading = (heading + random.uniform(-2, 2)) % 360
        speed = max(0.0, speed + random.uniform(-0.5, 0.5))
        rpm = max(0.0, speed * 100 + random.uniform(-50, 50))
        wind_speed = max(0.0, wind_speed + random.uniform(-1, 1))
        wind_dir = (wind_dir + random.uniform(-5, 5)) % 360

        messages = {
            features.PGN_HEADING: Message(ts.timestamp(), features.PGN_HEADING, {"heading": heading}),
            features.PGN_SPEED: Message(ts.timestamp(), features.PGN_SPEED, {"speed": speed}),
            features.PGN_ENGINE: Message(ts.timestamp(), features.PGN_ENGINE, {"rpm": rpm}),
            features.PGN_WIND: Message(ts.timestamp(), features.PGN_WIND, {"wind_speed": wind_speed, "wind_dir": wind_dir}),
        }
        steps.append(Step(ts.timestamp(), messages))
        ts = _next_timestamp(ts)
    return steps


def inject_anomalies(steps: List[Step], rate: float = 0.05, seed: int = 1) -> List[Step]:
    random.seed(seed)
    anomalous = []
    for step in steps:
        messages = dict(step.messages)
        if random.random() < rate:
            # Out-of-range anomaly in speed
            messages[features.PGN_SPEED] = Message(step.timestamp, features.PGN_SPEED, {"speed": random.uniform(-5, 50)})
        if random.random() < rate:
            # Correlation anomaly: high speed but zero RPM
            messages[features.PGN_ENGINE] = Message(step.timestamp, features.PGN_ENGINE, {"rpm": 0.0})
            messages[features.PGN_SPEED] = Message(step.timestamp, features.PGN_SPEED, {"speed": 15.0})
        anomalous.append(Step(step.timestamp, messages))
    return anomalous


def write_steps(path: str, steps: List[Step]) -> None:
    with open(path, "w") as fh:
        for step in steps:
            for msg in step.messages.values():
                data = ";".join(f"{k}={v}" for k, v in msg.fields.items())
                ts = datetime.fromtimestamp(msg.timestamp).isoformat()
                fh.write(f"{ts},{msg.pgn},{data}\n")
