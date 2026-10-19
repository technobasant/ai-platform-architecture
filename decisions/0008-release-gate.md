# 0008. Prompt, model and definition changes ship through a paired evaluation gate

- Status: Accepted
- Date: 2026-10-19
- Deciders: data lead, VP Product; proposed by the architect
- Evidence: evalproof_noise_gate, evalproof_latency_p95, aia_db_isolation

## Context

Every change to the prompt, the model, the semantic layer or the guard changes answers. Some
changes look like regressions and are noise; some real regressions are in latency or cost,
not accuracy.

## Decision drivers

- A8: no release that lowers A1, A2 or A3; A5, A6 budgets.
- Not blocking good changes on noise.

## Options

| | Catches real drops | Ignores noise | Covers isolation, latency, cost |
|---|---|---|---|
| Ship and watch | ✘ | ✔ | ✘ |
| Fail on any drop in the score | ✔ | ✘ | ✘ |
| **Paired comparison on the same questions with a significance test, plus hard fails on isolation, latency and cost** | ✔ | ✔ | ✔ |

## Decision

Baseline and candidate are scored on the same evaluation set: in CI from recorded responses,
before release on live models. A drop beyond tolerance that is significant on an exact
McNemar test fails; one that is not warns with the sample size needed. Any isolation leak, or
a latency or cost budget breach, fails outright.

## Consequences

- A 4.8-point drop with p = 0.39 is a warning, not a failure, and a p95 regression from 1.5 s
  to 4.4 s fails on its own budget, as in the evalproof lab.
- The evaluation set grows with every reported wrong answer, so the gate's power grows too.

## Revisit when

The set is large enough that tolerances, not significance, decide most changes.

## Evidence

<!-- evidence:start -->
- **p = 0.39** for a 4.8-point judge drop the gate declined to fail. Exact McNemar on 83 paired cases — 8 worse, 4 better, 71 unchanged — qwen3:1.7b judged by qwen3:8b on Ollama, temperature 0. Source: [evalproof/MEASUREMENTS.md](https://github.com/technobasant/evalproof/blob/main/MEASUREMENTS.md)
- **1,469 → 4,422 ms** p95 latency, the regression that was real. System latency over the same 83 cases, sequential, one Apple M5; mean answer length went from 19 to 77 tokens. Source: [evalproof/MEASUREMENTS.md](https://github.com/technobasant/evalproof/blob/main/MEASUREMENTS.md)
- **0 of 28** queries that reached the database (of the 120 requests; the rest were declined) and returned another account's data, run as the customer's own database role. One read-only login role per account, row-level security on every table keyed on the session's login role; each role sees 1 of the 200 accounts. Source: [ai-platform-architecture/results/assistant.json](https://github.com/technobasant/ai-platform-architecture/blob/main/results/assistant.json)
<!-- evidence:end -->
