---
id: program-load-sets
title: "Load Sets — what an AI reads together, and how much that is"
type: program
owner: orchestrator
status: active
since: 2026-08-02
updated: 2026-08-03
relations:
  - { type: part-of, target: index-program }
  - { type: governed-by, target: index-adr }
---
# Load sets — what an AI reads together, and how much that is

> **The gap this closes.** G9 budgets documents **one at a time** — 700 words for a concept, 1,000
> for a rule, 2,600 for `CLAUDE.md`. Nothing has ever measured **what gets loaded together**, which
> is the quantity the evidence says degrades a model's use of its context (ADR-0041). A session can
> read fifteen individually-compliant documents and be far past the point where the middle of the
> window stops being used.
>
> **G14** reads the manifest below, sums each set, and fails over budget. The measured totals are
> printed on every run, so the number is visible rather than discovered.

## The manifest

Each set names a **budget in words** and the files a session actually opens for that kind of task.
A member may be a literal path, a glob, or **`path#selector`** naming a *slice* of a file. Missing
members fail the gate, and so does an unimplemented selector — a manifest that silently prices the
wrong thing is worse than one that names a file it cannot find.

One selector exists, `adr-index`, and it is not a general mechanism. It prices the
one-line-per-decision entries of the ADR index and **not** the decision bodies, because that is how
the file is read: the entries are scanned and a body is looked up by ID when it is needed. The
difference is **1,950 words against 20,200**.

**Every set is a ratchet or a ceiling, and which one is not a matter of taste.** A set whose members
are all bounded documents gets a **ratchet** a few percent above measurement, so nothing grows
quietly. A set containing an **append-only** document — the ADR index, the improvement register, the
risk register, all of which grow monotonically by design and never shrink — gets a **ceiling with a
structural answer attached**, because a ratchet over a monotonic quantity schedules a false alarm
and a gate that reddens correct work gets disabled rather than obeyed. The classification is stated
per set below and it is the first thing to get right when adding one.

**Ask it of *sections*, not of documents — and the answer is that every set is a ceiling.** The test
was applied three times as "does this set contain an append-only *file*", and each time it missed the
one member every set has: `CLAUDE.md`, whose **gate roster is append-only**. Gate IDs are fixed and
new gates append (id-registry §6); a retired gate would stay listed exactly as a retired rule does.
So adding G17 pushed `every-task` past a ratchet that had one word of headroom, on a change that was
entirely correct — the fifth appearance of this class, and the first one the *rule* caught instead of
the gate catching it by surprise. **Both remaining ratchets are now ceilings**, and the general form
is worth more than the two reclassifications: a set is a ceiling if **any part of any member** grows
by design, and a roster of identifiers inside an otherwise bounded document is such a part.

```load-sets
# Recording a quantity against a standard: which unit code, which identifier, which instant.
# CEILING — CLAUDE.md's gate roster, and the regulatory reference carries a verified-on date per
# entry that grows as entries are re-verified (risk #12). When 4300 is reached the answer is a
# slice selector over the reference's code tables, the same treatment `planning` gives the ADR index.
#   This set exists because the `unit-codes` evaluation task was declared against `every-task`, which
# carries no code list at all: the three codes the task needs appear there only as an illustration
# inside an anti-pattern bullet, and the fourth appears nowhere. Two runs answered honestly and one
# of them was scored as a failure. **A task can only be scored against a set that can answer it**,
# and the set — not the answer — was what was wrong (ADR-0043).
recording-a-quantity = 4300
  CLAUDE.md
  docs/_index.md
  docs/standards/REGULATORY_FRAMEWORK.md

# CEILING — contains CLAUDE.md, whose gate roster appends a line per gate and never removes one.
# Held at a ratchet until 2026-08-03, when adding G17 put it 10 words over with correct work.
# When 3400 is reached the answer is compressing that roster to gate names only: the one-line
# descriptions are already carried in full by knowledge-architecture.md §11, so the entry point can
# cite the section instead of duplicating it. Do not raise this; do not trim prose that earns its
# place to make room for a roster that has a better home.
every-task = 3400
  CLAUDE.md
  docs/_index.md
  docs/program/evaluation.md

# "What should I do next?" — the state of the estate plus the decisions behind it.
# CEILING — contains WORKFLOW.md and the ADR index lines, both append-only by design. The ADR
# member is a SLICE: the one-line entries are scanned, a decision body is looked up by ID when it
# is needed, and only the entries are priced. When 20000 is reached the answer is that the
# "one-line" entries have grown into paragraphs — shorten them; do not raise this.
planning = 20000
  CLAUDE.md
  docs/_index.md
  docs/program/evaluation.md
  docs/program/WORKFLOW.md
  docs/10-decisions/README.md#adr-index

# CEILING — contains CLAUDE.md (its gate roster) and knowledge-architecture.md (the same roster in
# full), both append-only in the part that matters. When 8200 is reached the answer is the same one
# `every-task` names, taken in the other direction: §11 keeps the descriptions, CLAUDE.md keeps only
# the names, and this set pays for one copy instead of two.
authoring-a-concept = 8200
  CLAUDE.md
  docs/_index.md
  docs/program/evaluation.md
  docs/00-governance/knowledge-architecture.md
  docs/program/how-to/add-a-concept-node.md
  docs/program/templates/concept.md
  docs/30-foundation/scm-core/rule.md
  docs/30-foundation/measurement/rule.md

# CEILING — contains the id-registry, which grows monotonically: every allocation appends to it and
# nothing is ever removed. A ratchet here went 157 words over on the commit that allocated PLT-R7 and
# CPT-0167 — the third time this class was met, and the classification rule exists because of it.
# When 10000 is reached the answer is compacting the CPT allocation prose (one paragraph currently
# lists every range in words), not another raise.
changing-a-rule = 10000
  CLAUDE.md
  docs/_index.md
  docs/program/evaluation.md
  docs/program/how-to/change-a-rule.md
  docs/00-governance/knowledge-architecture.md
  docs/00-governance/id-registry.md
  docs/50-engineering/rule.md

# CEILING — contains the risk register, which is append-only (a closed risk stays listed so old
# references resolve). REACHED TWICE. First on 2026-08-03 at 12,069 words: the declared exit was
# taken rather than re-argued — eight closed risk rows moved to risk-register-archive.md, nothing
# deleted, back to 11,523. Reached AGAIN the same day at 12,275, and the exit named for that
# occurrence (archive the improvement register's `done` rows) turned out to be the wrong instrument:
# every remaining closed row carries a live review trigger, and filing away a live warning to satisfy
# a word count inverts what the budget is for. So the set changed shape instead. The improvement
# register LEFT the set: it is the *record* of incidents, its distillation into decision rules now
# lives in known-pitfalls.md (a document review-protocol.md already pointed at and which did not
# exist). 12,275 → 7,004 — the same fix as `planning`'s slice, applied to a document instead of a
# file range: load the unit that is actually read.
#   The pitfall list was FIRST appended to evaluation.md, which was already a member — and that broke
# `every-task`, `authoring-a-concept` and `changing-a-rule`, because evaluation.md belongs to four
# sets. G14 caught it immediately, which is the second time this gate has priced a placement decision
# the author had not thought of as one. Hence its own file, in this set only.
# The next exit, when 12000 is reached again: the pitfall list is the thing that will have grown, and
# a pitfall whose enforcement is a gate can be dropped to a citation of that gate.
reviewing-the-estate = 12000
  CLAUDE.md
  docs/_index.md
  docs/program/evaluation.md
  docs/program/review-protocol.md
  docs/program/known-pitfalls.md
  docs/00-governance/risk-register.md
```

## What the numbers say today

Measured 2026-08-03. **Every set is a ceiling** — see the section test above.

| Set | Words | ≈ Tokens | Budget |
|---|---|---|---|
| `every-task` | 3,210 | 4,269 | 3,400 |
| `reviewing-the-estate` | 7,004 | 9,315 | 12,000 |
| `authoring-a-concept` | 7,724 | 10,273 | 8,200 |
| `changing-a-rule` | 8,267 | 10,995 | 10,000 |
| **`planning`** | **18,993** | **25,260** | 20,000 |

The gate prints these on every run, so the table is a snapshot for reading, never the source of
truth — and it is the one place in this file that can go stale without anything failing.

**`planning` was 35,453 words and is 17,409 — halved without moving a file.** The whole difference is
the `adr-index` slice: the ADR file is 20,200 words, of which 1,950 are the entries a planning
session actually scans. Neither it nor `WORKFLOW.md` carries a G9 budget, because G9 budgets by
`type` and none exists for `adr` or `program`, so the two largest documents in the repository were
the two `CLAUDE.md` instructs a session to load on every planning task — and pricing the *unit that
is read* rather than the file it sits in was the whole fix.

**The gate caught the same mistake five times, which is how the ratchet/ceiling distinction got made
— and only the last one was caught by the rule rather than by the gate.**

- **First**, on the commit that introduced G14: `planning` measured 32,009 and the budget was set at
  33,000 as a ratchet. Writing the two ADRs that adopt G14 and the mutation harness added 1,674
  words to the ADR index and the gate went red. The change was right; the ratchet was wrong.
- **Then again, one commit later**, on `reviewing-the-estate` — 21 words over, from adding a single
  lesson to the improvement register. The lesson being added *was* the first occurrence. **Recording
  a lesson is not applying it** (improvement #15's point, demonstrated on itself), and the fix is
  not a bigger number: it is classifying every set as ratchet or ceiling by asking whether any
  member grows monotonically by design.
- **And a third time, on `changing-a-rule`** — 157 words over, from allocating PLT-R7 and CPT-0167 in
  the id-registry, which grows with every allocation and never shrinks. The classification rule was
  already written when this happened; **it had been written and not applied to the sets that already
  existed**, which is improvement #15's lesson for the third time in the same file.

- **A fourth time, on `reviewing-the-estate` again**, hours after its exit had been taken — and the
  exit named for the *next* occurrence turned out to be the wrong instrument. Every remaining closed
  risk row carries a live review trigger, so archiving one to save words would have filed away a live
  warning. The set changed shape instead: the improvement register left it, and the pitfall list it
  distils to took its place. **A declared exit is a hypothesis about the next breach, and it can be
  wrong; what it must never be is a raise nobody argued for.**
- **A fifth time, on `every-task`** — 10 words over, from adding G17 to `CLAUDE.md`'s gate roster.
  This is the first occurrence the *rule* caught rather than the gate: the roster is append-only, so
  the set was never a ratchet, and asking the classification question of **sections** rather than
  files is what the previous four sweeps had all missed.

Every ceiling carries a structural answer, not just headroom — and `planning`'s changed.

**Splitting the ADR bodies into files was the obvious answer and the owner rejected it** (backlog
X3): the index is to keep working by index search, because splitting would collide with planned work.
That ruling is what produced the slice, and the slice is better than the split would have been —
nothing moved, no forty-three new documents to keep reachable, and the priced unit is now the one a
session really loads.

So `planning`'s exit is different: at 20,000 the finding will be that the **"one-line" entries have
grown into paragraphs** — they average 45 words today, which is a paragraph by any reading. Shorten
them.

**`reviewing-the-estate` reached its ceiling on 2026-08-03, and the exit was taken.** Eight closed
risk rows moved to `risk-register-archive.md` — nothing deleted, because the register's own rule is
that a closed risk stays listed so old references resolve. 12,069 → 11,523. Worth recording that the
temptation was to add a thousand to the number, which would have been the fourth instance of a rule
written and not applied (improvement #28); the point of declaring an exit in advance is that the exit
is cheaper to take than to re-argue.

## What this does not claim

- **It does not measure tokens.** Words × 1.33 is the approximation ADR-0012 already uses for G9.
  A real tokenizer would be more accurate and would add a dependency to a lane that has none.
- **It does not know what a session actually read.** The manifest is a declaration of intent. It
  binds the *instructions* — if `CLAUDE.md` or `WORKFLOW.md` tells a session to read something, it
  belongs in a set here, and G14 then prices it.
- **It sets no target for model behaviour.** The evidence in ADR-0041 says degradation is
  continuous and begins early; it does not fix a safe number, and no standards body does either.
  The budget is this repository's own engineering decision, in the same category as G9's.
