from __future__ import annotations

"""Parsing utilities for simplified NMEA 2000 log files.

This module defines a :class:`Message` dataclass representing a single NMEA 2000
PGN message and helpers to read line oriented log files.  The log format used
throughout the proof of concept is intentionally simple:

    timestamp,pgn,field1=value1;field2=value2

Timestamps are in ISO-8601 format.  Field values are parsed as ``float`` and
stored in the :attr:`Message.fields` mapping.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, List


@dataclass
class Message:
    """Representation of a single NMEA 2000 message."""

    timestamp: float  # seconds since the UNIX epoch
    pgn: int
    fields: Dict[str, float]


def parse_line(line: str) -> Message:
    """Parse a single log ``line`` into a :class:`Message`.

    Parameters
    ----------
    line:
        Input string in the expected ``timestamp,pgn,key=value;...`` format.
    """

    ts_str, pgn_str, data_str = line.strip().split(",", 2)
    ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00")).timestamp()
    pgn = int(pgn_str)
    fields: Dict[str, float] = {}
    if data_str:
        for item in data_str.split(";"):
            if not item:
                continue
            key, value = item.split("=")
            fields[key] = float(value)
    return Message(timestamp=ts, pgn=pgn, fields=fields)


def load_messages(path: str) -> List[Message]:
    """Read a log file and return a list of :class:`Message` objects."""

    messages: List[Message] = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            messages.append(parse_line(line))
    return messages


def group_by_timestamp(messages: Iterable[Message]) -> List[Dict[int, Message]]:
    """Group messages that share a timestamp.

    Returns a list where each element is a mapping from PGN to the corresponding
    :class:`Message` observed at that timestamp.
    """

    grouped: List[Dict[int, Message]] = []
    current_ts: float | None = None
    current: Dict[int, Message] = {}
    for msg in sorted(messages, key=lambda m: m.timestamp):
        if current_ts is None or msg.timestamp != current_ts:
            if current:
                grouped.append(current)
                current = {}
            current_ts = msg.timestamp
        current[msg.pgn] = msg
    if current:
        grouped.append(current)
    return grouped
