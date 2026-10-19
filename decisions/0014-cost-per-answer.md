# 0014. The assistant has a cost per answer, from measured tokens, and a monthly ceiling

- Status: Accepted
- Date: 2026-10-19
- Deciders: CFO, VP Product; proposed by the architect
- Evidence: aia_cost_per_answer

## Context

The assistant is offered on every plan, including free. Its cost is tokens times price, per
question, and its volume is a guess until launch.

## Decision drivers

- A6: under $0.01 per answer on average; under $1,500 a month at launch.
- A price that holds when volume is ten times the guess.

## Options

| | Known before launch | Holds at ten times the volume |
|---|---|---|
| Estimate tokens, price later | ✘ | ✘ |
| **Measure tokens per answer in the evaluation, price them per model, and enforce a monthly ceiling at the gateway** | ✔ | ✔ with the ceiling |

## Decision

Cost per answer is computed from the evaluation's measured tokens for every candidate model
([`cost/`](../cost)), re-computed with every model or prompt change, and enforced at the
gateway as a monthly ceiling with per-account rate limits ([0010](0010-one-gateway.md)).

## Consequences

- At the measured 1,094 input and 198 output tokens, gpt-oss-120b costs $0.00032 an answer at
  list price in the client's EU region: about $19 a month at launch volume and $189 at 36
  months, far inside the budget.
- The model is not the large cost; the engine that runs its queries is. A SQL warehouse is
  billed for every minute it is awake, and customers ask at any hour. The smallest serverless
  warehouse, measured in the data architecture's proof of concept at 4 DBU an hour, costs
  $3.64 an hour in the client's region: $961 a month awake for EU working hours alone, and
  $2,657 awake all month, against the $1,500 ceiling, before a single token. So the
  assistant's queries do not get a warehouse of their own: they go where something is awake
  anyway, the stage-2 usage store
  ([data-platform-architecture 0010](https://github.com/technobasant/data-platform-architecture/blob/main/decisions/0010-customer-usage-serving.md)),
  which the usage page already reads. That store's SQL dialect is where 0011's launch gate
  runs the rewrite's escape corpus.

## Revisit when

The measured cost per answer moves by more than half after a model or prompt change; or
stage 2 is not built, and the assistant needs a query engine of its own.

## Evidence

<!-- evidence:start -->
- **$0.00032** per answer on gpt-oss-120b at Databricks' pay-per-token list price in the client's EU region, from measured tokens; p95 5.5 s. Mean 1,094 input and 198 output tokens (reasoning included) over the 90 questions with the semantic layer; 2.143 and 8.571 DBU per million tokens at $0.078 a DBU, AWS EU (Ireland), from the platform's system.billing.list_prices ($0.07 in US East). Source: [ai-platform-architecture/results/assistant.json](https://github.com/technobasant/ai-platform-architecture/blob/main/results/assistant.json)
<!-- evidence:end -->
