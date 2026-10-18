# 0013. Each AI feature has a cost per answer, from a model of tokens and prices, before it ships

- Status: Proposed. Modelled from list prices; no feature's bill has been observed.
- Date: 2026-10-18
- Evidence:

## Context

The cost of an AI feature is tokens per call, times calls per answer, times answers per month, times price. Each factor varies by an order of magnitude between designs: model size, retrieved context, agent loops, caching, batching. Teams find out from the invoice.

## Decision

- Each feature states its expected tokens per call, calls per answer and volume, and the [cost model](../cost/) prices it on the candidate models.
- The gateway ([0011](0011-model-gateway.md)) enforces the resulting budget per feature.
- Self-hosting a model is considered only above the request rate at which a dedicated GPU instance costs the same as API calls, and only after measuring that the instance can serve that rate.

## Consequences

- Model choice becomes a cost decision with numbers, not a default.
- The model rests on assumed token counts per call; the [guide](../docs/model-and-cost.md) states them, and they are the first thing to replace with measured ones.

## Alternatives considered

- **Pick the strongest model and watch the bill.** Works until volume grows.

## Evidence

<!-- evidence:start -->
Not measured yet; see the status above.
<!-- evidence:end -->
