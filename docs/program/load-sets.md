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

```load-sets
# RATCHET — all members bounded.
# Loaded before anything else, every single task.
every-task = 3200
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

# RATCHET — all members bounded.
# Adding or changing a concept node.
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
  docs/00-governance/knowledge-architecture.md
  docs/00-governance/id-registry.md
  docs/50-engineering/rule.md

# CEILING — contains the improvement register AND the risk register, both append-only (closed risks
# stay listed; lessons are never deleted). REACHED 2026-08-03 at 12,069 words, and the declared exit
# was taken rather than re-argued: eight closed risk rows moved to risk-register-archive.md, nothing
# deleted. Back to 11,523. The next time this is reached, the improvement register's `done` rows are
# the remaining candidate — and the number still does not move.
reviewing-the-estate = 12000
  CLAUDE.md
  docs/_index.md
  docs/program/evaluation.md
  docs/program/review-protocol.md
  docs/00-governance/risk-register.md
  docs/program/improvement-register.md
```

## What the numbers say today

Measured 2026-08-02, at the moment the gate was written:

| Set | Kind | Words | ≈ Tokens | Budget |
|---|---|---|---|---|
| `every-task` | ratchet | 2,992 | 3,979 | 3,200 |
| `authoring-a-concept` | ratchet | 6,722 | 8,940 | 7,200 |
| `changing-a-rule` | **ceiling** | 8,157 | 10,849 | 10,000 |
| `reviewing-the-estate` | **ceiling** | 11,523 | 15,326 | 12,000 |
| **`planning`** | **ceiling** | **17,409** | **23,153** | 20,000 |

**`planning` was 35,453 words and is 17,409 — halved without moving a file.** The whole difference is
the `adr-index` slice: the ADR file is 20,200 words, of which 1,950 are the entries a planning
session actually scans. Neither it nor `WORKFLOW.md` carries a G9 budget, because G9 budgets by
`type` and none exists for `adr` or `program`, so the two largest documents in the repository were
the two `CLAUDE.md` instructs a session to load on every planning task — and pricing the *unit that
is read* rather than the file it sits in was the whole fix.

**The gate caught the same mistake three times, which is how the ratchet/ceiling distinction got
made — and the third time was after the rule for it had been written.**

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

Both ceilings carry a structural answer, not just headroom — and `planning`'s changed.

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
