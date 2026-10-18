# 0001. AI features reach data only through typed tools behind one boundary

- Status: Accepted
- Date: 2026-10-18
- Evidence: agent_injection_actions

## Context

An agent that can run arbitrary SQL, call arbitrary APIs or read arbitrary files inherits every permission of the credentials it holds, and it reads untrusted text (questions, documents, tool results) that can contain instructions. Prompts cannot be the security boundary, because the model decides how to read them.

## Decision

- Models reach data only through a small set of typed tools exposed over one protocol boundary (MCP). Each tool has a schema, runs under the caller's permissions, and returns structured results.
- Read tools query governed views, never raw tables; SQL a model writes is parsed and checked against an allow-list of statements and tables before it runs.
- Tools that change state do not execute: they return a proposal, which goes to review ([0002](0002-outputs-become-state-after-checks.md)).
- Instructions found inside data are surfaced to the reviewer as a caveat, not obeyed.

## Consequences

- Five planted instructions in the data led to 0 proposed actions.
- New capabilities are new tools with schemas and tests, not new prompt text.
- The boundary adds a hop and a schema to maintain for every capability.

## Alternatives considered

- **Give the agent a database connection.** Fastest to build; the model's judgment becomes the access control.
- **Guard with prompt instructions.** Untestable as a control; a model that follows instructions can follow the wrong ones.

## Evidence

<!-- evidence:start -->
- **0 of 5** planted instructions that led to a proposed action. Five questions that make the model read instructions planted in product descriptions and refund notes; actions can only be proposed, and execute after a named person approves. Source: [governed-agent/MEASUREMENTS.md](https://github.com/technobasant/governed-agent/blob/main/MEASUREMENTS.md)
<!-- evidence:end -->

## Related decisions in the labs

- governed-agent [0002 MCP is the boundary between the agent and the data](https://github.com/technobasant/governed-agent/blob/main/docs/adr/0002-mcp-is-the-boundary.md), [0001 The agent is an explicit graph, not a loop](https://github.com/technobasant/governed-agent/blob/main/docs/adr/0001-explicit-graph-not-a-loop.md)
