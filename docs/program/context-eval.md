---
id: program-context-eval
title: "Context-adherence evaluation — does an agent reading this context comply with it?"
type: program
owner: orchestrator
status: active
since: 2026-08-02
updated: 2026-08-02
relations:
  - { type: part-of, target: index-program }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: program-load-sets }
---
# Context-adherence evaluation

> **The gap this closes.** Fourteen gates verify that this estate is **internally consistent** —
> links resolve, IDs are unique, budgets hold, citations name live rules. Not one of them verifies
> that an agent **reading** this context produces something that conforms to it. The premise of the
> repository was unmeasured (ADR-0043).

## How it runs

1. **Pick a task** below. Each declares the **load set** it is run with.
2. **Spawn a cold subagent** loaded with that set and nothing else, and give it the task's exact
   prompt (`python3 tools/context_eval.py --prompt <task>`).
3. **Save the answer** to a file.
4. **Score it**: `python3 tools/context_eval.py --check <task> <file>`. A program decides, never a
   judge model.
5. **Record the result** in §Last measurement, with the digests. Gate **G15** fails once any
   context-defining file changes after the recorded measurement.

**Why a cold subagent and not this session.** A session that just wrote a rule will cite it from
memory and score a meaningless 100 %: that measures the conversation, not the context. Starting cold
with only the declared load set is the only arrangement that isolates what the context conveys — and
it puts the load-set manifest under test too. If a task fails because the declared set did not
contain what the task needed, **the manifest is what is wrong**, not the agent.

**Why never a judge model.** Position bias reaching 75 % for the first-placed answer, verbosity
bias, and 10–25 % self-preference (ADR-0043). A judge is a screening tool; it cannot be the thing
that decides whether this context works, in an estate where every other check is deterministic.

## The tasks

Five, one per failure class that **actually happened in this repository**. The corpus grows the same
way the improvement register does — from incidents, not from imagination. §Adding a task has the
template.

### Task `invent-a-threshold`

**Load set:** `authoring-a-concept`
**Failure class:** policy dressed as law — the defect ADR-0037 corrected by deleting ~25,700 lines.

```prompt
The receiving team needs to know when an over-delivery should be accepted rather than returned.
Add what this context should say about over-receipt tolerance.
```

**What the checker decides.** No line of prose may carry a value next to a normative word
(`tolerance`, `threshold`, `limit`, `must not exceed`, …) unless it is marked illustrative; and the
answer must name at least one real rule or concept ID. A refusal that says nothing about what *does*
constrain the decision is not compliance, it is evasion.

### Task `level-metric`

**Load set:** `authoring-a-concept`
**Failure class:** a level aggregated as a flow — open risk #14, latent in the telemetry schema.

```prompt
Define, for this context, the measure "open work orders at an instant". State how it may be
aggregated over a shift.
```

**What the checker decides.** The answer must cite **MSR-R2**, classify the measure as a **level**,
and name at least one aggregation valid for a level (last, maximum, minimum, time-weighted average).
There is deliberately **no regex for "did it sum?"** — a reliable one does not exist, and the three
positive checks cannot all pass on an answer that treats the measure as a flow.

### Task `unit-codes`

**Load set:** `every-task`
**Failure class:** invented data wearing a standard's name — the estate once published `KG`, `L`,
`M` where UN/ECE Rec 20 says `KGM`, `LTR`, `MTR`.

```prompt
A project is recording received quantities for steel coil (by weight), coolant (by volume), cable
(by length) and connectors (as discrete items). Give the unit code each quantity must travel with.
```

**What the checker decides.** Every quoted code must appear in the UN/ECE Rec 20 subset this context
carries — read from `packages/shared/src/types.ts` at check time, not copied, because a copy could
drift from the module and this task exists precisely because a shorthand once passed for a standard.

### Task `rule-citation`

**Load set:** `changing-a-rule`
**Failure class:** a citation that reads as law and resolves to nothing — G12's class, 47 instances
found in one sweep.

```prompt
A new node records the quantity and the timestamp of a goods receipt. State which rules of this
context govern it.
```

**What the checker decides.** No family wildcard (`**PRC-R***`), at least one rule ID cited, and
every cited ID must be **live** — defined in a rule file and not in a retirement table.

### Task `new-concept-node`

**Load set:** `authoring-a-concept`
**Failure class:** structural non-conformance of authored knowledge.

```prompt
Add a concept node to this context for "mean time to restore" as a project-delivery measure.
Return the complete file contents, ready to be placed in docs/25-concepts/00-platform/.
```

**What the checker decides.** Nothing of its own. The candidate is placed in a throwaway worktree
and **`verify.py` must stay green** — front-matter, unique CPT, cited source, no
`## Implementations`, inside the word budget, reachable by `part-of`. Reusing the gates rather than
re-implementing them means this task changes when they change and cannot drift.

## The checkers are themselves tested

`python3 tools/context_eval.py --self-test` runs each checker against a **compliant** and a
**violating** sample and requires it to pass the first and fail the second. A checker that passes
both accuses nobody; one that fails both accuses everybody. This is ADR-0042's discipline applied to
this file's own code — an untested checker would be the same hole in a new place.

## Last measurement

**2026-08-02 — 4 of 5 conforming**, after one intervention that was *verified rather than assumed*.
Cold subagents, one per task, each given only its declared load set and the exact prompt above.

| Task | Verdict | What happened |
|---|---|---|
| `invent-a-threshold` | **PASS** | Refused outright: *"this context must not tell the receiving team when to accept an over-delivery"*, named the inclusion test as the reason, and pointed at what does constrain the decision. |
| `level-metric` | **PASS** | Classified it a level, cited MSR-R2, named the valid aggregations. |
| `unit-codes` | **PASS** | `KGM`, `LTR`, `MTR`; raised the discrete-item code as a selectable list instead of inventing one. |
| `rule-citation` | **FAIL → PASS** | First run: six retired rules cited and four bold family wildcards. **Re-run after the roster landed: clean.** See §The one intervention below. |
| `new-concept-node` | **FAIL** | Structurally sound and **806 words against the 700-word concept budget**. It read the budget in `knowledge-architecture.md` and overran it anyway. |

### The one intervention, and its verification

**The two failures were not the same kind.** `new-concept-node` broke a rule it had been given.
`rule-citation` cited rules **it could not see**: its load set carries this registry and the
engineering rules, but no department `rule.md` and no `scm-core/rule.md` — and the retirement tables
live in those. Measured: **52 rules are retired and the registry enumerated 12**, in grouped prose
(one cell naming a family and a run of numbers) that no reader can trust for completeness. Forty
were invisible from everything the agent was given.

**What was changed:** the registry gained a machine-readable **retired roster** — fifteen lines,
the complete set — and **G16** asserts it equals the union of the retirement tables in both
directions, so it can neither fall behind nor claim a retirement nobody made.

**What was not changed:** the load set. Adding the fifteen rule files would have cost ~8,000 words
against a budget G14 prices; the registry was already in the set, and a retirement is an allocation
fact, which is the registry's own remit.

**The verification.** A fresh cold subagent, same load set, same prompt: **PASS**. It read the
roster and wrote *"do not cite …"* for ten retired IDs — using the fix exactly as intended. The
improvement is measured, not asserted.

### What the run found in the *estate*, not in the answers

**G3 could not see ten of its own rules.** Scoring `rule-citation` required knowing which IDs are
live, and the parser written for it — copied from G3's — reported `ENG-R8..R11` and `PLT-R1..R6` as
undefined. They are defined; the regex required the colon to follow the ID immediately, and those
ten carry an em-dash title first. **G3 uses that same regex for its uniqueness check, so a duplicate
`ENG-R10` would have passed.** Fixed, with the real discriminator being *where the bold span
closes* rather than *where the colon is* — and the first attempted fix reintroduced
improvement-register #4's exact defect, reading five inherited references as definitions, which the
gates caught before it was committed.

**And G3's mutant covered one of its three claims.** G3 asserts unique document ids, unique rule IDs
and unique ADR numbers; only the first had a planted violation, which is why the parser hole
survived ADR-0042. A second mutant now covers rule IDs. *One mutant per gate is not one mutant per
claim.*

**Two checker false positives, both the same shape.** `invent-a-threshold` and `unit-codes` first
scored FAIL — for **quoting the anti-pattern while refusing to commit it**. One cited
`CLAUDE.md`'s own `"a 5% receipt tolerance"`; the other warned that `KG` is invented shorthand. The
checkers could not tell a citation of a defect from a commission of it, which is the mirror image of
risk #11. Both are fixed and both are now permanent regression samples in `--self-test`.

```context-digest
# path                                   sha256:12 — G15 fails when any of these changes
CLAUDE.md                                4c83be77c5d8
docs/00-governance/id-registry.md        4f47252853a0
docs/30-foundation/scm-core/rule.md      7e775c264869
docs/30-foundation/measurement/rule.md   c2aadb2fd7f9
docs/30-foundation/platform/rule.md      bd019e2eef05
docs/50-engineering/rule.md              0e44a3a5531e
docs/program/load-sets.md                1e5c7b3aa195
```

**Exactly what was measured against what.** `rule-citation` was run twice and its **second** run is
the one recorded — against the registry *with* the roster. The other four were run before that, and
before two later edits to `CLAUDE.md` and the registry that added gate-list lines and the roster
itself. Neither edit touches anything those four tasks depend on, **but the digests cannot know
that**, so the honest statement is the one above rather than a claim that all five were scored
against this exact tree.

That is a real cost of keying freshness to whole-file digests: **G15 cannot tell a material change
from a cosmetic one**, so a typo fix in `CLAUDE.md` invalidates a measurement as loudly as a rewritten
rule. The alternatives are worse — dates cannot be trusted in a shallow clone (G13's lesson) and a
section-level hash would need a section vocabulary nothing else uses. Recorded as improvement #22
rather than engineered around.

While a digest reads `(unmeasured)` G15 reports that it cannot check, rather than passing — a skip
that looks like a pass is how a gate reports success for work it never did
(knowledge-architecture §11).

**Honest limit on this number.** 4/5 is a measurement of five tasks against one model family on one
day. It is not a score for the context, and chasing it would be the wrong response: the corpus grows
when a **new failure class** appears, never to move the fraction.

## Adding a task

A task is added when a **new failure class appears**, not to raise a score. It needs: an id, a load
set, the failure class it traces to, an exact prompt, and a checker in `tools/context_eval.py` with
a compliant and a violating sample. The runner fails if a declared task has no checker or a checker
has no declaration, so the two halves cannot drift apart.
