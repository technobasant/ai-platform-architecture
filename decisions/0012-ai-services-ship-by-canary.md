# 0012. AI services ship by canary like every other service, after the evaluation gate

- Status: Accepted
- Date: 2026-10-18
- Evidence: deploy_bad_release_aborted, deploy_good_release_failures

## Context

An evaluation gate tests behaviour on a fixed set of cases. It does not test the deployment: configuration, dependencies, latency under real traffic, error rates.

## Decision

- An AI service passes the evaluation gate in CI, then deploys by GitOps with a canary judged against the stable version's latency and error rate.
- The canary needs a minimum number of real requests before it can be promoted.

## Consequences

- Six of six bad releases of the governed agent's API were aborted by the canary analysis; across three good releases, 0 of 18,003 requests failed.
- Quality regressions that only show on live traffic still need outcome monitoring ([0010](0010-promote-on-outcomes.md)).

## Alternatives considered

- **Treat the evaluation gate as the release gate.** It never sees production traffic.

## Evidence

<!-- evidence:start -->
- **6 of 6** bad releases aborted by canary analysis. A release whose Envoy sidecar returns 500 on 30% of requests, under 20 req/s from k6; three runs with keep-alive clients, three with a new connection per request; Prometheus analysis every 15 s after a 30 s initial delay. Source: [platform-deployments/MEASUREMENTS.md](https://github.com/technobasant/platform-deployments/blob/main/MEASUREMENTS.md)
- **0 of 18,003** requests failed across three good canary releases. K6 at 20 req/s for five minutes per run, GET /healthz and GET /review-queue with a 10 s timeout; canary 20% → 50% with 60 s pauses, background analysis and an evidence step before 100%. Source: [platform-deployments/MEASUREMENTS.md](https://github.com/technobasant/platform-deployments/blob/main/MEASUREMENTS.md)
<!-- evidence:end -->

## Related decisions in the labs

- platform-deployments [0002 Argo Rollouts canary with Prometheus analysis](https://github.com/technobasant/platform-deployments/blob/main/docs/adr/0002-rollouts-canary-with-analysis.md)
