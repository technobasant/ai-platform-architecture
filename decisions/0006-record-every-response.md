# 0006. Every model response is recorded with its prompt's hash, and can be re-scored without the model

- Status: Accepted
- Date: 2026-10-19
- Deciders: data lead; proposed by the architect
- Evidence: aia_replay, agent_replay

## Context

A wrong answer reported by a customer has to be reproduced; a change to the guard or the
checker has to be judged on the same answers; CI cannot call paid models on every commit.
Models are not deterministic enough to reproduce a past answer by asking again.

## Decision drivers

- A7: traceability for 30 days; A8: change safety.
- CI that is fast, free and repeatable.

## Options

| | Reproduce a reported answer | Re-score after a code change | CI without models |
|---|---|---|---|
| Log the final answer only | ◐ | ✘ | ✘ |
| Ask the model again | ✘ not the same answer | ◐ | ✘ |
| **Record each response, keyed by a hash of its exact prompt; replay re-runs everything after the model** | ✔ | ✔ | ✔ |

## Decision

Every model response is stored with the hash of its prompt, the model, tokens and latency.
Scoring, isolation checks and cost are re-computed from recordings; a changed prompt has a
new hash and is asked again rather than scored on an old answer. In production the same
records are the traces kept for 30 days ([0013](0013-conversation-retention.md)).

## Consequences

- The lab's 660 responses are re-scored in CI against a freshly built mart, and must
  reproduce the published results exactly.
- Recordings of customer questions are personal data: they follow the retention and erasure
  rules.

## Revisit when

Never as a practice; the storage moves to the gateway's trace store in production.

## Evidence

<!-- evidence:start -->
- **660** recorded model responses re-scored in CI against a fresh mart, with no model called. Every response is stored with a hash of its prompt; replay re-runs extraction, execution as the customer's role and scoring, and must reproduce results/assistant.json. Source: [ai-platform-architecture/results/assistant-responses.jsonl](https://github.com/technobasant/ai-platform-architecture/blob/main/results/assistant-responses.jsonl)
- **54 of 54** cases where replaying the recorded model reproduced the live run's output. The live run's model responses recorded once and replayed in CI, so tests and the eval gate run with no model. Source: [governed-agent/MEASUREMENTS.md](https://github.com/technobasant/governed-agent/blob/main/MEASUREMENTS.md)
<!-- evidence:end -->
