---
id: program-adr-template
title: "ADR Template"
type: program
owner: orchestrator
status: draft
since: 2026-07-19
updated: 2026-07-19
relations:
  - { type: part-of, target: index-program }
  - { type: governed-by, target: governance-root }
---
# ADR template

> Allocate the number in `00-governance/id-registry.md` §3 first. Append the ADR to
> `docs/10-decisions/README.md` (or as its own file if extensive). Once accepted, the body
> is frozen: changes come only as a superseding ADR.

```markdown
## ADR-NNNN — <Title: the decision as a statement>

**Status:** Proposed | Accepted | Accepted (retroactive) | Superseded by ADR-XXXX | Deprecated
**Extends / Supersedes:** <ADR links, or "nothing">

**Context:** <The forces: what problem exists, why now, what constraints apply. Written so
a newcomer understands why this needed deciding.>

**Decision:** <What was decided, in active voice, concrete enough to be checkable. Include
the rules the decision imposes.>

**Consequences:**
- (+) <benefit>
- (−) <cost — every real decision has one; name it and say it is accepted>

**Alternatives considered:** <Each rejected option WITH the reason it lost. This is what
prevents relitigating the decision later.>
```
