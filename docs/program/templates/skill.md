---
id: program-skill-template
title: "skill.md Template (know-how per area)"
type: program
owner: orchestrator
status: draft
since: 2026-07-19
updated: 2026-07-19
relations:
  - { type: part-of, target: index-program }
  - { type: governed-by, target: governance-root }
---
# skill.md template

> The area's **know-how**: what an agent needs to work competently in this area without
> loading the whole repo. Lives next to the area's `rule.md` with `type: skill`
> front-matter. Advisory (Tier 6) — anything normative goes to `rule.md`. Creating a new
> skill requires the orchestrator's authorization with a cited justification.

```markdown
# Skill — <Area Name>

## Area identity
Domain area: <where this sits in the product model>
Units it contains: <keys>

## Purpose in the product
<What this area solves; what depends on it.>

## Domain knowledge (know-how)
<Key processes, concepts and terminology — the things an expert in this area knows that
the code alone does not teach. Concrete: quantities, states, flows, edge conventions.>

## How this part is built
- Domain entities: <…>
- Main use cases: <…>
- Invariants to respect: see rule.md (<CTX>-R1…)
- Capabilities: provides <…> | consumes <…>
- Events: publishes <…> | subscribes <…>

## References
Relevant decisions · this area's specs · related areas (by id).
```
