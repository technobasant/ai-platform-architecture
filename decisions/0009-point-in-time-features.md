# 0009. Model features are point-in-time correct, from one definition online and offline

- Status: Accepted
- Date: 2026-10-18
- Evidence: rtml_leakage, rtml_parity, rtml_serve_p99

## Context

The data platform holds the history models train on. A training set joined without regard to time teaches the model the future; a feature computed one way offline and another way online drifts between training and serving.

## Decision

- Training sets are built with point-in-time joins from the platform's history.
- Every feature is defined once and materialised offline and online; a parity test compares what training saw with what serving returns.
- Labels are used only once mature.

This mirrors decision 0011 of the [data platform architecture](https://github.com/technobasant/data-platform-architecture/blob/main/decisions/0011-point-in-time-features.md), which owns the storage side.

## Consequences

- A naive join scored an AUC-PR of 0.363 on the next two weeks; the point-in-time join scored 0.941.
- 99.905% of 9,500 live requests were served exactly the features training used, at a server-side p99 of 4.3 ms or less to fetch features and score.

## Alternatives considered

- **Features computed in the model service.** Fast to start; training and serving diverge.

## Evidence

<!-- evidence:start -->
- **0.363 vs 0.941** future AUC-PR, naive join against point-in-time join. Same rows, labels, model and hyperparameters; only the training join differs. Scored on the two weeks after training with point-in-time features and true labels, on seeded synthetic payments (874,446 transactions, 0.80% fraud). Source: [realtime-ml/MEASUREMENTS.md](https://github.com/technobasant/realtime-ml/blob/main/MEASUREMENTS.md)
- **99.905%** of 9,500 live requests served exactly the training features. Features logged by the API compared with Feast's point-in-time join for the same transactions, on a live stack replaying a day in about seven minutes. Source: [realtime-ml/MEASUREMENTS.md](https://github.com/technobasant/realtime-ml/blob/main/MEASUREMENTS.md)
- **≤ 4.3 ms** server-side p99 to fetch features and score. The API's own timer around the Feast online read and the model, at 25, 50 and 100 requests/s after a 500-request warm-up (whose p99 was 22.4 ms); 9,000 requests, 0 errors; every container on one 8-CPU VM, so no network hops. Source: [realtime-ml/MEASUREMENTS.md](https://github.com/technobasant/realtime-ml/blob/main/MEASUREMENTS.md)
<!-- evidence:end -->

## Related decisions in the labs

- realtime-ml [0002 Two implementations of each feature, held together by a parity test](https://github.com/technobasant/realtime-ml/blob/main/docs/adr/0002-two-implementations-of-each-feature.md), [0004 Label maturity](https://github.com/technobasant/realtime-ml/blob/main/docs/adr/0004-label-maturity.md)
