# 0008. Counts from a classifier are corrected for its error rates, and a model upgrade may not move a trend

- Status: Accepted
- Date: 2026-10-18
- Evidence: prev_cc_slope, prev_cc_coverage, prev_upgrade_trend

## Context

Dashboards built on a classifier count its labels: share of tickets about billing, share of sessions with frustration. A classifier's errors do not cancel when counted. They flatten every trend, and they change whenever the model does.

## Decision

- Shares reported over time are estimated, not counted: adjusted classify-and-count with error rates from a validation set, or prediction-powered inference with a small labelled sample from each period.
- Each reported share carries an interval.
- A model upgrade ships with a re-estimated history, or with a marked break in the series; it never silently changes a trend line.

## Consequences

- Counting a 95%-accurate classifier's labels recovered 0.628 of a real trend, and its naive intervals covered the truth in 0.0% of 12,000 period estimates. Adjusted counting recovered 1.003, and its intervals covered 95.0%.
- Upgrading the classifier on a flat series produced an apparent rise of 24.2%, and counted labels reported it as a significant trend in every replication.
- Estimation needs labelled samples per period: a small, recurring labelling budget.

## Alternatives considered

- **Count labels and improve the model.** A better model still has error rates, and changing it changes the series.

## Evidence

<!-- evidence:start -->
- **0.628** of the true trend recovered by counting a 95%-accurate classifier's labels. Prevalence rising from 10% to 25%; classifier TPR 0.645 and FPR 0.0166 at its training prior, so the counted share moves at TPR − FPR times the true one; adjusted classify-and-count recovered 1.003. Source: [prevalence-shift/MEASUREMENTS.md](https://github.com/technobasant/prevalence-shift/blob/main/MEASUREMENTS.md)
- **0.0%** of 12,000 period estimates where the naive 95% interval of counted labels covered the true prevalence. The same rising series; adjusted classify-and-count covered 95.0%, prediction-powered inference 94.7%. Source: [prevalence-shift/MEASUREMENTS.md](https://github.com/technobasant/prevalence-shift/blob/main/MEASUREMENTS.md)
- **+24.2%** apparent change in a flat 15% series when the classifier was upgraded mid-series and its labels were counted. True change zero; the upgrade changed the classifier's error rates, and counting labels reported them as a trend in 100% of replications. Source: [prevalence-shift/MEASUREMENTS.md](https://github.com/technobasant/prevalence-shift/blob/main/MEASUREMENTS.md)
<!-- evidence:end -->

## Related decisions in the labs

- prevalence-shift [README](https://github.com/technobasant/prevalence-shift#readme)
