---
id: concept-lstm-autoencoder-anomaly-detection
title: "LSTM Autoencoder Anomaly Detection (CPT-0081)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-10-risk-management }
  - { type: governed-by, target: index-adr }
---
# LSTM Autoencoder Anomaly Detection (CPT-0081)

> Unsupervised detection of abnormal supply-chain signal patterns (demand spikes,
> lead-time outliers, OTD degradation): an LSTM encoder-decoder learns to reconstruct
> *normal* windows; what it cannot reconstruct is anomalous.

## Formula

    anomaly_error = MSE(window, reconstruction)          (mean over time × features)
    threshold     = percentile_{(1−FPR)·100}(errors on normal validation windows)
    is_anomaly    = error > threshold
    anomaly_score = clip(error / (3·threshold), 0, 1)

| Symbol | Meaning | Unit |
|---|---|---|
| window | (seq_len × n_features) slice of the signal | normalized units |
| FPR | target false-positive rate (default 0.02) | fraction |

## Inputs and outputs

- **Pipeline:** `build_sliding_windows` (series → overlapping (N, seq_len, F) windows;
  raises if T < seq_len) → `train_autoencoder` (normal-only windows; Adam lr 1e-3,
  early stopping patience 8; returns loss curves + best epoch) → `calibrate_threshold`
  (validation percentile) → `score_windows` (errors, flags, 0–1 scores, anomaly rate).

## Assumptions and limits

- **Training data must be clean-normal:** anomalies inside the training set get
  learned as normal and become invisible. Curate the training window (e.g. exclude
  known disruption periods).
- Threshold-by-percentile *guarantees* ~FPR false alarms on normal data — tune FPR to
  the alert budget, not to zero.
- Features should be scaled comparably (MSE mixes them); unscaled cents next to
  fractions makes money dominate the error.
- Windows overlap ⇒ scores autocorrelate — one real event flags several consecutive
  windows; deduplicate before counting incidents.
- Seed is not fixed in training — runs vary (recorded testing caveat).
- **Does not apply when:** labelled anomalies are plentiful (supervised classifiers
  beat reconstruction) or the series is short (< a few hundred points).

## Worked example

Daily 4-feature signal `[demand, price, lead_time, otd]`, seq_len 14 → windows;
*Illustrative only.* Train on disruption-free months, then calibrate the threshold to the
false-positive rate the operation can absorb — say an FPR giving a threshold of 0.031; a port-
strike fortnight reconstructs at 0.11 → score 1.0, flagged across its windows.

## Governing rules

- OSI-only (ADR-0002): PyTorch BSD-3. Alerts are advisory inputs to the risk register.

## Related

- CPT-0068 NLP monitoring — text-signal early warning; this is the numeric-signal
  counterpart.

## References

- Malhotra et al. (2016), LSTM encoder-decoder anomaly detection, ICML AD Workshop.
- Hundman et al. (2018), KDD — thresholding practice.
