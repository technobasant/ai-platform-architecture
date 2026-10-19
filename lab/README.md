# The usage assistant lab

Everything behind [3. Options, measured](../docs/03-options.md): a seeded copy of the usage mart,
customer questions with answers computed by SQL, requests for other accounts' data, and the
runners that put them to models and score the answers.

| File | What it is |
|---|---|
| [`compose.yml`](compose.yml), [`data.sql`](data.sql) | Postgres 17 with the mart: 200 accounts, 1,935 users, 142,896 rows of daily activity (July to September 2026), a read-only login role per account with row-level security, and a role that reads everything |
| [`semantic.yml`](semantic.yml) | the semantic layer: periods, vocabulary, metric definitions, rules, three examples |
| [`questions.py`](questions.py), [`questions.json`](questions.json) | 70 answerable questions (24 templates for different accounts) and 20 unanswerable ones, with reference answers |
| [`attacks.yml`](attacks.yml) | 20 requests that only another account's data, or every account's, can answer |
| [`run.py`](run.py) | accuracy with and without the semantic layer, and isolation with and without the database enforcing it, for Qwen3 8B (Ollama), Llama 3.3 70B and gpt-oss-120b (Databricks model serving) |
| [`genie.py`](genie.py) | the same questions asked of a Databricks AI/BI Genie space with the semantic layer as instructions |
| [`rewrite.py`](rewrite.py) | the tool's query rewrite onto per-account tables, run on every recorded query and compared with row-level security |

## Reproducing it

```bash
cd lab && docker compose up -d mart
docker compose exec -T mart psql -U postgres -q -f /lab/data.sql
cd .. && uv sync --group lab
uv run python lab/questions.py --check     # the question set matches this mart
uv run python lab/run.py --replay          # re-score the recorded responses: no model calls
uv run python lab/genie.py --replay
uv run python lab/rewrite.py --check       # the tool's rewrite on every recorded query
```

`lab/run.py` without `--replay` asks the models for anything not yet recorded: Ollama with
`qwen3:8b` on localhost, and `DATABRICKS_HOST` and `DATABRICKS_TOKEN` for the hosted models.
`lab/genie.py` also needs `DATABRICKS_HTTP_PATH` (a SQL warehouse); it copies the tables to
`workspace.ai_assistant` and creates the space.

Every response is recorded with a hash of its exact prompt in
[`results/assistant-responses.jsonl`](../results/assistant-responses.jsonl) and
[`results/assistant-genie-responses.jsonl`](../results/assistant-genie-responses.jsonl). CI
builds the mart from `data.sql` and must reproduce the published results from the
recordings.

## How answers are scored

The reference answer is the first column of the first row of a reference query. A model's
answer is correct if every reference value appears in the first row of its query's result,
numbers compared to one decimal and dates as ISO dates. Questions whose answer would be zero,
missing or tied between two items are not asked. An unanswerable question is declined if the
reply is UNANSWERABLE with no query. Genie's answers are scored by the same checker on the
result of the query it ran.

## Limits

- One run per condition, temperature 0. Hosted models are not perfectly deterministic; the
  recordings, not a re-run, are the published result.
- 90 questions over one mart: enough to separate 55 from 70 correct, not to rank two models
  that both answered 70.
- Genie's space ran as the workspace's one user, with access to every account; the
  customer-identity question is in [0011](../decisions/0011-identity-on-the-platform.md).
- Latency on Free Edition's shared serving and on a laptop is indicative only.
- One of the semantic layer's examples teaches a metric the questions ask about for another
  month.
