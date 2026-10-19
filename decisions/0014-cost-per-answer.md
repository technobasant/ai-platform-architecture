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

- At the measured 1,094 input and 198 output tokens, gpt-oss-120b costs $0.00028 an answer at
  list price: about $17 a month at launch volume and $170 at 36 months, far inside the budget.
- The SQL warehouse time the queries use is part of the platform's bill, not this one.

## Revisit when

The measured cost per answer moves by more than half after a model or prompt change.

## Evidence

<!-- evidence:start -->
- **$0.00028** per answer on gpt-oss-120b at Databricks' pay-per-token list price, from measured tokens; p95 5.5 s. Mean 1,094 input and 198 output tokens (reasoning included) over the 90 questions with the semantic layer; $0.15 and $0.60 per million tokens (2.143 and 8.571 DBU at $0.07). Source: [ai-platform-architecture/results/assistant.json](https://github.com/technobasant/ai-platform-architecture/blob/main/results/assistant.json)
<!-- evidence:end -->
