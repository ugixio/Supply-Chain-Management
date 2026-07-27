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
> **G10 (rewritten by ADR-0037):** a node must claim a **unique CPT number** in its title, carry a
> **non-empty `## References`**, and carry **no `## Implementations`** section at all. The gate no
> longer maps concepts to code — there is no application here to map to, and a link into a
> project's code would invert the one-way rule (ADR-0024).
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

## Project-chosen inputs

> Every value an organization decides. Name the decision and **why it is the project's**, then
> stop — supplying a "sensible default" here is how one company's policy becomes every project's
> inheritance (ADR-0037). Omit the section only where the concept is a pure identity with no free
> parameter (a conservation law, a sum, a ratio of two given quantities).

| Input | Why the project must choose it |
|---|---|
| <the parameter or the choice> | <what it follows from — a contract, a service commitment, a cost of capital; never a value> |

A second row usually exists and is easy to miss: the **population, period or basis** the concept is
computed over. Two teams computing the same formula over different denominators disagree while both
being right.

## Worked example

<concrete numbers in, arithmetic shown, number out. Numbers here are **illustrative**: label them
so a reader cannot mistake an example input for a recommended value.>

## Governing rules

- <RULE-ID> — <one line on how this concept is constrained by that rule>

> Cite a **live** ID. G11 fails the build on a citation of a retired rule, since a retired ID is
> never reassigned and resolves to nothing.

## Related

- <CPT-NNNN> <Name> — <why it is related>

## References

> **Required and non-empty (G10).** Name the standards body, regulation or identity that fixes
> this concept. A node that cannot cite one does not belong in the context. **Do not add an
> `## Implementations` section** — G10 rejects it: the context defines concepts, projects own
> their code (ADR-0037).

- <author, work, chapter/equation — the standard or literature lineage>
```
