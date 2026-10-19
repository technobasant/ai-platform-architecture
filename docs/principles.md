# Principles

- **The model proposes; code decides what it may touch.** The model writes a query. Which rows
  that query can read is decided by an identity the model never sees.
- **Isolation is never a sentence in a prompt.** A prompt is a request to a model, not a
  control.
- **Definitions belong to the business, not to the model.** What "active users" and "last week"
  mean is written down once and given to every model and every dashboard.
- **Not knowing is an answer,** and it is measured on its own.
- **Show the working.** Every answer carries the definition and period it used.
- **Gate on evidence.** Paired cases, significance, and separate latency, cost and isolation
  budgets; nothing ships on a demo.
- **Record everything once.** Every model response is kept, so a score can be re-computed,
  a complaint reproduced, and a change compared, without asking the model again.
- **A cost per answer before launch,** not an invoice after it.
