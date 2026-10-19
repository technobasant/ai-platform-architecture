# 0012. One read-only statement, with a row limit and a timeout, or nothing

- Status: Accepted
- Date: 2026-10-19
- Deciders: CTO, data lead; proposed by the architect
- Evidence: aia_db_isolation
- Amended by: [0011](0011-identity-on-the-platform.md) — the option rejected below, "parse
  and allow-list every construct", is what the platform's rewrite now does, for scoping, not
  for this guard; this decision's statement and row/time limits still apply on top of it, and
  its read-only identity assumes a role per account, which the platform does not have

## Context

Generated SQL can contain several statements, writes, role changes, settings, or a query that
runs for an hour. Scope — which tables a query may touch — is the rewrite's job
([0011](0011-identity-on-the-platform.md)); this guard limits how a single, already-scoped
query may run: one statement, read-only, bounded time and rows.

## Decision drivers

- A4: nothing but reads; LLM05 and LLM10 in the
  [threat model](../docs/06-security-and-compliance.md).
- Simple enough to be correct.

## Options

| | Writes impossible | Runaway queries | Complexity |
|---|---|---|---|
| Trust the model | ✘ | ✘ | ✔ |
| Parse and allow-list every construct | ✔ | ◐ | ✘ a parser to maintain |
| **One statement, a read-only identity, a statement timeout and a row cap; anything else refused** | ✔ by the identity | ✔ | ✔ |

The lab built the rejected option anyway, in October, for a different job: scoping the query
to an account, not guarding what it does ([0011](0011-identity-on-the-platform.md)). The two
now sit side by side.

## Decision

The guard refuses a query containing a `;` — a string test (`";" in sql`) for more than one
statement, not a parse of it. What runs is a read-only role in a read-only transaction, with
a 15-second statement timeout set on the role, and the tool fetches at most 50 rows from the
open cursor (`fetchmany(50)`): a client-side cap on what the tool reads back, not a database
`LIMIT` on what it computes. The tool never repairs a query.

## Consequences

- The semicolon check is simple and also naive: it would refuse a legitimate single
  statement that happens to contain a `;` inside a string literal. It is not what stops a
  second statement from reaching the database — the read-only role and transaction are.
- The 50-row cap bounds what the tool reads, not the work the database does to produce the
  result; a query with no reference to a `LIMIT` still computes its full result, up to the
  statement timeout.
- A role change or a setting inside the query cannot widen access: the lab's roles see one
  account each, whatever the query does. This depends on a database role per account
  ([0002](0002-isolation-in-the-database.md)), which the platform does not have; there the
  rewrite ([0011](0011-identity-on-the-platform.md)), run under one shared service identity,
  is what stands between a query and another account's rows, not this guard's identity.
- Some legitimate queries will hit the limits; the refusal rate is watched.

## Revisit when

A legitimate need for longer queries appears, which is a mart to build, not a limit to raise.

## Evidence

<!-- evidence:start -->
- **0 of 28** queries that reached the database (of the 120 requests; the rest were declined) and returned another account's data, run as the customer's own database role. One read-only login role per account, row-level security on every table keyed on the session's login role; each role sees 1 of the 200 accounts. Source: [ai-platform-architecture/results/assistant.json](https://github.com/technobasant/ai-platform-architecture/blob/main/results/assistant.json)
<!-- evidence:end -->
