# Quality attributes

Targets for the reference design, with what the labs have measured toward each. Three are not met yet, and are kept as targets rather than lowered to fit.

| Attribute | Target | Why | How it is measured | Measured so far |
|---|---|---|---|---|
| Wrong answers that publish themselves | under 1% of auto-published answers | a wrong answer nobody reviewed is the costliest failure | evaluation set with a computed answer key; every auto-published case scored | 3 of 37 (8%): not met |
| Unanswerable questions declined | at least 7 of 8 | invented answers to unanswerable questions are the commonest harmful failure | labelled unanswerable cases | 4 of 8: not met |
| Answer accuracy | at least 90% | below that, reviewers stop trusting the feature | computed answer key | 48 of 54 (88.9%): not met |
| Actions from planted instructions | none | an injected instruction must never act | adversarial cases | 0 of 5 |
| Filtered retrieval | every call returns what it asked for; recall@10 at least 0.9 | a starved result looks like a confident answer from too little | row counts; recall against exact search | 0.949 with iterative scan |
| Regression detection | a significant drop fails; a noisy drop warns with the sample size needed | a gate that fails on noise is switched off | paired gate | p = 0.39 on a 4.8-point drop: warned, as designed |
| Latency, help-centre answer | p95 under 2.5 s | customers abandon slower answers | gate latency budget | baseline 1,469 ms; a change to 4,422 ms was stopped |
| Feature serving, scoring models | p99 under 10 ms server side | scores sit in the request path | serving benchmark | 4.3 ms or less |
| Reproducibility | identical outputs on replay | CI must test behaviour without a model | replay against the live run | 54 of 54; 20 of 20 with the cache off |
| Cost per answer | known before launch, enforced at the gateway | spend follows volume | cost model, then gateway metering | modelled only ([model and cost](model-and-cost.md)) |

## Not measured yet

- Tenant isolation under adversarial questions ([threat model](threat-model.md)).
- Injection through retrieved documents.
- Spend caps under load, and the gateway's own availability.
- Any of the above on hosted frontier models: the labs ran small local models, so rates would differ; the methods transfer.
