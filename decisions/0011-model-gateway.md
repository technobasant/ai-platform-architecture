# 0011. Every model call goes through one gateway: local-first, recorded for replay, and budgeted per feature

- Status: Accepted
- Date: 2026-10-18
- Evidence: evalproof_determinism, agent_replay

## Context

Features call models from several providers and sizes. Without one path, there is no single place to cache, to record calls for tests, to cap spend, to fail over, or to keep personal data from leaving.

## Decision

- All model calls go through a gateway that owns provider credentials, retries with jitter, timeouts and fallbacks.
- The default for development and CI is a local model; hosted providers are configuration.
- Calls are cached by content and can be recorded and replayed, so tests and the evaluation gate ([0004](0004-release-gate-on-paired-evaluation.md)) run without a model.
- Each feature has a token and cost budget enforced at the gateway, and personal data is redacted before a request leaves for a hosted provider unless the feature is approved to send it.

## Consequences

- With the cache off, 20 of 20 re-run cases gave identical outputs, verdicts and judge reasons at temperature 0 and a fixed seed on a local model.
- Replaying recorded responses reproduced the live run on 54 of 54 cases, so CI checks behaviour without calling a model.
- One more service on the critical path, which needs the same availability as the features it serves.

## Alternatives considered

- **Each feature calls its provider directly.** Fastest; no shared budget, cache, replay or redaction.

## Evidence

<!-- evidence:start -->
- **20 of 20** cases with identical outputs, verdicts and judge reasons when re-run with the cache off. Temperature 0 and seed 0 on local models through Ollama 0.23.2; checked on this backend only. Source: [evalproof/MEASUREMENTS.md](https://github.com/technobasant/evalproof/blob/main/MEASUREMENTS.md)
- **54 of 54** cases where replaying the recorded model reproduced the live run's output. The live run's model responses recorded once and replayed in CI, so tests and the eval gate run with no model. Source: [governed-agent/MEASUREMENTS.md](https://github.com/technobasant/governed-agent/blob/main/MEASUREMENTS.md)
<!-- evidence:end -->

## Related decisions in the labs

- governed-agent [0006 CI replays a recorded model instead of calling one](https://github.com/technobasant/governed-agent/blob/main/docs/adr/0006-replayed-model-in-ci.md)
- evalproof [0002 Local-first providers over plain HTTP](https://github.com/technobasant/evalproof/blob/main/docs/adr/0002-local-first-providers.md)
