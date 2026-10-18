# 0006. The vector store is chosen by recall under the product's filters, not by unfiltered benchmarks

- Status: Accepted
- Date: 2026-10-18
- Evidence: retrieval_engine_quality, retrieval_filter_rows, retrieval_iterative_scan, retrieval_filter_middle

## Context

Retrieval in a multi-tenant product is almost always filtered: this tenant's documents, this product area, this date range. Vector indexes are tuned and benchmarked unfiltered. A filter applied after the index search returns fewer rows than asked for, silently.

## Decision

- Engines are compared at the same recall, on the product's own filter selectivities, not at default parameters on unfiltered queries.
- Filtered search uses the engine's pre-filtering or iterative scan, and every retrieval call checks that it got the number of rows it asked for.
- With no measurable quality difference between engines, the choice goes to operations: pgvector where Postgres is already run, a dedicated engine where filtering or scale needs it.

## Consequences

- pgvector, Qdrant and OpenSearch were within 0.0015 nDCG@10 of exact search on the same embeddings: quality does not choose the engine.
- Post-filtered HNSW at 10% selectivity returned 3.9 of 10 rows on average, with no error. pgvector's iterative scan restored recall@10 to 0.949; OpenSearch's efficient filter reached 0.745.
- Filter selectivity becomes a number the product team has to know.

## Alternatives considered

- **Pick by an unfiltered public benchmark.** Measures the case the product never runs.

## Evidence

<!-- evidence:start -->
- **≤ 0.0015** nDCG@10 between pgvector, Qdrant and OpenSearch and exact search. The same bge-small vectors loaded into all three engines, ef_search 200, scored against human relevance judgements on SciFact, ArguAna and Touché 2020. Source: [retrieval-bench/MEASUREMENTS.md](https://github.com/technobasant/retrieval-bench/blob/main/MEASUREMENTS.md)
- **3.9 of 10** rows returned by post-filtered HNSW at 10% selectivity. Pgvector 0.8.7 HNSW at ef_search 40 with iterative scan off, 1,000 queries over 381,559 vectors, a filter keeping 10% of rows; recall@10 0.391 against exact kNN over the rows that pass. Source: [retrieval-bench/MEASUREMENTS.md](https://github.com/technobasant/retrieval-bench/blob/main/MEASUREMENTS.md)
- **0.949** recall@10 restored by pgvector's iterative scan at 10% selectivity. Hnsw.iterative_scan = relaxed_order, ef_search 40, same queries and filter as the post-filtered run. Source: [retrieval-bench/MEASUREMENTS.md](https://github.com/technobasant/retrieval-bench/blob/main/MEASUREMENTS.md)
- **0.745** recall@10 of OpenSearch's efficient filter at 10% selectivity. Filter inside the knn clause, Faiss HNSW at ef_search 40, 1,000 queries over 381,559 vectors, against exact kNN over the rows that pass. Source: [retrieval-bench/MEASUREMENTS.md](https://github.com/technobasant/retrieval-bench/blob/main/MEASUREMENTS.md)
<!-- evidence:end -->

## Related decisions in the labs

- retrieval-bench [0002 Compare engines at the same recall](https://github.com/technobasant/retrieval-bench/blob/main/docs/adr/0002-iso-recall-operating-point.md), [0001 Embed once, load the same vectors everywhere](https://github.com/technobasant/retrieval-bench/blob/main/docs/adr/0001-embed-once-row-ids.md)
