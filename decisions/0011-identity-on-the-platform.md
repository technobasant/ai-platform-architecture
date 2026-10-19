# 0011. On the platform, the assistant's tool scopes each query by rewriting it onto per-account tables

- Status: Accepted
- Date: 2026-10-19
- Deciders: security and compliance lead, data lead; proposed by the architect
- Evidence: aia_rewrite_attacks, aia_rewrite_ordinary, dpa_session_variable_filter, aia_rewrite_escapes, aia_rls_catalog

## Context

The lab scopes each query with a database role per account and row-level security
([0002](0002-isolation-in-the-database.md)). A managed platform cannot reasonably hold a
service principal for each of 12,000 accounts, and its row filters are keyed on the platform
user, which a customer is not. The question was what replaces the lab's per-account roles.

## Decision drivers

- A3: the model cannot affect the scope.
- 12,000 accounts in a year, 40,000 in three.
- Works on Databricks or Snowflake, whichever the data architecture chooses.
- Changes no correct answer.

## Options

| | The query cannot change it | Scales to 40,000 accounts | On Databricks | Measured |
|---|---|---|---|---|
| A service identity per account, with a row filter on the identity | ✔ | ✘ | ✔ | the filter: 1 of 5 accounts visible per identity |
| One service identity; a row filter reading a per-request value the tool sets | ✔ if the query cannot set it | ✔ | **✘ a filter function cannot read a session variable** | `UNRESOLVED_COLUMN` on Databricks |
| **One service identity; the tool parses the query, default-deny on expression type, refuses any table but the three it may read, and puts per-account versions of them in front of the query** | ✔ | ✔ | ✔ | 44 of 44 hand-written escapes refused; 28 of 28 attack queries scoped exactly as row-level security; 436 of 436 ordinary answers unchanged |
| The prompt | ✘ (23 of 120 leaked) | ✔ | ✔ | |

## Decision

The assistant's tool scopes every query itself, on any platform, default-deny: one
statement, a query, no write and no `RECURSIVE` anywhere; every expression in it on an
explicit list — the clauses of a `SELECT`, and the operators, aggregates, window, date,
string and maths functions a usage question needs — with any function the parser does not
know refused, which is what stops `query_to_xml()`, `table_to_xml()`, `ts_stat()` and their
kind; every cast to a plain scalar type only, never `regclass`; no schema- or
catalog-qualified table; no table but `accounts`, `users` and `user_daily_activity`,
unqualified, resolved in their own scope and never redefined; no table function but
`generate_series`; anything the parser or the checks cannot analyse refused, never passed.
It then prepends common table expressions with the same three names, each selecting only
the customer's account from the governed table. The service identity it runs as reads the
marts and nothing else.

## Consequences

- A SQL parser is in the trust path. Its refusals are tested in CI against a 44-case escape
  corpus of hand-written attempts to get past it (`lab/escapes.yml`) and 13 ordinary shapes
  that must still be scoped and identical to row-level security, and the isolation suite
  runs against the rewrite on every change.
- The service identity can read every account; the rewrite is the only thing between a
  query and another customer's rows, so the rewrite's code is reviewed like an access
  policy.
- Row-level security filters rows, not the catalog: the customer's own role in the lab
  counted 14 users but could read 1,935 — every account's — from `pg_class.reltuples`; the
  rewrite refuses any query that reads `pg_class` or another catalog table outright, whether
  or not the platform's own identity has that problem.
- Before launch, the escape corpus and the isolation suite run again in the SQL dialect of
  the engine the queries actually run on: the stage-2 usage store, since a warehouse kept
  awake for the assistant would cost more than its whole budget
  ([0014](0014-cost-per-answer.md)), or the platform's SQL if that changes. The function
  list and the parser differ between engines, so a refusal proven on Postgres is not assumed
  to carry over untested.
- If the chosen platform gains a per-request value a filter can read, the platform policy
  replaces the rewrite, or sits under it.

## Revisit when

The chosen platform can key a row filter on a value set per request that a query cannot
change; or the assistant needs a table the rewrite does not cover.

## Amendment (2026-10-19)

A review of the first version of the rewrite (commit 2b80533) found it accepted 23 of the 44
hand-written escapes in `lab/escapes.yml`: among them, functions that run SQL of their own
(`query_to_xml`, `table_to_xml`, `ts_stat` and similar), and a common table expression
defined inside a nested query and read outside it to reach `tenant_roles` and `pg_class`. The
rewrite in this decision is the fix: default-deny on expression type, a cast allow-list, and
CTE visibility scoped to where a name is actually defined. All 44 escapes are now refused, the
13 ordinary shapes in the same corpus are still scoped and identical to row-level security,
and the 28 attack queries and 436 ordinary queries measured before the review are unchanged
(28 of 28, 436 of 436). The catalog gap above (1,935 read where row-level security showed
14) is refused the same way, as reading `pg_class`.

## Evidence

<!-- evidence:start -->
- **28 of 28** queries the models wrote for the isolation attacks that the tool's rewrite scoped to the customer's rows, exactly as row-level security did, including the 23 that leaked through the prompt. Each recorded query parsed with sqlglot, refused unless it reads only the three permitted tables unqualified, then given per-account common table expressions with the same names and run as a role that reads every account; compared with the same query run as the customer's own role. Source: [ai-platform-architecture/results/assistant-rewrite.json](https://github.com/technobasant/ai-platform-architecture/blob/main/results/assistant-rewrite.json)
- **436 of 436** queries for ordinary questions whose result the rewrite left exactly as row-level security gave it, none refused. Every recorded query from the three models, with and without the semantic layer, rewritten and compared as above. Source: [ai-platform-architecture/results/assistant-rewrite.json](https://github.com/technobasant/ai-platform-architecture/blob/main/results/assistant-rewrite.json)
- **UNRESOLVED_COLUMN** what Databricks returns for a row filter function that reads a session variable: a per-request value cannot scope rows. Databricks SQL 2026.39 on Free Edition: DECLARE VARIABLE request_account, then CREATE FUNCTION … RETURN account_id = request_account; the same function keyed on current_user() through a mapping table scoped a table to 1 of 5 accounts. Source: [data-platform-architecture/results/poc-databricks.json](https://github.com/technobasant/data-platform-architecture/blob/main/results/poc-databricks.json)
- **44 of 44** hand-written escapes refused by the hardened, default-deny rewrite; the first version of the rewrite (commit 2b80533) accepted 23 of them. 44 hand-written queries in lab/escapes.yml, shaped to look like usage questions but instead running SQL of their own (query_to_xml, table_to_xml, ts_stat and similar), casting to a catalog type, naming a schema, or redefining a scoped table name inside a nested CTE reaching tenant_roles or pg_class; each parsed with sqlglot and must be refused. The same file's 13 ordinary shapes must still be scoped and identical to row-level security. Source: [ai-platform-architecture/results/assistant-rewrite.json](https://github.com/technobasant/ai-platform-architecture/blob/main/results/assistant-rewrite.json)
- **1,935** users in every account, read from pg_class.reltuples by the customer's own row-level-security role, which counted only 14 users of its own; the rewrite refuses the query. SELECT reltuples FROM pg_class WHERE relname = 'users' AND relnamespace = 'usage'::regnamespace, run as the customer's role, against SELECT count(*) FROM users by the same role; row-level security filters rows, not the catalog. Source: [ai-platform-architecture/results/assistant-rewrite.json](https://github.com/technobasant/ai-platform-architecture/blob/main/results/assistant-rewrite.json)
<!-- evidence:end -->
