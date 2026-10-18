# Threat model

The [OWASP Top 10 for LLM Applications, 2025 edition](https://genai.owasp.org/llm-top-10/), mapped to this architecture: what each risk looks like here, the controls, and what has been tested. "Not tested" means designed and not yet exercised.

| Risk | Here | Controls | Tested |
|---|---|---|---|
| LLM01 Prompt Injection | instructions planted in a ticket, a document or a table cell | tools cannot act, only propose ([0001](../decisions/0001-one-governed-boundary-to-data.md)); instructions found in data are surfaced to the reviewer; actions need approval ([0002](../decisions/0002-outputs-become-state-after-checks.md)) | 5 planted instructions led to 0 actions. Injection through retrieved help-centre passages: not tested |
| LLM02 Sensitive Information Disclosure | another tenant's data in an answer; personal data sent to a hosted model | tools run under the caller's permissions and tenant; retrieval filters by tenant; the gateway redacts personal data ([0011](../decisions/0011-model-gateway.md)) | not tested as an adversarial suite |
| LLM03 Supply Chain | a changed model, package or tool server | model digests recorded with every run; CI actions pinned by commit; datasets checked for licences | model digests recorded in the evaluation runs |
| LLM04 Data and Model Poisoning | poisoned help-centre content; a corrupted evaluation set or label sample | retrieval only from owned, governed sources; evaluation sets hashed; labels audited case by case ([0005](../decisions/0005-judges-are-instruments.md)) | label audit found the answer key wrong 7 times in 13 disagreements; poisoning itself not tested |
| LLM05 Improper Output Handling | SQL written by the model; text rendered in the product | SQL parsed and allowed only against listed views; every output validated against a schema; outputs rendered as data | the SQL guard's own test cases in governed-agent |
| LLM06 Excessive Agency | an agent that sends, deletes or changes | proposals only; review before execute; an outbox executes approved actions once ([0002](../decisions/0002-outputs-become-state-after-checks.md)) | 0 of 5 planted instructions produced a proposal |
| LLM07 System Prompt Leakage | the prompt revealed through questions | nothing secret in prompts; credentials live in the gateway and tool server | by design; not tested |
| LLM08 Vector and Embedding Weaknesses | retrieval across tenants; filters that silently starve results | tenant filter enforced in the retrieval tool, not by the model; result counts checked ([0006](../decisions/0006-retrieval-by-filtered-recall.md)) | filtered recall measured; cross-tenant isolation not tested |
| LLM09 Misinformation | a confident wrong answer | grounding check of quoted numbers; abstention as a typed answer; review | 3 of 37 wrong answers still passed every check; 4 of 8 unanswerable questions declined |
| LLM10 Unbounded Consumption | an agent loop, a prompt that grows context, a spike in traffic | an explicit graph with bounded steps; timeouts; per-feature token and cost budgets at the gateway | latency budget enforced in the gate; spend caps not load-tested |

## The gaps, in order

1. An adversarial isolation suite: questions and documents that try to reach another tenant's data, run in CI against every feature.
2. Injection through retrieved content, not only through structured data.
3. Spend caps under load: a burst of traffic and a looping agent against the gateway's budgets.
