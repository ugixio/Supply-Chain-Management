---
id: program-concept-template
title: "concept.md Template (one supply-chain calculation per node)"
type: program
owner: orchestrator
status: draft
since: 2026-07-20
updated: 2026-07-20
relations:
  - { type: part-of, target: index-program }
  - { type: governed-by, target: governance-root }
---
# concept.md template

> One **calculation or concept** per node (ADR-0015). Lives at
> `docs/25-concepts/<NN-department>/<slug>.md` with `type: concept` front-matter.
> Allocate the `CPT-NNNN` id in the ID registry §1 in the same commit.
>
> **Authority:** a concept node owns *semantics* — formula, units, assumptions, when the
> method does not apply. It **never restates an invariant**: cite the rule ID and let
> `rule.md` remain the law (knowledge-architecture SSOT).
>
> **Relations:** `part-of` the department concept index · `governed-by: index-adr` ·
> `depends-on` ONLY for true mathematical prerequisites (G6 enforces acyclicity — two
> concepts that merely reference each other must use `traces-to`, not `depends-on`).
>
> **G10:** the `## Implementations` bullets are machine-read. Each bullet must name the
> symbol in backticks inside the link text and point at the file that defines it, or the
> gate fails. Omit the section entirely when nothing implements the concept yet — state
> that under `## Status` instead.
>
> Budget: 700 words (gate G9). Be dense, not long.

```markdown
# <Concept Name> (<CPT-NNNN>)

> One-sentence definition — what it answers, for whom.

## Formula

    <symbolic form>

| Symbol | Meaning | Unit |
|---|---|---|
| <x> | <meaning> | <unit — integer cents, units/day, days, dimensionless> |

## Inputs and outputs

- **Inputs:** <named, with units and admissible ranges>
- **Output:** <what comes back, unit, and its rounding/typing convention>

## Assumptions and limits

- <assumption the formula rests on — e.g. demand is normally distributed>
- **Does not apply when:** <the boundary — e.g. intermittent demand; use CPT-NNNN>

## Worked example

<concrete numbers in, arithmetic shown, number out — must match the implementation>

## Implementations

- TS: [`<symbolName>`](../../../src/departments/<NN-dept>/<path>.ts)
- PY: [`<symbol_name>`](../../../python/<NN_dept>/<path>.py)

## Governing rules

- <DMD-R4> — <one line on how this concept is constrained by that rule>

## Related

- <CPT-NNNN> <Name> — <why it is related>

## References

- <author, work, chapter/equation — the standard or literature lineage>
```
