# 0001. The assistant answers by querying the governed usage tables, not from documents

- Status: Accepted
- Date: 2026-10-19
- Deciders: VP Product, CTO, data lead; proposed by the architect
- Evidence: aia_semantic_llama, aia_unanswerable

## Context

Customers ask for numbers about their own usage: counts, people, days, features. The numbers
live in the usage marts the data platform publishes, at user and day grain, for every
account. An assistant can produce them by writing a query, by retrieving pre-written text, or
by being handed a summary of the account's data in its prompt.

## Decision drivers

- A1: the right number, 9 times in 10; A2: "the data does not have this" when it does not.
- A3: never another account's data.
- A9: the same definition as the dashboards.
- A6: cost per answer.

## Options

| | Exact numbers | Any period or breakdown | Scoped by the data's identity | Cost |
|---|---|---|---|---|
| Retrieval over documents or pre-written summaries (RAG) | ✘ only what was written | ✘ | ◐ by filter on the index | ◐ |
| The account's data summarised into the prompt | ◐ what fits | ✘ | ◐ | ✘ grows with the account |
| Fixed question templates, no model | ✔ | ✘ only the templates | ✔ | ✔ |
| **A model writes one SQL query over the marts; the rows answer** | ✔ | ✔ | ✔ scoped to the customer by a mechanism it cannot influence ([0002](0002-isolation-in-the-database.md)) | ✔ one call |

## Decision

The assistant answers by having a model write one SQL query against the usage marts, scoped
to the customer's account by a mechanism the model cannot influence — a database role and
row-level security in the lab, one service identity and the tool's rewrite on the platform
([0002](0002-isolation-in-the-database.md), [0011](0011-identity-on-the-platform.md)) — and
composing the answer from the rows, with the definition and period shown. The model never
sees other accounts' rows; it does not see the result either, in this design.

## Consequences

- Answers are as exact as the marts, and as wrong as the query: accuracy is the model's and
  the semantic layer's ([0003](0003-semantic-layer.md)), measured by an evaluation set with
  SQL reference answers.
- Questions the marts cannot answer must be recognised and declined
  ([0009](0009-abstention-is-an-answer.md)).
- Fixed templates remain the fallback for the five or six questions asked most, if a model
  is ever unavailable.

## Revisit when

Customers mostly ask "how do I" rather than "how many", which is a help-centre assistant over
documents, and a different decision.

## Evidence

<!-- evidence:start -->
- **55 → 70 of 70** customers' questions answered correctly by Llama 3.3 70B, from the table definitions alone and with the semantic layer. 70 answerable questions (24 templates, each asked for different accounts) with reference answers computed by SQL on a reproducible generated usage mart; the model writes one PostgreSQL query, run as the customer's own role, with the prompt's today (2026-10-01) pinned for CURRENT_DATE and now(); the reference value must be in the first row, numbers to one decimal. Source: [ai-platform-architecture/results/assistant.json](https://github.com/technobasant/ai-platform-architecture/blob/main/results/assistant.json)
- **20 of 20** questions the data cannot answer that gpt-oss-120b declined, with the semantic layer. 10 questions about billing, sessions, personal data, tickets and predictions, each asked for two accounts; a declined answer is UNANSWERABLE with no query. Source: [ai-platform-architecture/results/assistant.json](https://github.com/technobasant/ai-platform-architecture/blob/main/results/assistant.json)
<!-- evidence:end -->
