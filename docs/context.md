# Context

## The features

| Feature | Who uses it | What it does | Where it is built and measured |
|---|---|---|---|
| Analyst | finance and product people; later, customers about their own account | answers questions over governed data by planning, calling typed tools and composing an answer with its sources | [governed-agent](https://github.com/technobasant/governed-agent) |
| Help-centre assistant | customers | answers from retrieved help-centre passages, or says the help centre does not cover it | [evalproof](https://github.com/technobasant/evalproof) (its support-QA suite), [retrieval-bench](https://github.com/technobasant/retrieval-bench) |
| Triage | support and product teams | groups short free text (ticket tags, cancellation reasons) into named intents, and flags new ones | [short-text-triage](https://github.com/technobasant/short-text-triage) |
| Scoring models | the product, in the request path | fraud and churn scores from point-in-time features | [realtime-ml](https://github.com/technobasant/realtime-ml) |
| Category trends | product and leadership dashboards | shares of tickets or sessions by category, over time | [prevalence-shift](https://github.com/technobasant/prevalence-shift) |

## Constraints

- **Tenant isolation.** A customer-facing feature never sees another customer's data, whatever the question says.
- **Personal data.** Names, e-mail addresses and free text that may contain them are redacted before a request leaves for a hosted model, unless the feature is approved to send them.
- **Reviewable.** Anything that becomes state (a published answer, a sent message, a changed record) can be traced to the inputs, tools and checks that produced it.
- **Cost known in advance.** Each feature has a cost per answer and a monthly budget before it ships.
- **A small team.** The same three to five engineers who run the data platform run this; operating cost in people counts.

## Volumes

The cost model prices the analyst and the help-centre assistant at three tiers:

| | Small | Medium | Large |
|---|---:|---:|---:|
| Analyst answers per month | 2,000 | 20,000 | 200,000 |
| Help-centre answers per month | 10,000 | 100,000 | 1,000,000 |

These are assumptions, set in [`cost/workloads.yml`](../cost/workloads.yml).

## Out of scope

Training or fine-tuning foundation models; voice and image features; autonomous agents that act without review.
