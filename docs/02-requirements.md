# 2. Requirements

What the assistant must do for the people in [the brief](01-brief.md), as scenarios that can
be tested. "Lab" is what the measurement in [lab/](../lab) found for the recommended design
([4. Target architecture](04-target-architecture.md)); the full results are in
[3. Options](03-options.md).

| # | Quality | Scenario | Target | Lab |
|---|---|---|---|---|
| A1 | Accuracy | a customer asks an answerable question about their own usage | the right number, item or date, 9 times in 10 | 70 of 70 (gpt-oss-120b and Llama 3.3 70B with the semantic layer) |
| A2 | Knowing what it does not know | a customer asks something the data cannot answer | "the data does not have this", 19 times in 20 | 20 of 20 (gpt-oss-120b) |
| A3 | Tenant isolation | a customer asks, innocently or not, for another account's data or everyone's | never another account's rows or totals | 0 of the 28 queries that reached the database leaked with the customer's database role; 28 of 28 attack queries scoped by the tool's rewrite; 23 of 120 leaked with the prompt alone |
| A4 | No side effects | any question, including instructions hidden in it | the assistant only reads; nothing is written, sent or changed | read-only role; one statement per query |
| A5 | Latency | a question is asked | an answer within 10 s, 95 times in 100 | 2.9 s median, 5.5 s p95 (gpt-oss-120b) |
| A6 | Cost | a month of questions at launch volume | under $0.01 an answer on average; under $1,500 a month | $0.00032 an answer; about $19 a month at launch volume for the model; a warehouse awake for the queries would add $961 to $2,657 a month ([0014](../decisions/0014-cost-per-answer.md)) |
| A7 | Traceability | support asks why a customer got an answer | the question, SQL, result, model, prompt version and definitions used, for 30 days | every response recorded and replayable |
| A8 | Change safety | a prompt, model or definition changes | no release that lowers A1, A2 or A3 on the evaluation set | the evaluation set re-scored in CI from recorded responses |
| A9 | Consistency with dashboards | a customer compares an answer with the BI tool | the same definition gives the same number | one semantic layer for both |
| A10 | Transparency | a customer uses the assistant | told it is an AI system, shown the definition and period used | product design |
| A11 | Data protection | a customer or a user asks to be erased | their questions and answers are deleted within 30 days | retention job; not yet built |

## Ranking

Isolation (A3) and side effects (A4) are not traded against anything. Then knowing what it
does not know (A2) before accuracy (A1): a declined answer costs a support ticket, a wrong
one costs trust. Then latency and cost.
