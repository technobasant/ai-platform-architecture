# Risks

| # | Risk | Likelihood | Impact | Owner | Mitigation | Trigger to act |
|---|---|---|---|---|---|---|
| R1 | An answer contains another customer's data | low | high | CTO | identity-scoped queries, never prompt-scoped ([0002](../decisions/0002-isolation-in-the-database.md)); isolation suite blocks deploys | any isolation test failure or report |
| R2 | Confident wrong numbers erode trust | medium | high | VP Product | semantic layer; abstention; definition shown; "this is wrong" route; the gate | wrong-answer reports above 1 in 200 |
| R3 | The tool's query rewrite has a gap a query can slip through | low | high | data lead | strict parser, refusal tests in CI, the isolation suite against the rewrite on every change ([0011](../decisions/0011-identity-on-the-platform.md)) | any isolation test failure |
| R4 | Injection through text columns in the data | medium | medium | security lead | read-only identity, one statement, no write tools; injection suite (gap) | before customer launch |
| R5 | Cost per answer above budget on the free plan | medium | medium | CFO | the cheapest model that passes the gate; per-account rate limits | average above $0.01 for a week |
| R6 | The hosted model changes or is withdrawn | medium | medium | data lead | model recorded per response; a second model in the gateway; the gate on any change | provider notice |
| R7 | Definitions drift between the assistant and the dashboards | medium | medium | data lead | one semantic layer for both | a customer reports a mismatch |
| R8 | Questions contain personal data kept too long | low | medium | security lead | 30-day retention; erasure by user ([0013](../decisions/0013-conversation-retention.md)) | retention job fails |
| R9 | The EU AI Act's transparency duty is missed in the interface | low | medium | VP Product | disclosure in the design; part of launch checklist | before customer launch |
