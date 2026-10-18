# 0005. An LLM judge is an instrument: calibrated against labels, audited with them, and never trusted pairwise

- Status: Accepted
- Date: 2026-10-18
- Evidence: evalproof_gold_errors, evalproof_reasoning_fpr, evalproof_pairwise_flips

## Context

Most evaluation of free-text answers uses a model as the judge. A judge is a classifier with error rates; its pass rate is a classify-and-count estimate. The labels it is checked against have errors too.

## Decision

- Each judge is measured against a labelled sample: true-positive and false-positive rates, and agreement (Cohen's κ). Pass rates are reported with those rates, and corrected where the sample is large enough.
- Disagreements between the judge and the labels are read, not averaged: either can be wrong.
- Where the gate's correctness matters more than its speed, a reasoning judge is used: in the measurement below it passed no wrong answer, at several times the cost.
- Pairwise preference ("which answer is better") is a diagnostic only, judged in both orders, never a gate.

## Consequences

- Of 13 cases where the judge and the answer key disagreed, the key was wrong 7 times and the judge 4. Auditing the labels changed the conclusion more than tuning the judge would have.
- With reasoning on, the judge's false-positive rate on the baseline fell from 5.9% to 0.0%, at 6.7 times the judge time.
- 42.2% of pairwise verdicts flipped when the answer order was swapped.

## Alternatives considered

- **Trust the judge's pass rate.** Its bias is unknown, and so is the error in the comparison.
- **Pairwise judging for sensitivity.** Position and length biases dominate at this model size.

## Evidence

<!-- evidence:start -->
- **7 vs 4** judge–key disagreements where the key, not the judge, was wrong. All 13 disagreements across both runs read by hand; 2 were ambiguous. Source: [evalproof/MEASUREMENTS.md](https://github.com/technobasant/evalproof/blob/main/MEASUREMENTS.md)
- **5.9% → 0.0%** false-positive rate of the judge on the baseline run, thinking off against thinking on. The same qwen3:8b judge on cached answers, scored against labels audited case by case wherever the answer key and the two judges disagreed (22 cases); thinking took 6.7 times the judge time (1,338 s against 201 s for 83 verdicts). Source: [evalproof/MEASUREMENTS.md](https://github.com/technobasant/evalproof/blob/main/MEASUREMENTS.md)
- **42.2%** pairwise verdicts that flipped with answer order. 35 of 83 pairs judged in both orders (166 calls) by qwen3:8b; order-dependent verdicts are reported as ties. Source: [evalproof/MEASUREMENTS.md](https://github.com/technobasant/evalproof/blob/main/MEASUREMENTS.md)
<!-- evidence:end -->

## Related decisions in the labs

- evalproof [0001 An LLM judge is a classifier](https://github.com/technobasant/evalproof/blob/main/docs/adr/0001-judge-is-a-classifier.md)
