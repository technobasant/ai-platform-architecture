# 0007. Label the distinct string, not the row: cluster before calling a model, and assign by margin

- Status: Accepted
- Date: 2026-10-18
- Evidence: triage_calls, triage_margin

## Context

Short free text (support tags, cancellation reasons, search terms) repeats heavily, with typos, case and Unicode variants. Sending every row to a model pays for the same answer thousands of times, and labels the same meaning inconsistently.

## Decision

- Normalise first (whitespace, Unicode NFKC, case, edge punctuation) and work on distinct keys.
- Embed keys, cluster them, and call a model once per cluster to name it; rows inherit the label of their key.
- New text is assigned to a known cluster only when its nearest centroid beats the second-nearest by a margin; everything else goes to a review pool, where new intents surface as new clusters.

## Consequences

- On day 1, 125 model calls labelled what one call per row would have taken 20,000 calls to label.
- Assigning by margin was 95.2% precise against 66.2% for the best fixed similarity threshold; the cost is a review pool for what the margin rejects.
- The normalisation is a contract: a source that switches Unicode form misses every cached key unless keys are normalised.

## Alternatives considered

- **A model call per row.** Simplest, most expensive, least consistent.
- **A fixed similarity threshold.** Similarities are compressed into a narrow band; a threshold either over-assigns or assigns nothing.

## Evidence

<!-- evidence:start -->
- **125 vs 20,000** LLM labelling calls on day 1, one per cluster against one per row. 20,000 short-text rows normalised to 1,537 distinct keys, clustered with UMAP and HDBSCAN; one call per cluster plus one taxonomy call. Source: [short-text-triage/MEASUREMENTS.md](https://github.com/technobasant/short-text-triage/blob/main/MEASUREMENTS.md)
- **95.2% vs 66.2%** precision assigning new rows to known intents: a margin rule against the best absolute similarity threshold. Day-2 rows assigned to the nearest centroid only when it beats the second by a margin of 0.03 (1,728 rows) against a fixed cosine threshold of 0.92 (2,862 rows); the rest go to review. Source: [short-text-triage/MEASUREMENTS.md](https://github.com/technobasant/short-text-triage/blob/main/MEASUREMENTS.md)
<!-- evidence:end -->

## Related decisions in the labs

- short-text-triage [README](https://github.com/technobasant/short-text-triage#readme)
