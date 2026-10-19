# 0007. A model that judges answers is an instrument: calibrated against labels before its scores count

- Status: Accepted
- Date: 2026-10-19
- Deciders: data lead; proposed by the architect
- Evidence: evalproof_gold_errors, evalproof_reasoning_fpr

## Context

The assistant's numbers are scored exactly against SQL. Explanations, summaries and later
features (a help-centre assistant) have free text that only a person or a model can judge.
A judge model has error rates like any classifier, and so do hand labels.

## Decision drivers

- A8: a gate that fails for real regressions and not for noise.
- The cost of human labels.

## Options

| | Trustworthy | Cost |
|---|---|---|
| Trust a judge model's verdicts as they come | ✘ unknown error rates | ✔ |
| Human review of every answer | ✔ | ✘ |
| **Calibrate the judge on a labelled sample, report its true and false positive rates, and audit disagreements both ways** | ✔ | ◐ a sample |

## Decision

Exact checks first, wherever a reference can be computed. Where text must be judged, the
judge is calibrated against a labelled sample before its scores are used, and every
disagreement between judge and labels is read, because either may be wrong.

## Consequences

- Each new judged feature starts with a labelled sample.
- In the evalproof lab, the answer key, not the judge, was wrong in 7 of the disagreements
  read.

## Revisit when

A feature's judge passes calibration on a fresh sample twice in a row; the sample size can
then shrink.

## Evidence

<!-- evidence:start -->
- **7 vs 4** judge–key disagreements where the key, not the judge, was wrong. All 13 disagreements across both runs read by hand; 2 were ambiguous. Source: [evalproof/MEASUREMENTS.md](https://github.com/technobasant/evalproof/blob/main/MEASUREMENTS.md)
- **5.9% → 0.0%** false-positive rate of the judge on the baseline run, thinking off against thinking on. The same qwen3:8b judge on cached answers, scored against labels audited case by case wherever the answer key and the two judges disagreed (22 cases); thinking took 6.7 times the judge time (1,338 s against 201 s for 83 verdicts). Source: [evalproof/MEASUREMENTS.md](https://github.com/technobasant/evalproof/blob/main/MEASUREMENTS.md)
<!-- evidence:end -->
