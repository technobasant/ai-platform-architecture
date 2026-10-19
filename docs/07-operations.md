# 7. Operations

How the data team runs the assistant. It is customer-facing, so it has an on-call path the
batch platform does not: the product's on-call is paged if the assistant is down or leaking,
and everything else waits for business hours.

## What is watched

| Signal | Threshold | Goes to |
|---|---|---|
| An isolation test fails in CI | any | blocks the deploy |
| A leak reported by a customer or support | any | the product's on-call; the assistant is switched off |
| Error rate (model, guard or SQL) | 5% over 15 minutes | data team, business hours |
| Decline rate | doubles against last week | data team: usually a missing definition |
| p95 latency | above 10 s for an hour | data team |
| Spend against the monthly ceiling | 50%, 80%, 100% | data lead; at 100% the gateway stops new questions |
| "This is wrong" reports | any | support triages; each becomes an evaluation question |

## Runbooks

### A customer reports another account's data

Switch the assistant off with its feature flag. Find the trace by question and time; re-run
its SQL as the customer's identity and as an unrestricted one; if they differ and the
customer saw the unrestricted result, the identity or policy is wrong. Fix it, add the
question to the isolation suite, and tell security: it is a reportable incident under the
DPA.

### A wrong answer is reported

Reproduce it from the trace. If the SQL is wrong, find the missing or ambiguous definition
in the semantic layer, add the question to the evaluation set with its reference SQL, fix
the definition, and ship through the gate. If the data is wrong, it is the platform's
incident, not the assistant's.

### A model or prompt change

Through the gate only: the evaluation set on recorded responses in CI, then on the live
model before release ([0008](../decisions/0008-release-gate.md)). A model change also re-runs
the isolation suite and the cost estimate.

### The model provider is down or rate-limited

The gateway falls back to the second model in the list; if that fails too, the assistant
answers "try again shortly" and the product carries on.

### Spend jumps

Find the account or question pattern in the gateway's logs by tag; rate-limit the account
or raise the ceiling; check the prompt has not grown.

### Erasure

Delete the user's questions and answers from traces and recorded responses; the platform's
erasure covers the marts.
