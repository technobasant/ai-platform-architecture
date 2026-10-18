# Operations

## Changing a prompt, a model or a provider

1. Run the evaluation gate on live models: baseline against candidate, the same cases ([0004](../decisions/0004-release-gate-on-paired-evaluation.md)).
2. Compare cost per answer and p95 latency against the feature's budgets, not only quality.
3. Re-record the replay responses CI uses ([0011](../decisions/0011-model-gateway.md)).
4. Release by canary ([0012](../decisions/0012-ai-services-ship-by-canary.md)) and watch outcomes for the first week.

## Changing the judge

Calibrate the new judge against the labelled sample before it gates anything: true- and false-positive rates, and agreement. Read every disagreement with the labels ([0005](../decisions/0005-judges-are-instruments.md)).

## A wrong answer is reported

1. Add the case to the evaluation set first, with the right answer.
2. Reproduce it from the recorded inputs and tool results.
3. Decide which check should have caught it; change that check or the prompt; run the gate.
4. If it was auto-published, review whether the feature's auto-publication policy still holds.

## A provider is down or rate-limited

The gateway falls back to the next model configured for the feature. Features that cannot meet their quality bar on the fallback decline with a typed "unavailable" answer rather than answering worse.

## Spend jumps

The gateway's per-feature metering names the feature. Usual causes: an agent loop taking more steps, context growing with retrieved passages, a traffic spike. Cap at the gateway first, then fix the cause, then add a gate case that would have caught it.

## The review queue backs up

The queue's size is set by the checks. Look at why items are held: if one check holds mostly correct answers, tighten it; if wrong answers are arriving, the feature may need auto-publication turned off until the gate shows otherwise.

## An injection is found

Add it to the adversarial set; confirm the tools it targeted cannot act; check whether any proposal it produced was approved, and through the outbox log, whether anything executed.

## A classifier behind a dashboard is upgraded

Re-estimate the history with the new model's error rates, or mark a break in the series. Never let the upgrade show up as a trend ([0008](../decisions/0008-correct-counted-labels.md)).
