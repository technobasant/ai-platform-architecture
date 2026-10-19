# 0009. "The data does not have this" is a supported answer, and it is measured on its own

- Status: Accepted
- Date: 2026-10-19
- Deciders: VP Product, head of support; proposed by the architect
- Evidence: aia_unanswerable

## Context

Customers will ask what the marts cannot answer: what they paid, which user will cancel, how
long sessions last, what was in an export. An assistant that always produces a number will
produce one for these too.

## Decision drivers

- A2: decline, 19 times in 20, when the data cannot answer.
- A1: without declining what it can answer.

## Options

| | Wrong numbers on unanswerable questions | Declines what it should answer |
|---|---|---|
| Always answer | ✘ | ✔ never |
| Answer only from a whitelist of question types | ✔ | ✘ often |
| **A typed "UNANSWERABLE" reply the model is told to use, scored separately from accuracy** | ✔ measured | ✔ measured |

## Decision

The prompt makes "UNANSWERABLE" the reply when the tables cannot answer; the product shows it
as "the data does not have this" with a route to support. The evaluation set carries
unanswerable questions and scores declines separately from accuracy, so a model that
declines everything fails A1 and a model that answers everything fails A2.

## Consequences

- With the semantic layer, gpt-oss-120b declined 20 of 20 and wrongly declined none of the 70
  answerable questions. Genie, with the same definitions, invented a "projected" zero for
  next month's reports.
- Boundary questions (answerable ones that sound unanswerable) are the next part of the set.

## Revisit when

Declines on answerable questions rise in production: a definition is missing.

## Evidence

<!-- evidence:start -->
- **20 of 20** questions the data cannot answer that gpt-oss-120b declined, with the semantic layer. 10 questions about billing, sessions, personal data, tickets and predictions, each asked for two accounts; a declined answer is UNANSWERABLE with no query. Source: [ai-platform-architecture/results/assistant.json](https://github.com/technobasant/ai-platform-architecture/blob/main/results/assistant.json)
<!-- evidence:end -->
