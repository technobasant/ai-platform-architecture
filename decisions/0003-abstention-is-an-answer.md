# 0003. "The data does not have this" is a supported answer, and it is measured separately

- Status: Accepted
- Date: 2026-10-18
- Evidence: agent_unanswerable_admitted

## Context

Some questions cannot be answered from the data the feature has. A model asked one of them tends to answer anyway, plausibly. An evaluation set made only of answerable questions never sees this failure.

## Decision

- Every feature's evaluation set includes questions its data cannot answer, labelled as such.
- Abstention is part of the output schema: a typed "not answerable from the available data" with the reason, which the product renders as an answer, not an error.
- The share of unanswerable questions correctly declined is reported on its own, next to accuracy, and is a release criterion.

## Consequences

- The governed agent declined 4 of 8 unanswerable questions. This is its weakest measured behaviour, and the reason the check is kept separate: averaged into overall accuracy it would be invisible.
- Abstention can be overdone; the evaluation set needs answerable questions near the boundary too, so a feature that declines everything fails.

## Alternatives considered

- **Rely on the system prompt ("say you don't know").** Necessary, not sufficient, and untested without labelled unanswerable cases.

## Evidence

<!-- evidence:start -->
- **4 of 8** unanswerable questions answered with “the data does not have this”. Eight questions with no supporting data (NPS, margin without costs, delivery time without delivery dates and others); 95% CI 22–78%. Source: [governed-agent/MEASUREMENTS.md](https://github.com/technobasant/governed-agent/blob/main/MEASUREMENTS.md)
<!-- evidence:end -->

## Related decisions in the labs

- governed-agent [MEASUREMENTS](https://github.com/technobasant/governed-agent/blob/main/MEASUREMENTS.md)
