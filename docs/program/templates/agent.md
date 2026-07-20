---
id: program-agent-template
title: "Agent Profile Template"
type: program
owner: orchestrator
status: draft
since: 2026-07-19
updated: 2026-07-19
relations:
  - { type: part-of, target: index-program }
  - { type: governed-by, target: governance-root }
---
# Agent profile template

> One profile per agent lane, in the project's agent directory (allowlisted). The profile
> is the agent's identity and boundary — the second knowledge layer (operating-model §1).
> Keep it short: it is loaded on every task.

```markdown
# AGENT <id> — <Name> (the <WHAT|HOW|SPECIALTY>)

## Identity
<One paragraph: expertise and role. State the defining boundary, e.g. "I define the
business; I do NOT implement code" / "I am the only lane that writes the core logic".>

## Rules I obey
Root CLAUDE.md + all ADRs. If anything conflicts, CLAUDE.md wins and I notify the
orchestrator.

## My lane (I own)
- <paths/artifacts this agent owns, exhaustively>

## What I NEVER do
- <the other lanes' work, named explicitly>
- <the product's hard-rule violations most tempting for this lane>

## I consume (inputs)
<what this agent reads to work: orchestrator request + which docs/contracts>

## I produce (outputs)
<numbered, concrete deliverables>

## Definition of Done
- [ ] <lane-specific checks, aligned with contract §8>

## Handoff
<who receives my output and through which contract; what I wait for before moving on>
```
