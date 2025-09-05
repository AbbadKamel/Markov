Markov AIS anomaly detection demo

This repository contains a small dataset (data/houston_data_small.csv) and a
simple example of training a Markov chain for anomaly detection.

Run the demo:

    python scripts/demo_markov.py

The script trains on speeds from the dataset, builds a transition matrix, and
reports improbable transitions as potential anomalies.

NMEA 2000 anomaly detection proof of concept
-------------------------------------------

Synthetic NMEA 2000 traffic can be generated and analysed using Markov-chain
models.  The demo script will train on normal traffic and then score a test
sequence with injected anomalies:

    python scripts/demo_nmea2000.py

The implementation lives under ``src/`` and comprises a small parser, feature
engineering helpers, a detector combining Markov transitions with range and
correlation checks, and traffic simulation utilities.
