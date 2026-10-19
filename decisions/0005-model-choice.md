# 0005. gpt-oss-120b on the platform's model serving, with Llama 3.3 70B as the fallback

- Status: Accepted
- Date: 2026-10-19
- Deciders: data lead, CFO; proposed by the architect
- Evidence: aia_unanswerable, aia_cost_per_answer, aia_semantic_qwen

## Context

With the semantic layer, two hosted open-weight models answered every answerable question.
They differ in declining, latency and price. A small local model is cheaper to run per
token, and slower and less accurate.

## Decision drivers

- A1, A2; A5: within 10 s, 95 times in 100; A6: under $0.01 per answer.
- Data protection: processing in the client's EU region, under the platform's agreement.
- A second model for when the first is unavailable.

## Options

| With the semantic layer | Correct | Declined, unanswerable | p50 / p95 | Per answer, list price |
|---|---:|---:|---|---:|
| **gpt-oss-120b, platform model serving** | 70 of 70 | 20 of 20 | 2.9 s / 5.5 s | $0.00028 |
| Llama 3.3 70B, platform model serving | 70 of 70 | 19 of 20 | 2.1 s / 2.9 s | $0.00060 |
| Qwen3 8B, self-hosted | 64 of 70 | 18 of 20 | 9.1 s / 11.6 s on a laptop | the GPU's hours |
| A frontier API | not measured | | | $0.002–0.021 at the same tokens ([cost](../cost)) |

## Decision

gpt-oss-120b on the platform's pay-per-token model serving is the primary model; Llama 3.3
70B is the gateway's fallback. Both stay in the client's region. The two are equally accurate
with the semantic layer (70 of 70); the choice between them rests on cost per answer and on
the one-question difference in declines (20 of 20 against 19 of 20), which on its own cannot
rank them. Self-hosting is not worth it at this volume, and the arithmetic does not favour it
at any realistic volume either: an L4 or L40S GPU cannot hold a 120-billion-parameter model
at all, so a single GPU instance is not a hosting option for gpt-oss-120b; on hardware that
could (p5-48xlarge, 8×H100), break-even is about 194,600 answers an hour.

## Consequences

- At launch volume (60,000 answers a month) the model bill is about $17 a month at list price.
- gpt-oss-120b is a reasoning model: its output tokens include reasoning, and its latency
  varies more than Llama's.
- The decline difference (20 of 20 vs 19 of 20) is one data point among several, not by
  itself a reason to prefer one model: on a single held-out question each, it is within
  noise; cost and latency carry more of the decision.
- A model change goes through the gate and re-runs the isolation suite
  ([0008](0008-release-gate.md)).

## Revisit when

Either model leaves the platform's serving, a release fails the gate, or volume passes a few
thousand answers an hour.

## Evidence

<!-- evidence:start -->
- **20 of 20** questions the data cannot answer that gpt-oss-120b declined, with the semantic layer. 10 questions about billing, sessions, personal data, tickets and predictions, each asked for two accounts; a declined answer is UNANSWERABLE with no query. Source: [ai-platform-architecture/results/assistant.json](https://github.com/technobasant/ai-platform-architecture/blob/main/results/assistant.json)
- **$0.00028** per answer on gpt-oss-120b at Databricks' pay-per-token list price, from measured tokens; p95 5.5 s. Mean 1,094 input and 198 output tokens (reasoning included) over the 90 questions with the semantic layer; $0.15 and $0.60 per million tokens (2.143 and 8.571 DBU at $0.07). Source: [ai-platform-architecture/results/assistant.json](https://github.com/technobasant/ai-platform-architecture/blob/main/results/assistant.json)
- **46 → 64 of 70** the same questions answered correctly by Qwen3 8B, run locally, without and with the semantic layer. As above; Ollama on a laptop, temperature 0, thinking off. Source: [ai-platform-architecture/results/assistant.json](https://github.com/technobasant/ai-platform-architecture/blob/main/results/assistant.json)
<!-- evidence:end -->
