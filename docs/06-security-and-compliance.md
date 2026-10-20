# 6. Security and compliance

What can go wrong with an assistant that writes SQL over every customer's data, what stops
it, and what has been tested. "Not tested" means designed and not yet exercised.

## Threats: the OWASP Top 10 for LLM Applications (2025)

| Risk | For this assistant | Controls | Tested |
|---|---|---|---|
| LLM01 Prompt injection | a question that tells the model to ignore its instructions, claims to be an admin, or embeds SQL | the account scope is applied by the data's identity, not the prompt ([0002](../decisions/0002-isolation-in-the-database.md)); one read-only statement ([0012](../decisions/0012-sql-guard.md)) | 20 direct attacks, two customers each, three models ([3. Options](03-options.md#isolation)). Injection through data (an account name carrying instructions): not tested |
| LLM02 Sensitive information disclosure | another customer's usage; personal data | the tool scopes every query to the account — a role per account with row-level security in the lab, one service identity and the tool's rewrite on the platform ([0011](../decisions/0011-identity-on-the-platform.md)); the marts hold no personal data | isolation measured with and without the database enforcing it |
| LLM03 Supply chain | a model or provider changing underneath | the model and endpoint recorded with every response; the gate re-run on a model change | recorded per response |
| LLM04 Data and model poisoning | the evaluation set or the semantic layer edited to pass | both in Git, reviewed; reference answers computed from data, not written by hand | by design |
| LLM05 Improper output handling | SQL written by the model | one `SELECT`, read-only role, timeout, row limit; results rendered as data | refusals counted per run |
| LLM06 Excessive agency | an assistant that changes seats or sends exports | it has no tool that writes or sends ([1. Brief](01-brief.md#out-of-scope)) | by design |
| LLM07 System prompt leakage | the prompt shown to a customer | nothing secret in the prompt: schema and definitions only; credentials live in the tool | by design |
| LLM08 Vector and embedding weaknesses | not used: answers come from SQL, not retrieval | | |
| LLM09 Misinformation | a confident wrong number | the semantic layer; abstention as an answer; the definition and period shown with every answer; the gate | accuracy and abstention measured |
| LLM10 Unbounded consumption | a burst of questions, a runaway query | per-feature and per-account budgets at the gateway; statement timeout and row limit | timeouts in the lab; budgets not load-tested |

## Data protection

- **What the model sees:** the question, the schema and the definitions. Query results are
  not sent back to the model in this design; the service composes the answer from the rows.
- **Where it runs:** on the platform's model serving in the company's EU region, so prompts
  do not leave the region or the platform's data processing agreement.
- **What is kept:** question, SQL, result summary, model and prompt version, 30 days, then
  deleted; deleted earlier for an erasure request
  ([0013](../decisions/0013-conversation-retention.md)).
- **Training:** no customer question or answer is used to train or tune a model.

## Regulation and frameworks

| | What applies | How the design meets it |
|---|---|---|
| EU AI Act | a general-purpose model used in a system that interacts with people: not a high-risk use; transparency (Article 50: people are told they are interacting with an AI system) and AI literacy (Article 4) for the staff who run it | the interface says it is an AI assistant and shows the definition used; the runbooks and the evaluation are the team's training material |
| GDPR | questions may contain personal data; erasure and retention | 30-day retention; erasure by user; processing in the EU region |
| SOC 2 (the company's audit) | access, change management, monitoring | the assistant's identities in Terraform; prompt, model and definition changes through the gate; traces and audit |
| NIST AI RMF | Govern, Map, Measure, Manage | ownership and the decision records; the brief and threats above; the evaluation set and isolation suite; the gate, monitoring and runbooks |
| ISO/IEC 42001 | an AI management system, if the company certifies | the same artefacts are its evidence: policy (principles), risk register, evaluation records, change control |

## The gaps, in order

1. Injection through data: an account name, a report title or any text column carrying
   instructions, in the isolation suite.
2. The rewrite on the engine the queries will run on: measured on Postgres with the lab's
   recordings ([0011](../decisions/0011-identity-on-the-platform.md)); to be re-run in the
   stage-2 usage store's SQL dialect before launch ([0014](../decisions/0014-cost-per-answer.md)).
3. Budgets under load: a burst of questions and a looping client against the gateway.
