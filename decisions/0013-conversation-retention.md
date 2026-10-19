# 0013. Questions and answers are kept 30 days, never used for training, and erased on request

- Status: Proposed
- Date: 2026-10-19
- Deciders: security and compliance lead, VP Product; proposed by the architect
- Evidence:

## Context

Customers type questions that can contain names, e-mail addresses or anything else. Support
needs recent conversations to investigate a wrong answer; the DPA commits to erasure within
30 days; nothing in the brief needs conversations kept longer.

## Decision drivers

- A7: 30 days of traceability; A11: erasure.
- GDPR storage limitation; the DPA.

## Options

| | Support can investigate | Erasure is simple | Training risk |
|---|---|---|---|
| Keep indefinitely | ✔ | ✘ | ✘ |
| Keep nothing | ✘ | ✔ | ✔ |
| **30 days, deleted by user on request, excluded from any training** | ✔ | ✔ | ✔ |

## Decision

Proposed until the retention job and erasure are built and drilled: traces and recorded
responses expire after 30 days; an erasure request deletes the user's records within 7;
provider settings forbid training on prompts; evaluation questions taken from real
conversations are rewritten without personal data before they enter the set.

## Consequences

- Investigations of answers older than 30 days rely on the evaluation set, not the traces.
- The model provider's retention must match, which the platform's model serving terms set.

## Revisit when

The retention job and the erasure drill pass; then Accepted.

## Evidence

<!-- evidence:start -->
Not measured yet; see the status above.
<!-- evidence:end -->
