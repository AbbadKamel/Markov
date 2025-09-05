from __future__ import annotations

"""Feature engineering utilities for NMEA 2000 messages."""

from typing import Dict
from .parser import Message

# PGN identifiers used in the proof of concept
PGN_HEADING = 127250
PGN_SPEED = 128259
PGN_ENGINE = 127488
PGN_WIND = 130306

# Discretization bins and labels per field
_BINS: Dict[int, Dict[str, list[float]]] = {
    PGN_HEADING: {"heading": [0.0, 90.0, 180.0, 270.0, 360.0]},
    PGN_SPEED: {"speed": [0.0, 5.0, 10.0, 20.0, float("inf")]},
    PGN_ENGINE: {"rpm": [0.0, 1000.0, 2000.0, 3000.0, float("inf")]},
    PGN_WIND: {
        "wind_speed": [0.0, 5.0, 15.0, 30.0, float("inf")],
        "wind_dir": [0.0, 90.0, 180.0, 270.0, 360.0],
    },
}

_LABELS: Dict[int, Dict[str, list[str]]] = {
    PGN_HEADING: {"heading": ["0_90", "90_180", "180_270", "270_360"]},
    PGN_SPEED: {"speed": ["0_5", "5_10", "10_20", "20_inf"]},
    PGN_ENGINE: {"rpm": ["0_1k", "1k_2k", "2k_3k", "3k_inf"]},
    PGN_WIND: {
        "wind_speed": ["0_5", "5_15", "15_30", "30_inf"],
        "wind_dir": ["0_90", "90_180", "180_270", "270_360"],
    },
}

_PGN_LABEL = {
    PGN_HEADING: "HDG",
    PGN_SPEED: "SPD",
    PGN_ENGINE: "RPM",
    PGN_WIND: "WND",
}


def _discretize(value: float, bins: list[float], labels: list[str]) -> str:
    for i in range(len(bins) - 1):
        if bins[i] <= value < bins[i + 1]:
            return labels[i]
    return labels[-1]


def message_state(msg: Message) -> str:
    """Return discretized state label for ``msg``."""

    pgn_label = _PGN_LABEL.get(msg.pgn, str(msg.pgn))
    fields = _BINS.get(msg.pgn, {})
    labels = _LABELS.get(msg.pgn, {})
    parts: list[str] = []
    for key, bins in fields.items():
        if key in msg.fields:
            parts.append(_discretize(msg.fields[key], bins, labels[key]))
    if not parts:
        parts.append("unknown")
    return f"{pgn_label}_" + "_".join(parts)


def rpm_speed_state(rpm_msg: Message, speed_msg: Message) -> str:
    """Joint state capturing RPM and speed correlation."""

    rpm_state = message_state(rpm_msg)
    speed_state = message_state(speed_msg)
    return f"{rpm_state}|{speed_state}"
