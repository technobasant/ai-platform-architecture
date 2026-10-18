# Choosing models, and what they cost

**Status.** Prices are list prices read from each vendor's pricing page; token counts per call are assumptions. No feature's bill has been observed ([0013](../decisions/0013-cost-budget-per-feature.md)).

## Choosing a model per feature

1. Start from the cheapest model that passes the feature's evaluation gate, not the strongest available one. The gate, not the model's reputation, says what is good enough.
2. Price the feature on that model and on the next one up; the difference is what the quality gain costs.
3. Route by step where it pays: a small model to classify or plan, a larger one only where the gate shows it is needed.
4. Recheck when a model or price changes; both do, often.

## What moves the cost

| Lever | Effect |
|---|---|
| Model | about 100× between the cheapest and most expensive model priced here, for the same answer |
| Calls per answer | an agent that plans, queries and composes pays three times for every answer |
| Context size | retrieved passages and tool schemas are most of the input tokens |
| Design | labelling once per cluster instead of once per row is about 13× cheaper on every model priced |
| Caching and batch | prompt caching cuts the price of repeated input sharply; batch APIs halve prices for work that can wait. Neither is in the model |

## The numbers

<!-- cost:start -->
List prices retrieved 2026-10-18 ([`cost/prices.yml`](../cost/prices.yml)); token counts assumed in [`cost/workloads.yml`](../cost/workloads.yml).

**Per answer, and per month at the medium tier**

| Model | Analyst answer | Support answer | Analyst, 20,000/month | Support, 100,000/month |
|---|---:|---:|---:|---:|
| claude-opus-5-5 | $0.0660 | $0.0190 | $1,320 | $1,900 |
| claude-sonnet-5 | $0.0330 | $0.0095 | $660 | $950 |
| claude-haiku-4-5 | $0.0165 | $0.0047 | $330 | $475 |
| gpt-6-astra | $0.1650 | $0.0475 | $3,300 | $4,750 |
| gpt-6-1-sol | $0.0330 | $0.0095 | $660 | $950 |
| gpt-6-luna | $0.0016 | $0.0005 | $33 | $48 |
| gemini-3-1-pro-preview | $0.0348 | $0.0100 | $696 | $1,000 |
| gemini-3-8-flash | $0.0124 | $0.0036 | $248 | $356 |
| gemini-3-5-flash-lite | $0.0059 | $0.0017 | $117 | $168 |

**Self-hosting break-even.** Requests per hour a dedicated instance must serve before it costs less than the API, for a support answer. Price arithmetic only.

| Model replaced | g6-xlarge ($0.8048/h) | g6e-xlarge ($1.861/h) | p5-48xlarge ($55.04/h) |
|---|---:|---:|---:|
| claude-opus-5-5 | 42 | 98 | 2,897 |
| claude-sonnet-5 | 85 | 196 | 5,794 |
| claude-haiku-4-5 | 169 | 392 | 11,587 |
| gpt-6-astra | 17 | 39 | 1,159 |
| gpt-6-1-sol | 85 | 196 | 5,794 |
| gpt-6-luna | 1,694 | 3,918 | 115,874 |
| gemini-3-1-pro-preview | 80 | 186 | 5,504 |
| gemini-3-8-flash | 226 | 522 | 15,450 |
| gemini-3-5-flash-lite | 480 | 1,111 | 32,860 |

**Triage, day 1** (measured call counts: 20,000 per row, 125 per cluster)

| Model | One call per row | One call per cluster |
|---|---:|---:|
| claude-opus-5-5 | $18.00 | $1.40 |
| claude-sonnet-5 | $9.00 | $0.70 |
| claude-haiku-4-5 | $4.50 | $0.35 |
| gpt-6-astra | $45.00 | $3.50 |
| gpt-6-1-sol | $9.00 | $0.70 |
| gpt-6-luna | $0.45 | $0.03 |
| gemini-3-1-pro-preview | $9.60 | $0.72 |
| gemini-3-8-flash | $3.38 | $0.26 |
| gemini-3-5-flash-lite | $1.65 | $0.11 |
<!-- cost:end -->

### Reading the numbers

- **Model choice is the largest lever.** An analyst answer costs from well under a cent to 16.5 cents depending on the model, before any design change.
- **Self-hosting rarely pays against small hosted models.** A single L40S instance costs the same as a few hundred help-centre answers an hour on mid-sized hosted models, but several thousand an hour on the cheapest. Whether one instance can serve that rate, with an open model that passes the gate, is the part to measure before buying.
- **Design beats model choice for repetitive text.** Triage per cluster costs a fraction of triage per row on every model, because it pays for distinct meanings, not rows.
- **Prices move.** Two of the Gemini prices here double on 1 December 2026 and 1 January 2027 (noted in [`cost/prices.yml`](../cost/prices.yml)).

### Not modelled

Prompt caching, batch discounts, long-context surcharges, data-residency uplifts (10% on some providers), embedding and reranking calls, judge calls in the gate, review time, and people.
