# ai-platform-architecture

The AI architecture for a fictional B2B SaaS company's usage assistant, stage 3 of the
engagement in [data-platform-architecture](https://github.com/technobasant/data-platform-architecture):
an assistant inside the product that answers customers' questions about their own usage from
the governed tables. Every recommendation is measured on a lab copy of the data, with local,
hosted and platform-native models.

[![ci](https://github.com/technobasant/ai-platform-architecture/actions/workflows/ci.yml/badge.svg)](https://github.com/technobasant/ai-platform-architecture/actions/workflows/ci.yml)

## Executive summary

**The ask.** Customers ask support how many reports they created, who used the mobile app,
which week was busiest. Product wants an assistant to answer, on every plan, within a year
([the brief](docs/01-brief.md)). The data is in usage marts that hold every customer's rows;
the customers are not users of the analytical platform.

**What was measured** ([3. Options](docs/03-options.md), [lab/](lab)): 90 customer questions
with answers computed by SQL, and 20 requests for other accounts' data, on a seeded copy of the
mart, put to Qwen3 8B run locally, Llama 3.3 70B and gpt-oss-120b on Databricks model serving,
and Databricks AI/BI Genie.

- **The semantic layer mattered more than the model.** Given the business's definitions as
  well as the schema, Llama 3.3 70B went from **55 to 70 of 70** correct and Qwen3 8B from 46
  to 64. gpt-oss-120b answered 70 of 70 and declined all 20 unanswerable questions. Results
  cluster by template (24 templates, not 70 independent questions), and the semantic layer
  was written with those templates in view, so these gains are an upper bound for questions
  like them.
- **A prompt is not isolation.** Told to answer only about the customer's account, the models
  leaked another account's data on **23 of 120** requests; every query Llama 3.3 70B wrote for
  them did. Run as the customer's own database identity, the same queries leaked **0**.
- **Genie was nearly as accurate, slower, and showed why.** With the same definitions it answered 69
  of 70, at 14.5 s median. Its one miss was a missing pair of parentheses that counted every
  account's Android users: 1,570 people instead of 12.
- **Cost is not the constraint.** At measured tokens, $0.00028 an answer on gpt-oss-120b: about
  $17 a month at launch volume. Self-hosting is price arithmetic only: an L4 or L40S GPU is
  far too small to hold a 120-billion-parameter model at all; on hardware that actually could
  (p5-48xlarge, 8×H100), break-even is about 194,600 answers an hour, against about 80 at
  launch.

**The recommendation.** The client's own small service on the platform's model serving:
gpt-oss-120b with Llama 3.3 70B as the fallback, the semantic layer in every prompt, one
read-only query per question scoped to the customer's account by the tool's own rewrite,
every response recorded, and a paired evaluation gate with hard fails on isolation, latency
and cost. Genie for internal staff, who are platform users. On the platform the tool runs as
one service identity that can read every account; because a row filter there cannot read a
per-request value, the tool scopes each query itself by rewriting it onto
per-account tables: on every recorded query it returned exactly what row-level security did
([0011](decisions/0011-identity-on-the-platform.md)).

## Contents

| | Document | What it answers |
|---|---|---|
| 1 | [Brief](docs/01-brief.md) | what the product wants, why it is hard, stakeholders, constraints |
| 2 | [Requirements](docs/02-requirements.md) | eleven quality targets as testable scenarios, with the lab's result for each |
| 3 | [Options, measured](docs/03-options.md) | accuracy, isolation, latency and cost for every way of building it |
| 4 | [Target architecture](docs/04-target-architecture.md) | the request path, carrying the customer's identity, observability, failure modes |
| 5 | [Evaluation](docs/05-evaluation.md) | the evaluation set, scoring, the gate, after release |
| 6 | [Security and compliance](docs/06-security-and-compliance.md) | OWASP Top 10 for LLM applications, data protection, EU AI Act, GDPR, NIST AI RMF |
| 7 | [Operations](docs/07-operations.md) | what is watched; runbooks for a leak, a wrong answer, a model change, an outage |
| | [Decisions](decisions) | 14 decision records with options, drivers and evidence |
| | [Risks](docs/risks.md), [principles](docs/principles.md) | the register; the rules across decisions |
| | [lab/](lab) | the mart, the questions, the attacks, the runners, and how to reproduce every number |

## Decisions

<!-- decisions:start -->
| # | Decision | Status | Backed by |
|---|---|---|---|
| 0001 | [The assistant answers by querying the governed usage tables, not from documents](decisions/0001-answers-from-governed-tables.md) | Accepted | 55 → 70 of 70 customers' questions answered correctly by Llama 3.3 70B, from the table definitions alone and with the semantic layer; 20 of 20 questions the data cannot answer that gpt-oss-120b declined, with the semantic layer |
| 0002 | [Each query is scoped to the customer's account by a mechanism the model cannot influence; the prompt is not a control](decisions/0002-isolation-in-the-database.md) | Accepted | 23 of 120 requests for another account's data that leaked when isolation was left to the prompt; 0 of 28 queries that reached the database (of the 120 requests; the rest were declined) and returned another account's data, run as the customer's own database role |
| 0003 | [A semantic layer of the business's definitions goes into every prompt](decisions/0003-semantic-layer.md) | Accepted | 55 → 70 of 70 customers' questions answered correctly by Llama 3.3 70B, from the table definitions alone and with the semantic layer; 46 → 64 of 70 the same questions answered correctly by Qwen3 8B, run locally, without and with the semantic layer |
| 0004 | [Customers get the client's own assistant service; staff can use the platform's assistant](decisions/0004-own-service-genie-for-staff.md) | Accepted | 69 of 70 questions Databricks AI/BI Genie answered correctly with the same definitions as instructions; median 14.5 s; 1,570 vs 12 people Genie counted for one customer's mobile users, against the right answer: a missing pair of parentheses counted every account's Android users |
| 0005 | [gpt-oss-120b on the platform's model serving, with Llama 3.3 70B as the fallback](decisions/0005-model-choice.md) | Accepted | 20 of 20 questions the data cannot answer that gpt-oss-120b declined, with the semantic layer; $0.00028 per answer on gpt-oss-120b at Databricks' pay-per-token list price, from measured tokens; p95 5.5 s |
| 0006 | [Every model response is recorded with its prompt's hash, and can be re-scored without the model](decisions/0006-record-every-response.md) | Accepted | 660 recorded model responses re-scored in CI against a fresh mart, with no model called; 54 of 54 cases where replaying the recorded model reproduced the live run's output |
| 0007 | [A model that judges answers is an instrument: calibrated against labels before its scores count](decisions/0007-judges-are-instruments.md) | Accepted | 7 vs 4 judge–key disagreements where the key, not the judge, was wrong; 5.9% → 0.0% false-positive rate of the judge on the baseline run, thinking off against thinking on |
| 0008 | [Prompt, model and definition changes ship through a paired evaluation gate](decisions/0008-release-gate.md) | Accepted | p = 0.39 for a 4.8-point judge drop the gate declined to fail; 1,469 → 4,422 ms p95 latency, the regression that was real |
| 0009 | ["The data does not have this" is a supported answer, and it is measured on its own](decisions/0009-abstention-is-an-answer.md) | Accepted | 20 of 20 questions the data cannot answer that gpt-oss-120b declined, with the semantic layer |
| 0010 | [Every model call goes through one gateway: budgeted, recorded, with a fallback](decisions/0010-one-gateway.md) | Accepted | 20 of 20 cases with identical outputs, verdicts and judge reasons when re-run with the cache off; 54 of 54 cases where replaying the recorded model reproduced the live run's output |
| 0011 | [On the platform, the assistant's tool scopes each query by rewriting it onto per-account tables](decisions/0011-identity-on-the-platform.md) | Accepted | 28 of 28 queries the models wrote for the isolation attacks that the tool's rewrite scoped to the customer's rows, exactly as row-level security did, including the 23 that leaked through the prompt; 436 of 436 queries for ordinary questions whose result the rewrite left exactly as row-level security gave it, none refused |
| 0012 | [One read-only statement, with a row limit and a timeout, or nothing](decisions/0012-sql-guard.md) | Accepted | 0 of 28 queries that reached the database (of the 120 requests; the rest were declined) and returned another account's data, run as the customer's own database role |
| 0013 | [Questions and answers are kept 30 days, never used for training, and erased on request](decisions/0013-conversation-retention.md) | Proposed | modelled, not yet measured |
| 0014 | [The assistant has a cost per answer, from measured tokens, and a monthly ceiling](decisions/0014-cost-per-answer.md) | Accepted | $0.00028 per answer on gpt-oss-120b at Databricks' pay-per-token list price, from measured tokens; p95 5.5 s |
<!-- decisions:end -->

Every figure, with its method and source file, is in [EVIDENCE.md](EVIDENCE.md).

## What is measured and what is not

| | Status |
|---|---|
| Accuracy, abstention, isolation, latency and tokens | measured: 660 recorded responses from three models and 90 from Genie, re-scored in CI from the recordings against a freshly built mart |
| Cost per answer | measured tokens at list prices ([`cost/`](cost)); not an observed bill |
| The release gate, judge calibration, replay | measured in [evalproof](https://github.com/technobasant/evalproof) and [governed-agent](https://github.com/technobasant/governed-agent) |
| Scoping on the platform | measured: the tool's rewrite on 464 recorded queries and a 44-case escape corpus ([`lab/escapes.yml`](lab/escapes.yml), `lab/rewrite.py --check`); Databricks' row filters on its identity, and their limit, in [data-platform-architecture](https://github.com/technobasant/data-platform-architecture) |
| Conversation retention | designed, Proposed |
| Injection through text in the data, budgets under load | not tested ([gaps](docs/06-security-and-compliance.md#the-gaps-in-order)) |

The client is fictional and its data synthetic; the hosted models ran on Databricks Free
Edition's model serving, and the local model on a laptop. The first version of this
repository, a reference architecture for several AI features without a client, is in the
[v0.1.0 tag](https://github.com/technobasant/ai-platform-architecture/tree/v0.1.0).

## Licence

Apache-2.0. See [LICENSE](LICENSE).
