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

Modeling choices in ``demo_nmea2000.py``
---------------------------------------

The NMEA 2000 demo configures a simple first-order Markov chain with the
following conventions:

* **State space** – Each message is mapped to a discrete state derived from its
  PGN and binned values such as RPM or speed.
* **Transition matrix** – Consecutive states are counted for every PGN, then
  Laplace smoothing (add-one) is applied and the counts are normalised to form
  transition probabilities.
* **Initial distribution** – Transition tables start uniformly, which
  corresponds to an uninformed prior on the first observation.
* **Markov property** – The detector assumes the next state depends only on the
  current state, ignoring earlier history.
* **Stationary distribution** – No stationary distribution is computed; the
  model focuses on transition likelihoods for anomaly detection.
