# 0011. On the platform, the assistant's tool scopes each query by rewriting it onto per-account tables

- Status: Accepted
- Date: 2026-10-19
- Deciders: security and compliance lead, data lead; proposed by the architect
- Evidence: aia_rewrite_attacks, aia_rewrite_ordinary, dpa_session_variable_filter

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
| **One service identity; the tool parses the query, refuses any table but the three it may read, and puts per-account versions of them in front of the query** | ✔ | ✔ | ✔ | 28 of 28 attack queries scoped exactly as row-level security; 436 of 436 ordinary answers unchanged |
| The prompt | ✘ (23 of 120 leaked) | ✔ | ✔ | |

## Decision

The assistant's tool scopes every query itself, on any platform. It parses the generated SQL
(one statement, a query, no schema- or catalog-qualified table, no table but `accounts`,
`users` and `user_daily_activity`, none of them redefined, no table function but
`generate_series`), and prepends common table expressions with the same three names, each
selecting only the customer's account from the governed table. The service identity it runs
as reads the marts and nothing else.

## Consequences

- A SQL parser is in the trust path. Its refusals are tested in CI with the escapes that
  matter (a qualified table, another table, a redefined name, a file-reading table
  function, two statements, a write), and the isolation suite runs against the rewrite on
  every change.
- The service identity can read every account; the rewrite is the only thing between a
  query and another customer's rows, so the rewrite's code is reviewed like an access
  policy.
- If the chosen platform gains a per-request value a filter can read, the platform policy
  replaces the rewrite, or sits under it.

## Revisit when

The chosen platform can key a row filter on a value set per request that a query cannot
change; or the assistant needs a table the rewrite does not cover.

## Evidence

<!-- evidence:start -->
- **28 of 28** queries the models wrote for the isolation attacks that the tool's rewrite scoped to the customer's rows, exactly as row-level security did, including the 23 that leaked through the prompt. Each recorded query parsed with sqlglot, refused unless it reads only the three permitted tables unqualified, then given per-account common table expressions with the same names and run as a role that reads every account; compared with the same query run as the customer's own role. Source: [ai-platform-architecture/results/assistant-rewrite.json](https://github.com/technobasant/ai-platform-architecture/blob/main/results/assistant-rewrite.json)
- **436 of 436** queries for ordinary questions whose result the rewrite left exactly as row-level security gave it, none refused. Every recorded query from the three models, with and without the semantic layer, rewritten and compared as above. Source: [ai-platform-architecture/results/assistant-rewrite.json](https://github.com/technobasant/ai-platform-architecture/blob/main/results/assistant-rewrite.json)
- **UNRESOLVED_COLUMN** what Databricks returns for a row filter function that reads a session variable: a per-request value cannot scope rows. Databricks SQL 2026.39 on Free Edition: DECLARE VARIABLE request_account, then CREATE FUNCTION … RETURN account_id = request_account; the same function keyed on current_user() through a mapping table scoped a table to 1 of 5 accounts. Source: [data-platform-architecture/results/poc-databricks.json](https://github.com/technobasant/data-platform-architecture/blob/main/results/poc-databricks.json)
<!-- evidence:end -->
