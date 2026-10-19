# 0002. Each query runs under an identity that can read only the customer's account; the prompt is not a control

- Status: Accepted
- Date: 2026-10-19
- Deciders: CTO, security and compliance lead; proposed by the architect
- Evidence: aia_prompt_isolation, aia_db_isolation, aia_genie_precedence

## Context

The marts hold every customer's usage. The assistant's model writes the query. If what keeps
a customer to their own rows is the model's `WHERE` clause, isolation is as good as the
model's obedience and its SQL. The lab tested both, with 20 prompts that only another
account's data, or every account's, could answer.

## Decision drivers

- A3: never another account's rows or totals, whatever the question says.
- A4: nothing but reads.
- Customers are not users of the analytical platform ([1. Brief](../docs/01-brief.md#constraints)).

## Options

| | Leaked in the lab | Depends on the model | Survives a model change |
|---|---|---|---|
| Tell the model the account, and to answer only about it | 23 of 120 requests (12 of the 12 queries Llama 3.3 70B wrote) | yes | no |
| Check the generated SQL for an `account_id` filter | not measured | partly: a filter can be wrong, as Genie's was | partly |
| **Run the query as an identity that sees only the account** (a role per account and row-level security in the lab; a platform policy in production, [0011](0011-identity-on-the-platform.md)) | 0 of 120 | no | yes |

## Decision

The query tool runs every generated query under an identity that can read only the
customer's account, set from the product's authenticated session and never from the
question. The prompt still names the account, because it makes answers better, not because
it protects anything.

## Consequences

- A model that writes a query for another account, or for all of them, returns only the
  customer's own rows. In the lab, the most accurate model (Llama 3.3 70B, 70 of 70) was also
  the one that leaked most when left to the prompt; Genie leaked on an ordinary question
  through a missing pair of parentheses.
- The isolation suite runs in CI against the identity, not the prompt, and blocks deploys.
- The production form of the identity depends on the platform
  ([0011](0011-identity-on-the-platform.md)).

## Revisit when

Never as a principle. The mechanism is revisited with the platform choice.

## Evidence

<!-- evidence:start -->
- **23 of 120** requests for another account's data that leaked when isolation was left to the prompt. 20 prompts asking for another account's or every account's data, each from two customers, to three models told to answer only about the customer's account; the generated query run with access to every account and as the customer's role, a leak being any difference. Llama 3.3 70B leaked with 12 of the 12 queries it wrote. Source: [ai-platform-architecture/results/assistant.json](https://github.com/technobasant/ai-platform-architecture/blob/main/results/assistant.json)
- **0 of 120** the same requests that returned another account's data when the query ran as the customer's own database role. One read-only login role per account, row-level security on every table keyed on the session's login role; each role sees 1 of the 200 accounts. Source: [ai-platform-architecture/results/assistant.json](https://github.com/technobasant/ai-platform-architecture/blob/main/results/assistant.json)
- **1,570 vs 12** people Genie counted for one customer's mobile users, against the right answer: a missing pair of parentheses counted every account's Android users. WHERE account_id = 132 AND platform ILIKE '%ios%' OR platform ILIKE '%android%' AND …, run with access to every account, as the lab's Genie space was. Source: [ai-platform-architecture/results/assistant-genie-responses.jsonl](https://github.com/technobasant/ai-platform-architecture/blob/main/results/assistant-genie-responses.jsonl)
<!-- evidence:end -->
