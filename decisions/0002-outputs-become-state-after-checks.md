# 0002. A model's output becomes state only after a schema, a policy, a grounding check and, for side effects, a person

- Status: Accepted
- Date: 2026-10-18
- Evidence: agent_answer_match, agent_published_wrong

## Context

A model's answer that is shown to a customer, written to a table or sent as a message has become state. A wrong answer that was only displayed costs trust; a wrong action costs more. Accuracy measured on average says nothing about which wrong answers reached someone.

## Decision

- Every output is typed: a schema the answer must validate against.
- Answers that quote numbers are checked deterministically against the tool results they claim to come from; a model does not judge another model's answer at publication time.
- Outputs that fail a check, or that carry a proposed action, go to a review queue. Only those that pass every check publish automatically.
- Approved actions execute through an outbox, at most once, with an idempotency key.
- What matters is measured: not only how many answers are right, but how many wrong ones published themselves.

## Consequences

- The agent matched an answer key computed by SQL on 48 of 54 questions.
- Of 37 answers that passed every check and published without review, 3 were wrong. That is the number the next change to the checks has to bring down, and the reason auto-publication is a policy per feature, not a default.
- Review is a queue to staff. The checks decide its size.

## Alternatives considered

- **Publish everything, sample for quality.** Cheaper; the wrong answers are found by customers.
- **Review everything.** Safe, and the feature saves no time.
- **An LLM judge at publication time.** Another probabilistic component on the critical path; see [0005](0005-judges-are-instruments.md) for where judges belong.

## Evidence

<!-- evidence:start -->
- **48/54** answers matched an answer key computed by SQL. One live run of a 54-question golden set against qwen3:8b under Ollama, temperature 0, thinking off, over a seeded synthetic warehouse; 95% CI 78–95%. Source: [governed-agent/MEASUREMENTS.md](https://github.com/technobasant/governed-agent/blob/main/MEASUREMENTS.md)
- **3 of 37** answers published without review were wrong. Same run; a finding is published only after its schema, policy and grounding checks pass with no proposal attached; 95% Wilson interval on 3/37 is 3–21%. Source: [governed-agent/MEASUREMENTS.md](https://github.com/technobasant/governed-agent/blob/main/MEASUREMENTS.md)
<!-- evidence:end -->

## Related decisions in the labs

- governed-agent [0003 A deterministic grounding check, not a model judging the answer](https://github.com/technobasant/governed-agent/blob/main/docs/adr/0003-grounding-check-not-a-judge.md), [0004 Nothing with a side effect runs without approval](https://github.com/technobasant/governed-agent/blob/main/docs/adr/0004-review-before-execute.md), [0005 Approved actions go through an outbox](https://github.com/technobasant/governed-agent/blob/main/docs/adr/0005-outbox-and-idempotency.md)
