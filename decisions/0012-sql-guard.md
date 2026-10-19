# 0012. One read-only statement, with a row limit and a timeout, or nothing

- Status: Accepted
- Date: 2026-10-19
- Deciders: CTO, data lead; proposed by the architect
- Evidence: aia_db_isolation

## Context

Generated SQL can contain several statements, writes, role changes, settings, or a query that
runs for an hour. The identity limits what is read ([0002](0002-isolation-in-the-database.md));
the guard limits what is run.

## Decision drivers

- A4: nothing but reads; LLM05 and LLM10 in the
  [threat model](../docs/06-security-and-compliance.md).
- Simple enough to be correct.

## Options

| | Writes impossible | Runaway queries | Complexity |
|---|---|---|---|
| Trust the model | ✘ | ✘ | ✔ |
| Parse and allow-list every construct | ✔ | ◐ | ✘ a parser to maintain |
| **One statement, a read-only identity, a statement timeout and a row limit; anything else refused** | ✔ by the identity | ✔ | ✔ |

## Decision

The tool refuses more than one statement, runs the query as a read-only identity in a
read-only transaction, with a 15-second timeout and a 50-row limit, and returns the rows or
an error. It never repairs a query.

## Consequences

- A role change or a setting inside the query cannot widen access: the lab's roles see one
  account each, whatever the query does.
- Some legitimate queries will hit the limits; the refusal rate is watched.

## Revisit when

A legitimate need for longer queries appears, which is a mart to build, not a limit to raise.

## Evidence

<!-- evidence:start -->
- **0 of 120** the same requests that returned another account's data when the query ran as the customer's own database role. One read-only login role per account, row-level security on every table keyed on the session's login role; each role sees 1 of the 200 accounts. Source: [ai-platform-architecture/results/assistant.json](https://github.com/technobasant/ai-platform-architecture/blob/main/results/assistant.json)
<!-- evidence:end -->
