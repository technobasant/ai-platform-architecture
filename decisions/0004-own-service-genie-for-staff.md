# 0004. Customers get the client's own assistant service; staff can use the platform's assistant

- Status: Accepted
- Date: 2026-10-19
- Deciders: CTO, VP Product, data lead; proposed by the architect
- Evidence: aia_genie_accuracy, aia_genie_precedence, aia_semantic_llama

## Context

Databricks AI/BI Genie (and Snowflake Cortex Analyst) answer questions over governed tables
with no service to build. The lab gave Genie the same tables, the semantic layer as
instructions and the same three examples, and asked the same questions.

## Decision drivers

- A1, A2: accuracy and declining.
- A3: isolation for customers, who are not platform users.
- A5: an answer within 10 s, 95 times in 100.
- The team's effort.

## Options

| | Correct | Declined, unanswerable | Median time | Customer identity |
|---|---:|---:|---:|---|
| Genie, with the semantic layer as instructions | 69 of 70 | 19 of 20 | 14.5 s (includes up to 3 s of polling) | workspace users and groups; customers would need an identity per account or a shared one |
| **The client's service: gpt-oss-120b on platform model serving, with the semantic layer** | 70 of 70 | 20 of 20 | 2.9 s (p95 5.5 s) | set by the service from the product's session ([0002](0002-isolation-in-the-database.md)) |
| The same service with Llama 3.3 70B | 70 of 70 | 19 of 20 | 2.1 s (p95 2.9 s) | as above |

## Decision

Customers use the client's own assistant service on the platform's model serving. Internal
staff (analysts, customer success) may use the platform's assistant over the same marts and
semantic layer, because they are platform users and its row filters apply to them.

## Consequences

- One more service to build and run, small: a prompt, a guard, a query tool, a gateway.
- Genie stays useful where its identity model fits; with the same definitions it was within
  one answer of the best models (69 of 70 against 70). It had no run without them, so it
  does not show that the definitions caused that; the three models' before and after does.
- Genie's one wrong answer counted every account's Android users because of a missing pair
  of parentheses: in the lab it ran with access to every account. For staff that is a wrong
  number; for a customer it would have been another customer's data.

## Revisit when

The platform's assistant can carry an external customer's identity to row filters and
answers within the latency target, with an evaluation API the gate can call.

## Evidence

<!-- evidence:start -->
- **69 of 70** questions Databricks AI/BI Genie answered correctly with the same definitions as instructions; median 14.5 s. The mart's tables copied to Unity Catalog; a Genie space whose instructions and examples are the semantic layer; each question asked as 'I am account N.' through the Conversation API, polled every 3 s until it completes, and its query result scored with the same checker; each timing includes up to 3 s of polling. Source: [ai-platform-architecture/results/assistant-genie.json](https://github.com/technobasant/ai-platform-architecture/blob/main/results/assistant-genie.json)
- **1,570 vs 12** people Genie counted for one customer's mobile users, against the right answer: a missing pair of parentheses counted every account's Android users. WHERE account_id = 132 AND platform ILIKE '%ios%' OR platform ILIKE '%android%' AND …, run with access to every account, as the lab's Genie space was. Source: [ai-platform-architecture/results/assistant-genie-responses.jsonl](https://github.com/technobasant/ai-platform-architecture/blob/main/results/assistant-genie-responses.jsonl)
- **55 → 70 of 70** customers' questions answered correctly by Llama 3.3 70B, from the table definitions alone and with the semantic layer. 70 answerable questions (24 templates, each asked for different accounts) with reference answers computed by SQL on a seeded usage mart; the model writes one PostgreSQL query, run as the customer's own role, with the prompt's today (2026-10-01) pinned for CURRENT_DATE and now(); the reference value must be in the first row, numbers to one decimal. Source: [ai-platform-architecture/results/assistant.json](https://github.com/technobasant/ai-platform-architecture/blob/main/results/assistant.json)
<!-- evidence:end -->
