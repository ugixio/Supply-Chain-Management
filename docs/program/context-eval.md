---
id: program-context-eval
title: "Context-adherence evaluation — does an agent reading this context comply with it?"
type: program
owner: orchestrator
status: active
since: 2026-08-02
updated: 2026-08-03
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

Six, one per failure class that **actually happened in this repository**. The corpus grows the same
way the improvement register does — from incidents, not from imagination. §Adding a task has the
template.

### Task `what-is-this-for`

**Load set:** `every-task`
**Failure class:** the purpose is unreadable — every other task checks whether an agent *obeys* the
context; none checked whether it can say what the context is **for**.

```prompt
In your own words: what is this repository for, and who uses it?
```

**Why this task exists, and it is the newest.** The owner asked for a plain summary of the project
and the answer exposed the weakest thing in the estate: the entry point named a supply-chain
knowledge base *and* a DevOps monitoring application and **never connected them**. A reader could
follow every rule here and still not know why a knowledge repository ships a dashboard. The fix was a
purpose section in `CLAUDE.md` (ADR-0045); **this task is what stops it degrading again**, because
prose with nothing checking it drifts back.

**What the checker decides.** Four claims by presence of *any* term from a set — a comprehension
check, not a recitation check. The answer must name **both axes** (company operating discipline and
engineering practice), name the **portfolio of projects**, and **connect monitoring to those
projects on a single line** — mentioning both separately is exactly the gap. And it must **not**
conclude that this is a supply-chain application, which is what ADR-0037 deleted 25,700 lines to stop
being true.

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

**Load set:** `recording-a-quantity`
**Failure class:** invented data wearing a standard's name — the estate once published `KG`, `L`,
`M` where UN/ECE Rec 20 says `KGM`, `LTR`, `MTR`.

```prompt
A project is recording received quantities for steel coil (by weight), coolant (by volume), cable
(by length) and connectors (as discrete items). Give the unit code each quantity must travel with.
End your answer with a fenced block, opened with three backticks and the word `answer`, holding one
`quantity: CODE` line per quantity — and no line for a quantity whose code this context does not
carry. Only that block is scored; explain, quote and warn freely outside it.
```

**What the checker decides.** Every code **declared in the answer block** must appear in the UN/ECE
Rec 20 subset this context carries — read from `packages/shared/src/types.ts` at check time, not
copied, because a copy could drift from the module and this task exists precisely because a shorthand
once passed for a standard. Prose is not read at all.

**The block replaced a prose heuristic, and this task is why the heuristic is gone.** It used to
score every quoted token on any line that did not *disown* it. On 2026-08-03 a correct answer failed
on all four codes: it gave `KGM`, `LTR`, `MTR`, quoted `CLAUDE.md`'s anti-pattern (which spells out
`KG`, `L`, `M`), and named `PCE` only to refuse to assert it — and wrapped prose had put every
disowning word on a different line from its token. That was the **sixth** occurrence of a class the
register had already set a threshold for, so the instrument changed rather than the regex widening
again. **Its load set changed in the same breath:** the task was declared against `every-task`, which
carries no code list — three of the four codes appear there only as an anti-pattern illustration and
the fourth nowhere at all. Two runs answered as well as that set allows, and the second was scored a
failure for it.

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
Use CPT-0999 as its number, and make it reachable by a part-of relation to `index-concepts-00-platform`.
```

> **The last two sentences were added on 2026-08-03**, after the task had been run twice. They state
> facts a session would normally get from the registry and the department index, neither of which is
> in this load set — so without them the answer's placement is a guess and two runs are not
> comparable. The first run solved both correctly anyway and failed only on word count; the addition
> removes a variable rather than removing a difficulty.
>
> **The number is `CPT-0999`, reserved in the ID registry and never allocated.** The first version of
> this prompt said `CPT-0167`, which was free that morning and was allocated to a real node the same
> afternoon — after which this task would have failed on a duplicate CPT, a spurious failure in the
> one place the estate measures itself. A task that names an identifier must name a reserved one.

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

**2026-08-03, second cycle — 6 of 6 conforming.** Re-run in full because M2b changed `CLAUDE.md`,
the id-registry and the load-set manifest, and G15 was right to red: a measurement is about the
context it was taken against. All six were run fresh against **this** tree — one cold subagent each,
given its declared load set and nothing else, and the exact prompt above.

| Task | Verdict | What happened |
|---|---|---|
| `what-is-this-for` | **PASS** | Named both axes, the portfolio, and tied monitoring to the projects it watches — from the three always-loaded files. |
| `invent-a-threshold` | **PASS** | Refused to state a tolerance, named the inclusion test as the reason, and cited what does constrain the decision. |
| `level-metric` | **PASS** | Classified it a level, cited MSR-R2, named the valid aggregations. |
| `unit-codes` | **FAIL → PASS** | **The one regression of this cycle, and the answer was right.** Scored against `every-task`, a correct answer failed on all four codes; the checker and the task's load set both changed, and the re-run declared `KGM` · `LTR` · `MTR` · `EA`. See §The regression below. |
| `rule-citation` | **PASS**, twice | Cited SCM-R9 and SCM-R10, and wrote off the retired IDs by name using the roster. **Re-run the same day** when `how-to/change-a-rule.md` joined its load set: adding a member changes what the subject reads, so the earlier score no longer described its input. Clean again. |
| `new-concept-node` | **PASS** | Inside the 700-word budget, source cited, no `## Implementations`; `verify.py` stayed green with the candidate in place. |

### The regression, and what it cost to diagnose honestly

Two things were wrong and only one of them was visible.

**The checker.** It scored every quoted `[A-Z]{1,4}` token on any line that did not *disown* it. The
answer gave `KGM`, `LTR`, `MTR`, quoted `CLAUDE.md`'s anti-pattern — which spells out `KG`, `L`, `M`
— and named `PCE` only to say it would not assert it. All four were counted as used, because wrapped
prose put every disowning word on a **different line** from its token. That was the **sixth**
occurrence of this class, and improvement #22 had already written the threshold down: at the sixth
widening the line-level regex is the wrong instrument. So the instrument changed. The task now asks
for its conclusion in a fenced `answer` block, one `quantity: CODE` line each, and **only that block
is scored** — the same move G17 makes, giving a claim a structure instead of inferring it from
sentences. The failing answer is now a permanent `--self-test` sample.

**The load set, which is the finding that matters.** `unit-codes` was declared against `every-task`.
That set carries **no code list**: `KGM`, `LTR` and `MTR` appear there only as an illustration inside
an anti-pattern bullet, and the code for a discrete item appears nowhere at all. Two separate runs
answered as well as that set allows — the first raised the fourth code as an open question, the
second named `PCE` and refused to assert it — and both were the *correct* behaviour of an agent that
had not been given the answer. The previous cycle recorded this as a PASS, which was luck.
**A task can only be scored against a set that can answer it**, and ADR-0043 says that when the
declared set is missing something the task needs, the manifest is what is wrong. A new set,
`recording-a-quantity`, adds `docs/standards/REGULATORY_FRAMEWORK.md`, whose code table carries all
four. Re-run: all four correct, `EA` included.

This is improvement #21's rule paying for itself a second time — **when an agent gets something
wrong, ask what it was given before asking what it did** — and it is worth noting that the rule was
nearly not applied, because a red gate invites fixing the checker and stopping there.

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

### The second intervention, and an honest confound

`new-concept-node` failed on the one thing the context states plainly and the agent still got wrong:
**the 700-word budget, read and overrun.** Nothing was missing from its load set — the number was in
front of it. What was missing was a **form**: against the Diátaxis four the estate had *reference*
(182 concept nodes, 20 rule files) and *explanation* (the ADRs) and **no task-oriented document at
all**, while `CLAUDE.md` promises a project can learn "which departments it needs *and how to
implement them*".

`program/how-to/add-a-concept-node.md` is that form (ADR-0044), and it makes the budget operational
instead of stated: *count while writing, here is the command, trim the node rather than the budget,
and here is what to cut first.* **Re-run: 633 words**, and the answer named the budget in its own
report.

**The confound, stated because the number is worthless without it.** Two things changed between the
runs, not one: the guide was added to the load set **and** the prompt gained the CPT number and the
`part-of` target. The first run had solved both of those correctly on its own and failed *only* on
word count, so the addition removed a variable rather than a difficulty — but the two runs are not
identical and this is not a controlled experiment. What is solid: the failing dimension moved
806 → 633 and the answer explained why.

**A third thing was wrong and it was the instrument.** The first re-run scored FAIL on G15 reporting
that the *measurement record* was stale — true, and nothing to do with the candidate node. The check
delegated to the whole gate suite and inherited every verdict it reached. It now attributes only
failures that name the candidate file, which still catches cross-file verdicts that genuinely
implicate it (G10's duplicate-CPT message names both).

### What the first run found in the *estate*, not in the answers

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
# path                                        sha256:12 — G15 fails when any of these changes
CLAUDE.md                                     ec95648042d5
docs/_index.md                                53f2766c9d3f
docs/program/evaluation.md                    6e806b7f4e29
docs/00-governance/knowledge-architecture.md  3706e4bb0421
docs/00-governance/id-registry.md             bcc09beca388
docs/30-foundation/scm-core/rule.md           7e775c264869
docs/30-foundation/measurement/rule.md        c2aadb2fd7f9
docs/30-foundation/platform/rule.md           0268bef446f1
docs/50-engineering/rule.md                   0e44a3a5531e
docs/50-engineering/practice-areas.md         318d1ff3932e
docs/standards/REGULATORY_FRAMEWORK.md        f1f47f8501ae
docs/program/load-sets.md                     1850bc3adb60
docs/program/how-to/add-a-concept-node.md     6341e78e7551
docs/program/templates/concept.md             09d066c2e4ab
```

**The watched set grew from nine files to fourteen**, and deliberately in the direction of more false
alarms. Every file in a task's declared load set is now listed: `docs/_index.md`, `evaluation.md`,
`knowledge-architecture.md` and `templates/concept.md` were being *read by the subject* while nothing
recorded which version, and `REGULATORY_FRAMEWORK.md` joined with the new load set. The cost is that
a cosmetic edit to any of the fourteen reddens G15; the recorded decision (below) is to prefer the
false alarm to an unverifiable claim, and this is that decision applied rather than restated.

**Exactly what was measured against what.** All six tasks were run against the tree these digests
describe, with one exception stated plainly: `unit-codes` was run twice, and the **second** run — the
one recorded — was scored against the corrected load set and the corrected checker. Its first run is
not discarded; it is the reason both changed, and it is preserved as a `--self-test` sample.

Unlike the first cycle, no task here was scored against a state of the tree that a later edit moved.
That is not a claim of discipline: it is what happens when the whole cycle is re-run instead of
patched, which is the only thing the digests can actually certify.

**One later edit did move the tree, and it was answered rather than argued away.** Two how-to guides
landed after this cycle closed, and one of them — `change-a-rule.md` — was added to the
`changing-a-rule` load set, which is `rule-citation`'s. A new member is a **material** change: it
alters what the cold subagent reads. So that one task was re-run and passed again. The other five read
nothing that moved; their digests are unchanged and their scores stand. G15 could not have told those
two cases apart, which is why the distinction is written here and not left to the gate.

That is a real cost of keying freshness to whole-file digests: **G15 cannot tell a material change
from a cosmetic one**, so a typo fix in `CLAUDE.md` invalidates a measurement as loudly as a rewritten
rule. The alternatives are worse — dates cannot be trusted in a shallow clone (G13's lesson) and a
section-level hash would need a section vocabulary nothing else uses. Recorded as improvement #22
rather than engineered around.

While a digest reads `(unmeasured)` G15 reports that it cannot check, rather than passing — a skip
that looks like a pass is how a gate reports success for work it never did
(knowledge-architecture §11).

**Honest limit on this number.** 6/6 is a measurement of six tasks against one model family, on two days, with the corpus
authored by the same process it evaluates. It is not a score for the context, and chasing it would be the wrong response: the corpus grows
when a **new failure class** appears, never to move the fraction.

## Adding a task

A task is added when a **new failure class appears**, not to raise a score. It needs: an id, a load
set, the failure class it traces to, an exact prompt, and a checker in `tools/context_eval.py` with
a compliant and a violating sample. The runner fails if a declared task has no checker or a checker
has no declaration, so the two halves cannot drift apart.
