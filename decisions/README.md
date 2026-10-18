# Decisions

Decisions for AI features on the platform, one file each: context, decision, consequences, alternatives, and the measured evidence (generated from [`../evidence/evidence.yml`](../evidence/evidence.yml) by `scripts/build.py`).

<!-- decisions:start -->
| # | Decision | Status | Backed by |
|---|---|---|---|
| 0001 | [AI features reach data only through typed tools behind one boundary](0001-one-governed-boundary-to-data.md) | Accepted | 0 of 5 planted instructions that led to a proposed action |
| 0002 | [A model's output becomes state only after a schema, a policy, a grounding check and, for side effects, a person](0002-outputs-become-state-after-checks.md) | Accepted | 48/54 answers matched an answer key computed by SQL; 3 of 37 answers published without review were wrong |
| 0003 | ["The data does not have this" is a supported answer, and it is measured separately](0003-abstention-is-an-answer.md) | Accepted | 4 of 8 unanswerable questions answered with “the data does not have this” |
| 0004 | [Prompt and model changes ship through a paired evaluation gate, with latency and cost gated separately](0004-release-gate-on-paired-evaluation.md) | Accepted | p = 0.39 for a 4.8-point judge drop the gate declined to fail; 1,469 → 4,422 ms p95 latency, the regression that was real |
| 0005 | [An LLM judge is an instrument: calibrated against labels, audited with them, and never trusted pairwise](0005-judges-are-instruments.md) | Accepted | 7 vs 4 judge–key disagreements where the key, not the judge, was wrong; 5.9% → 0.0% false-positive rate of the judge on the baseline run, thinking off against thinking on |
| 0006 | [The vector store is chosen by recall under the product's filters, not by unfiltered benchmarks](0006-retrieval-by-filtered-recall.md) | Accepted | ≤ 0.0015 nDCG@10 between pgvector, Qdrant and OpenSearch and exact search; 3.9 of 10 rows returned by post-filtered HNSW at 10% selectivity |
| 0007 | [Label the distinct string, not the row: cluster before calling a model, and assign by margin](0007-label-strings-not-rows.md) | Accepted | 125 vs 20,000 LLM labelling calls on day 1, one per cluster against one per row; 95.2% vs 66.2% precision assigning new rows to known intents: a margin rule against the best absolute similarity threshold |
| 0008 | [Counts from a classifier are corrected for its error rates, and a model upgrade may not move a trend](0008-correct-counted-labels.md) | Accepted | 0.628 of the true trend recovered by counting a 95%-accurate classifier's labels; 0.0% of 12,000 period estimates where the naive 95% interval of counted labels covered the true prevalence |
| 0009 | [Model features are point-in-time correct, from one definition online and offline](0009-point-in-time-features.md) | Accepted | 0.363 vs 0.941 future AUC-PR, naive join against point-in-time join; 99.905% of 9,500 live requests served exactly the training features |
| 0010 | [Models are promoted on a paired improvement within a latency budget, and watched on outcomes, not only on input drift](0010-promote-on-outcomes.md) | Accepted | 82.5% of fraud cost saved on two unseen weeks; 0 of 5 tactics drifts caught by feature PSI |
| 0011 | [Every model call goes through one gateway: local-first, recorded for replay, and budgeted per feature](0011-model-gateway.md) | Accepted | 20 of 20 cases with identical outputs, verdicts and judge reasons when re-run with the cache off; 54 of 54 cases where replaying the recorded model reproduced the live run's output |
| 0012 | [AI services ship by canary like every other service, after the evaluation gate](0012-ai-services-ship-by-canary.md) | Accepted | 6 of 6 bad releases aborted by canary analysis; 0 of 18,003 requests failed across three good canary releases |
| 0013 | [Each AI feature has a cost per answer, from a model of tokens and prices, before it ships](0013-cost-budget-per-feature.md) | Proposed | modelled, not yet measured |
<!-- decisions:end -->

## Decisions inside the labs

| Repository | Decision records |
|---|---|
| [governed-agent](https://github.com/technobasant/governed-agent/tree/main/docs/adr) | 6: the explicit graph, MCP as the boundary, the grounding check, review before execute, the outbox, the replayed model in CI |
| [evalproof](https://github.com/technobasant/evalproof/tree/main/docs/adr) | 3: the judge as a classifier, local-first providers, gating on significance |
| [retrieval-bench](https://github.com/technobasant/retrieval-bench/tree/main/docs/adr) | 5: embed once, iso-recall comparison, latency measurement, datasets, Postgres full text |
| [realtime-ml](https://github.com/technobasant/realtime-ml/tree/main/docs/adr) | 7: Feast with DuckDB and Redis, two implementations per feature, window semantics, label maturity, the promotion gate, Kafka KRaft, drift monitoring |
| [platform-deployments](https://github.com/technobasant/platform-deployments/tree/main/docs/adr) | 8: GitOps and the canary that ships the agent's API |

The data platform these features run on has its own decisions in [data-platform-architecture](https://github.com/technobasant/data-platform-architecture/tree/main/decisions).
