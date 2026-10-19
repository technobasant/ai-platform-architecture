# 0010. Every model call goes through one gateway: budgeted, recorded, with a fallback

- Status: Accepted
- Date: 2026-10-19
- Deciders: data lead, CTO; proposed by the architect
- Evidence: evalproof_determinism, agent_replay

## Context

The assistant calls a hosted model on every question; later features will call others. Cost
limits, fallbacks, recording and redaction are needed for each, and are easy to get wrong
when each feature calls providers directly.

## Decision drivers

- A6: a monthly ceiling, enforced; A7: every call recorded.
- Availability: a second model when the first fails.

## Options

| | Budgets | Fallback | Recording | Build effort |
|---|---|---|---|---|
| Each feature calls the provider | ✘ | ✘ | ◐ | ✔ |
| The platform's AI gateway, if the platform offers one | ✔ | ◐ | ✔ | ✔ |
| **One gateway in front of every provider, the platform's where it covers these, a thin service where not** | ✔ | ✔ | ✔ | ◐ |

## Decision

One gateway: per-feature and per-account budgets, the fallback order from
[0005](0005-model-choice.md), and a record of every call with its prompt hash, model, tokens
and latency ([0006](0006-record-every-response.md)). Whether it is the platform's own gateway
or a thin service is decided with the platform.

## Consequences

- The cost ceiling is enforced in one place; the assistant degrades to "try again later" at
  the budget, not to an invoice.
- Replay from recordings makes runs repeatable: in the governed-agent lab, every recorded run
  replayed to the same outputs.

## Revisit when

A second AI feature needs a provider the gateway cannot reach.

## Evidence

<!-- evidence:start -->
- **20 of 20** cases with identical outputs, verdicts and judge reasons when re-run with the cache off. Temperature 0 and seed 0 on local models through Ollama 0.23.2; checked on this backend only. Source: [evalproof/MEASUREMENTS.md](https://github.com/technobasant/evalproof/blob/main/MEASUREMENTS.md)
- **54 of 54** cases where replaying the recorded model reproduced the live run's output. The live run's model responses recorded once and replayed in CI, so tests and the eval gate run with no model. Source: [governed-agent/MEASUREMENTS.md](https://github.com/technobasant/governed-agent/blob/main/MEASUREMENTS.md)
<!-- evidence:end -->
