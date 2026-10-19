# 0003. A semantic layer of the business's definitions goes into every prompt

- Status: Accepted
- Date: 2026-10-19
- Deciders: data lead, VP Product; proposed by the architect
- Evidence: aia_semantic_llama, aia_semantic_qwen

## Context

The table definitions say what the columns are, not what customers mean. "How many people
used the product" is distinct users, not a sum of daily counts; "last week" starts on Monday;
"average daily active users" counts days with no activity. A model given only the schema
guesses, and some guesses are plausible and wrong.

## Decision drivers

- A1: accuracy; A2: declining what the data cannot answer.
- A9: the same definitions as the dashboards.
- Cost: every token of definition is paid on every question.

## Options

| | Llama 3.3 70B correct | Qwen3 8B correct | gpt-oss-120b correct | Prompt size |
|---|---:|---:|---:|---|
| Table definitions only | 55 of 70 | 46 of 70 | 65 of 70 | about 340 tokens |
| **Table definitions and the semantic layer** (periods, vocabulary, metric SQL, rules, three examples) | **70 of 70** | **64 of 70** | **70 of 70** | about 1,100 tokens |
| Fine-tuning a model on the client's questions | not measured | | | the smallest prompt, a model to maintain |

## Decision

One semantic layer, [`lab/semantic.yml`](../lab/semantic.yml), maintained by the data team
next to the dashboards' definitions, goes into every prompt and into any platform assistant
used internally ([0004](0004-own-service-genie-for-staff.md)). A wrong answer is fixed by a
definition and a new evaluation question, not by a prompt tweak.

## Consequences

- Prompts are three times longer: at the measured token counts this is a fraction of a cent
  per answer ([0014](0014-cost-per-answer.md)).
- The semantic layer is a product with an owner: a definition missing from it shows up as a
  wrong answer or a rise in declines.
- One of the three examples teaches a metric (average daily active users) the evaluation set
  also asks about, for another month; the gain is not only from that question.
- The semantic layer was written with the evaluation's 24 question templates in view: its
  periods and metric SQL map onto them directly, and each template is asked for up to three
  accounts, not 70 independent questions. The gains above are an upper bound for questions
  shaped like these, not a general accuracy figure; a held-out set of templates written after
  `semantic.yml` was frozen is future work.

## Revisit when

The semantic layer passes about 5,000 tokens, or the questions outgrow one mart: then
definitions are retrieved per question rather than sent whole.

## Evidence

<!-- evidence:start -->
- **55 → 70 of 70** customers' questions answered correctly by Llama 3.3 70B, from the table definitions alone and with the semantic layer. 70 answerable questions (24 templates, each asked for different accounts) with reference answers computed by SQL on a seeded usage mart; the model writes one PostgreSQL query, run as the customer's own role, with the prompt's today (2026-10-01) pinned for CURRENT_DATE and now(); the reference value must be in the first row, numbers to one decimal. Source: [ai-platform-architecture/results/assistant.json](https://github.com/technobasant/ai-platform-architecture/blob/main/results/assistant.json)
- **46 → 64 of 70** the same questions answered correctly by Qwen3 8B, run locally, without and with the semantic layer. As above; Ollama on a laptop, temperature 0, thinking off. Source: [ai-platform-architecture/results/assistant.json](https://github.com/technobasant/ai-platform-architecture/blob/main/results/assistant.json)
<!-- evidence:end -->
