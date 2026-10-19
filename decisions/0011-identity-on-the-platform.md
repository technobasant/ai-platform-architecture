# 0011. On the chosen platform, the account scope is a policy on a value the query cannot change

- Status: Proposed
- Date: 2026-10-19
- Deciders: security and compliance lead, data lead; proposed by the architect
- Evidence:

## Context

The lab scopes each query with a database role per account and row-level security
([0002](0002-isolation-in-the-database.md)). A managed platform cannot reasonably hold a
service principal for each of 12,000 accounts, and its row filters are normally keyed on the
platform user, which a customer is not.

## Decision drivers

- A3: the model cannot affect the scope.
- 12,000 accounts in a year, 40,000 in three.
- Works on Databricks or Snowflake, whichever the data architecture chooses.

## Options

| | The query cannot change it | Scales to 40,000 accounts | On Databricks | On Snowflake |
|---|---|---|---|---|
| A service identity per account | ✔ | ✘ | ✘ | ✘ |
| One service identity; a row filter or row access policy reading a per-request value the tool sets | ✔ if the query cannot set it | ✔ | to be tested | to be tested |
| One service identity; the tool parses the query and rewrites it onto views it defines for the account | ✔ if parsing is strict | ✔ | ✔ | ✔ |
| The prompt | ✘ (23 of 120 leaked) | ✔ | ✔ | ✔ |

## Decision

Proposed: a platform policy on a per-request value where the platform guarantees the query
cannot change it; otherwise the tool's rewrite onto per-account views, with a strict parser.
Decided with the platform, by running the lab's isolation suite on it.

## Consequences

- Until decided, the assistant does not launch to customers.
- The rewrite option puts a SQL parser in the trust path, and needs its own tests.

## Revisit when

The data architecture's platform decision is made; this record becomes Accepted with the
isolation suite's result on that platform.

## Evidence

<!-- evidence:start -->
Not measured yet; see the status above.
<!-- evidence:end -->
