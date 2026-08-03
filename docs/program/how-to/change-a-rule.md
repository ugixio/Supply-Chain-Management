---
id: how-to-change-a-rule
title: "How to change a rule"
type: how-to
owner: orchestrator
status: active
since: 2026-08-03
updated: 2026-08-03
relations:
  - { type: part-of, target: index-program }
  - { type: governed-by, target: index-adr }
---
# How to change a rule

> **For someone who has decided a rule is wrong, missing or dead.** The law is elsewhere and is not
> restated here: `30-foundation/scm-core/rule.md` for what may be a rule at all,
> `knowledge-architecture.md` §12 for the vocabulary, `00-governance/id-registry.md` for the numbers.
> This is the order of operations, and the four traps this repository has actually fallen into.

## 0. Establish that it is a rule and not a policy

A rule states a **constraint** that something outside this repository fixes. If an organization could
reasonably choose otherwise, it is project policy — name the decision and the standard that bounds
it, and stop. **Seven of thirteen original `SCM-R*` rules failed this test** and were retired by
ADR-0037; the ones that read most convincingly as law were the invented ones.

The second question is *whose* law: a cross-cutting identity is `SCM-R*` or `MSR-R*`, a build-time
constraint is `ENG-R*`, a platform constraint is `PLT-R*`, and anything belonging to one department
goes to that department's `rule.md`. Putting a departmental rule in the foundation is how the same
statement ends up written twice.

## 1. Never edit a rule's meaning in place

A rule ID is a stable citation. Something already cites it, and changing what it says under a
citation that resolves silently is the worst outcome available — worse than a broken link, which at
least fails G4.

- **Sharpening the wording** without changing the constraint: edit in place, restamp `updated:`.
- **Changing the constraint**: **retire the old ID and allocate a new one.** Never reassign.
- **Deleting the constraint**: retire the ID. It stays listed forever.

## 2. Retiring is three edits, and G16 fails if you do two

1. The rule's own file: move it into that file's `## Retired rules` table with the reason.
2. `00-governance/id-registry.md`: add the number to the `retired-roster` fenced block.
3. Every live citation of it: **remove or repoint**. G11 fails a citation of a retired ID.

**G16 asserts the roster equals the union of the retirement tables in both directions**, so it
catches a roster that fell behind *and* a roster claiming a retirement nobody declared. This gate
exists because the registry once enumerated **12 retired rules when 52 were retired**, in grouped
prose that no reader could trust — and forty of them were invisible to an agent reading only the
registry.

## 3. Adding a rule: the number, then the test

Take the next free number in the family from the registry and **record the allocation in the same
commit**. Then:

- **A rule with no test is a suggestion.** `docs/program/WORKFLOW.md` treats a rule ID as testable:
  either a gate enforces it, or a Rust/TypeScript test names it, or the rule says plainly that no
  mechanism enforces it and a human is the only check. **Say which of the three it is.**
- Cite, never restate. If your rule needs an identity that `MSR-R1` already fixes, cite `MSR-R1`.
  ADR-0039 exists because the same arithmetic was being rewritten per department.
- The 1,000-word budget applies to the whole `rule.md`, not to your addition:

      wc -w docs/40-contexts/<NN-dept>/rule.md

## 4. The load-set trap, which has caught four changes

`changing-a-rule` is a **declared load set** (`program/load-sets.md`) and it contains the
id-registry, which grows with every allocation and never shrinks. Allocating your rule can push the
set past its budget and turn G14 red **on correct work**.

**When that happens the number is not the answer.** Each set names the structural exit it takes when
reached; `changing-a-rule`'s is compacting the CPT allocation prose. Take the named exit. This class
has recurred five times, and the fourth time the exit that had been written down turned out to be the
wrong instrument — so if the named exit does not fit, say so and pick a better one, but do not quietly
raise the ceiling.

## 5. Run everything, not just the doc gates

    make verify-full

`verify` alone will not catch a broken rule test or a clippy warning, and `verify-full` adds the gate
mutation tests — which matter here because retiring a rule touches the same files two of the mutants
plant violations in.

## When this is not the guide you want

- **A new concept** rather than a constraint — `how-to/add-a-concept-node.md`.
- **A change that introduces or renames a concept** — that is plan⇄context (ADR-0010): the model, the
  ADR and the rules land *before* any code.
- **Adding a gate** — a gate is not a rule; it is the mechanism that enforces one. It needs a
  `G*` number from the registry §6, an entry in `knowledge-architecture.md` §11, and **its own
  mutant** in `tools/test_gates.py` (ADR-0042). One mutant per *claim*, not per gate: G3 asserts
  three things and carries two mutants because only one of its claims had been planted.
