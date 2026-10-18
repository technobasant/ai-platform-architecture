# 0004. Prompt and model changes ship through a paired evaluation gate, with latency and cost gated separately

- Status: Accepted
- Date: 2026-10-18
- Evidence: evalproof_noise_gate, evalproof_latency_p95

## Context

Every change to a prompt, a model, a retrieval setting or a tool changes the feature's behaviour. A gate that compares two pass rates against a tolerance fails harmless changes on noise and gets switched off; a gate with no statistics passes real regressions.

## Decision

- Baseline and candidate run on the same cases; the comparison is paired (exact McNemar for pass/fail, paired bootstrap for scores), against a dataset hash both runs share.
- A change fails only when the drop is both beyond tolerance and significant. A large drop that is not significant passes with a warning that names the sample size needed.
- Latency (p95) and cost per answer have budgets of their own, with their own exit codes, because they are often the regression the data can see.
- The gate runs in CI on replayed model responses ([0011](0011-model-gateway.md)), and on live models before a release.

## Consequences

- A 4.8-point drop from 8 worse and 4 better answers out of 83 was p = 0.39: the gate warned instead of failing, and said how many cases it would take to know.
- The same change tripled p95 latency, from 1,469 ms to 4,422 ms, and the latency budget failed it.
- Small evaluation sets cannot detect small regressions. The gate says so, rather than pretending otherwise; growing the set is the fix.

## Alternatives considered

- **Delta against a tolerance.** Fails on noise; teams learn to ignore it.
- **No gate, human spot checks.** Regressions are found in production.

## Evidence

<!-- evidence:start -->
- **p = 0.39** for a 4.8-point judge drop the gate declined to fail. Exact McNemar on 83 paired cases — 8 worse, 4 better, 71 unchanged — qwen3:1.7b judged by qwen3:8b on Ollama, temperature 0. Source: [evalproof/MEASUREMENTS.md](https://github.com/technobasant/evalproof/blob/main/MEASUREMENTS.md)
- **1,469 → 4,422 ms** p95 latency, the regression that was real. System latency over the same 83 cases, sequential, one Apple M5; mean answer length went from 19 to 77 tokens. Source: [evalproof/MEASUREMENTS.md](https://github.com/technobasant/evalproof/blob/main/MEASUREMENTS.md)
<!-- evidence:end -->

## Related decisions in the labs

- evalproof [0003 Gate on a significant regression, not on a delta](https://github.com/technobasant/evalproof/blob/main/docs/adr/0003-gate-on-significance-not-delta.md)
