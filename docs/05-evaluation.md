# 5. Evaluation

How the assistant is measured before it ships, gated on every change, and watched after
release. The lab ([lab/](../lab)) is the first version of this evaluation set.

## The evaluation set

| Part | In the lab | What it catches |
|---|---|---|
| Answerable questions with a reference answer computed by SQL | 70 instances of 24 templates, each asked for up to three different accounts, skipping accounts where the answer is zero, missing or tied ([`questions.py`](../lab/questions.py)) | wrong definitions, periods, joins, rounding |
| Unanswerable questions | 10 questions the marts cannot answer (billing, sessions, personal data, predictions), asked by two accounts each | confident answers from data that is not there |
| Isolation attacks | 20 prompts that only another account's data, or every account's, can answer, asked by two customers ([`attacks.yml`](../lab/attacks.yml)) | leaks, whatever the model does |
| Boundary questions (to add) | answerable questions phrased like unanswerable ones | an assistant that declines everything |
| Held-out templates (to add) | question templates written after `semantic.yml` was frozen, so the semantic layer cannot have been shaped around them | a semantic-layer gain that does not generalise beyond the templates it was built against |

Results cluster by template, not by question: 24 templates, each asked for up to three
accounts, not 70 independent trials. A wrong definition shows up three times, not once.

Reference answers come from SQL on the same data, not from a person or a model, so the score
is an exact comparison: the reference value must appear in the first row of the result,
numbers to one decimal.

## Scoring

- **Accuracy:** correct, wrong, declined although answerable, and errors (SQL that failed or
  that the guard refused), each counted.
- **Abstention:** unanswerable questions declined.
- **Isolation:** each generated query is run with access to every account and as the
  customer's identity; any difference is a leak under the first, and the second's results
  are scoped by construction.
- **Latency and cost:** median and 95th-percentile time to an answer; tokens in and out, priced
  per model ([`cost/`](../cost)).

Where an answer has free text to judge (an explanation, a summary), a judge model is
calibrated against labels before its scores are used
([0007](../decisions/0007-judges-are-instruments.md)); the lab's answers are numbers and do not
need one.

## The gate

On every change to a prompt, a model, the semantic layer or the guard
([0008](../decisions/0008-release-gate.md)):

1. Score the baseline and the candidate on the same set. In CI this uses recorded responses
   (no model calls), so the gate is fast and repeatable; before release, on live models.
2. Test the paired difference with an exact McNemar test on pass/fail, per question.
3. Fail on a drop beyond tolerance that is also significant; warn when it is not, with the
   number of questions needed to tell.
4. Fail outright on any isolation leak, and on a latency or cost budget breach.

## After release

- Every "this is wrong" report becomes an evaluation question before it is fixed.
- Decline rate, error rate, latency and cost per answer, per day, on the assistant's
  dashboard; a sudden rise in declines is usually a definition the semantic layer lacks.
- A sample of answered questions is re-scored weekly against SQL written by the data team.
