# Evaluation

How a feature is evaluated before it ships, gated on every change, and watched after release.

## The evaluation set

- **Answerable cases** with a reference answer, computed from the data where possible (an answer key from SQL is better than one written by hand).
- **Unanswerable cases**: questions the feature's data cannot answer, labelled as such ([0003](../decisions/0003-abstention-is-an-answer.md)).
- **Adversarial cases**: instructions planted in data and documents, requests for other tenants' data, attempts to make a tool act.
- **Boundary cases**: answerable questions close to unanswerable ones, so a feature that declines everything fails.
- A content hash of the set is recorded with every run; runs over different sets are not compared.

## Scoring

- Deterministic checks first: exact values, required fields, abstention type, whether an action was proposed.
- Where free text has to be judged, a judge model calibrated against a labelled sample, reporting its true- and false-positive rates ([0005](../decisions/0005-judges-are-instruments.md)). Disagreements between judge and labels are read; either may be wrong.
- What is reported per run: accuracy, wrong answers that would have published themselves, unanswerable cases declined, unsafe proposals, p50 and p95 latency, tokens and cost per answer.

## The gate

On every change to a prompt, model, retrieval setting or tool ([0004](../decisions/0004-release-gate-on-paired-evaluation.md)):

1. Run baseline and candidate over the same cases, in CI on replayed responses, and before release on live models.
2. Test the paired difference: exact McNemar for pass/fail, paired bootstrap for scores.
3. Fail on a drop beyond tolerance that is also significant; warn on one that is not, with the sample size needed to tell.
4. Fail on a latency or cost budget breach, with its own exit code.

## After release

- Outcome metrics as they mature (resolution rates, corrections, reviewer overrides), not only input drift ([0010](../decisions/0010-promote-on-outcomes.md)).
- The review queue as a signal: what fails checks, and why.
- Every reported wrong answer becomes an evaluation case before it is fixed.
