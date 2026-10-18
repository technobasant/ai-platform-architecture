# 0010. Models are promoted on a paired improvement within a latency budget, and watched on outcomes, not only on input drift

- Status: Accepted
- Date: 2026-10-18
- Evidence: rtml_cost_saved, rtml_drift_psi

## Context

A new model is usually "better on validation". Whether it is better on what the business pays for, at the latency the product needs, is a different test. After release, input-distribution metrics are the easiest thing to watch and can miss the change that matters.

## Decision

- A candidate runs in shadow on live traffic. It is promoted only on a significant paired improvement on the outcome metric (for fraud: cost saved), within the latency budget.
- Monitoring watches outcomes as they mature (labels, costs) alongside input drift, and alerts on the outcome.

## Consequences

- On two unseen weeks, the promoted model saved 82.5% of fraud cost.
- Population stability on features caught 0 of 5 simulated changes in fraud tactics. Input drift is a hint, not the alarm.
- Outcome monitoring is only as fast as labels mature; for slow labels a proxy outcome is chosen and stated.

## Alternatives considered

- **Promote on offline validation.** Validation sets are where leakage hides ([0009](0009-point-in-time-features.md)).
- **Alert on feature drift.** Measured above: it missed what mattered.

## Evidence

<!-- evidence:start -->
- **82.5%** of fraud cost saved on two unseen weeks. A $5 review per flag plus the amount of every missed fraud, against approving everything; threshold chosen on the validation window, true labels. A hand-written rule saved 20.7%. Source: [realtime-ml/MEASUREMENTS.md](https://github.com/technobasant/realtime-ml/blob/main/MEASUREMENTS.md)
- **0 of 5** tactics drifts caught by feature PSI. Five seeded runs with a fraud-tactics drift and five without, monitors replayed every 6 hours over the trailing 24; calendar-trending features excluded, threshold 0.2 or 0.1. Source: [realtime-ml/MEASUREMENTS.md](https://github.com/technobasant/realtime-ml/blob/main/MEASUREMENTS.md)
<!-- evidence:end -->

## Related decisions in the labs

- realtime-ml [0005 Promote only on a significant paired improvement within the latency budget](https://github.com/technobasant/realtime-ml/blob/main/docs/adr/0005-promotion-gate.md), [0007 Drift monitoring](https://github.com/technobasant/realtime-ml/blob/main/docs/adr/0007-drift-monitoring.md)
