"""Demonstration of NMEA 2000 anomaly detection."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src import simulate, parser, detector


def main() -> None:
    train_steps = simulate.generate_normal(200)
    test_steps = simulate.inject_anomalies(simulate.generate_normal(80))

    tmp = ROOT / "data"
    tmp.mkdir(exist_ok=True)
    train_file = tmp / "train.log"
    test_file = tmp / "test.log"
    simulate.write_steps(str(train_file), train_steps)
    simulate.write_steps(str(test_file), test_steps)

    train_msgs = parser.load_messages(str(train_file))
    test_msgs = parser.load_messages(str(test_file))
    train_grouped = parser.group_by_timestamp(train_msgs)
    test_grouped = parser.group_by_timestamp(test_msgs)

    det = detector.AnomalyDetector()
    det.train(train_grouped)
    anomalies = det.score(test_grouped)
    print(f"Detected {len(anomalies)} anomalies")
    for a in anomalies[:5]:
        print(a)


if __name__ == "__main__":
    main()
