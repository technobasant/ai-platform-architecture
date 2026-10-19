# Decisions

The decisions for the usage assistant in [the brief](../docs/01-brief.md), one file each, in
the same template as the
[data architecture's](https://github.com/technobasant/data-platform-architecture/tree/main/decisions):
status, context, decision drivers, options scored against them, the decision, consequences,
when to revisit it, and evidence generated from
[`../evidence/evidence.yml`](../evidence/evidence.yml). `scripts/build.py --check` fails CI if
a record lacks a section, cites an unknown figure, or is Accepted without evidence.

<!-- decisions:start -->
| # | Decision | Status | Backed by |
|---|---|---|---|
| 0001 | [The assistant answers by querying the governed usage tables, not from documents](0001-answers-from-governed-tables.md) | Accepted | 55 → 70 of 70 customers' questions answered correctly by Llama 3.3 70B, from the table definitions alone and with the semantic layer; 20 of 20 questions the data cannot answer that gpt-oss-120b declined, with the semantic layer |
| 0002 | [Each query runs under an identity that can read only the customer's account; the prompt is not a control](0002-isolation-in-the-database.md) | Accepted | 23 of 120 requests for another account's data that leaked when isolation was left to the prompt; 0 of 120 the same requests that returned another account's data when the query ran as the customer's own database role |
| 0003 | [A semantic layer of the business's definitions goes into every prompt](0003-semantic-layer.md) | Accepted | 55 → 70 of 70 customers' questions answered correctly by Llama 3.3 70B, from the table definitions alone and with the semantic layer; 43 → 64 of 70 the same questions answered correctly by Qwen3 8B, run locally, without and with the semantic layer |
| 0004 | [Customers get the client's own assistant service; staff can use the platform's assistant](0004-own-service-genie-for-staff.md) | Accepted | 69 of 70 questions Databricks AI/BI Genie answered correctly with the same definitions as instructions; median 14.5 s; 1,570 vs 12 people Genie counted for one customer's mobile users, against the right answer: a missing pair of parentheses counted every account's Android users |
| 0005 | [gpt-oss-120b on the platform's model serving, with Llama 3.3 70B as the fallback](0005-model-choice.md) | Accepted | 20 of 20 questions the data cannot answer that gpt-oss-120b declined, with the semantic layer; $0.00028 per answer on gpt-oss-120b at Databricks' pay-per-token list price, from measured tokens; p95 5.5 s |
| 0006 | [Every model response is recorded with its prompt's hash, and can be re-scored without the model](0006-record-every-response.md) | Accepted | 660 recorded model responses re-scored in CI against a fresh mart, with no model called; 54 of 54 cases where replaying the recorded model reproduced the live run's output |
| 0007 | [A model that judges answers is an instrument: calibrated against labels before its scores count](0007-judges-are-instruments.md) | Accepted | 7 vs 4 judge–key disagreements where the key, not the judge, was wrong; 5.9% → 0.0% false-positive rate of the judge on the baseline run, thinking off against thinking on |
| 0008 | [Prompt, model and definition changes ship through a paired evaluation gate](0008-release-gate.md) | Accepted | p = 0.39 for a 4.8-point judge drop the gate declined to fail; 1,469 → 4,422 ms p95 latency, the regression that was real |
| 0009 | ["The data does not have this" is a supported answer, and it is measured on its own](0009-abstention-is-an-answer.md) | Accepted | 20 of 20 questions the data cannot answer that gpt-oss-120b declined, with the semantic layer |
| 0010 | [Every model call goes through one gateway: budgeted, recorded, with a fallback](0010-one-gateway.md) | Accepted | 20 of 20 cases with identical outputs, verdicts and judge reasons when re-run with the cache off; 54 of 54 cases where replaying the recorded model reproduced the live run's output |
| 0011 | [On the chosen platform, the account scope is a policy on a value the query cannot change](0011-identity-on-the-platform.md) | Proposed | modelled, not yet measured |
| 0012 | [One read-only statement, with a row limit and a timeout, or nothing](0012-sql-guard.md) | Accepted | 0 of 120 the same requests that returned another account's data when the query ran as the customer's own database role |
| 0013 | [Questions and answers are kept 30 days, never used for training, and erased on request](0013-conversation-retention.md) | Proposed | modelled, not yet measured |
| 0014 | [The assistant has a cost per answer, from measured tokens, and a monthly ceiling](0014-cost-per-answer.md) | Accepted | $0.00028 per answer on gpt-oss-120b at Databricks' pay-per-token list price, from measured tokens; p95 5.5 s |
<!-- decisions:end -->

The records of this repository's first version, a reference architecture for several AI
features without a client, are in the
[v0.1.0 tag](https://github.com/technobasant/ai-platform-architecture/tree/v0.1.0/decisions).
