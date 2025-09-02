Markov AIS anomaly detection demo

This repository contains a small dataset (data/houston_data_small.csv) and a
simple example of training a Markov chain for anomaly detection.

Run the demo:

    python scripts/demo_markov.py

The script trains on speeds from the dataset, builds a transition matrix, and
reports improbable transitions as potential anomalies.
