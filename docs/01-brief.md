# 1. The brief

Stage 3 of the engagement in
[data-platform-architecture](https://github.com/technobasant/data-platform-architecture):
the same fictional client, a B2B SaaS company with 6,000 customer accounts, now with an
analytical platform that holds its history in governed tables. The client and its data are
fictional; the assistant's behaviour is measured on a lab copy of the usage mart
([lab/](../lab)).

## What the product wants

An assistant inside the product that answers a customer's questions about their own usage,
in plain language: "How many reports did we create last month?", "Which day in September was
busiest?", "How many people used the mobile apps?". Customers ask support these questions
today, and support answers them by hand from the BI tool.

| | |
|---|---|
| Who asks | users of customer accounts, inside the product, signed in |
| About what | their own account's usage: events, people, features, platforms, roles, over the history the platform holds |
| How many | about 2,000 questions a day at launch, if a quarter of active accounts ask one a week (an assumption) |
| Answer | a number or a short list, the definition it used, and the period it covered; or "the data does not have this" |
| When | a pilot with internal users in month 9, enterprise customers in month 10, every plan in month 12 |

## Why it is hard

- **Another customer's data is one wrong `WHERE` away.** The assistant writes SQL against
  tables that hold every account. Whatever keeps a customer to their own rows must not be
  something a question can talk its way past.
- **The schema does not say what the business means.** "People who used the product" is a
  count of distinct users, not a sum of daily counts; "last week" starts on Monday. A model
  given only table definitions has to guess.
- **A confident wrong number is worse than no answer.** Customers act on usage numbers when
  they decide seats and renewals.
- **Every answer costs money and time,** and the free plan has to be affordable.

## Stakeholders

| Who | Cares most about | Will judge it by |
|---|---|---|
| VP Product (sponsor) | adoption; questions support no longer answers by hand | answers customers use |
| CTO | nothing that can leak or take the product down | isolation tested in CI; the assistant can fail without the product failing |
| Security and compliance lead | the DPA, SOC 2, the EU AI Act's transparency duty | isolation evidence, logs, retention, disclosure |
| Head of support | fewer usage tickets, and wrong answers flagged | answer accuracy; a route for "this is wrong" |
| Data team | definitions that stay consistent with the dashboards | one semantic layer for both |
| CFO | cost | cost per answer, and a monthly ceiling |

## Constraints

- **Built on stage 1.** The assistant reads only the governed marts, under the platform's
  access control; it gets no data of its own.
- **Customers are not platform users.** They sign in to the product, not to the analytical
  platform, so their identity has to be carried to the data by the assistant's own service.
- **Cost.** At most $0.01 per answer on average, and $1,500 a month at launch volume.
- **Latency.** An answer within 10 seconds, 95 times in 100.
- **Data protection.** Processing stays in the EU region; no customer data trains a model;
  questions and answers are kept 30 days unless a customer is told otherwise.
- **Team.** The same four data people, with product engineering for the interface.

## Out of scope

Actions on the customer's behalf (changing seats, exporting data): the assistant answers,
it does not act. Answers from documentation (a help-centre assistant) and models that score
customers (churn, fraud), which the client may add later on the same foundations.
