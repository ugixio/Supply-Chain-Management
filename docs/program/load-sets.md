---
id: program-load-sets
title: "Load Sets — what an AI reads together, and how much that is"
type: program
owner: orchestrator
status: active
since: 2026-08-02
updated: 2026-08-02
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
A member may be a literal path or a glob. Missing members fail the gate — a manifest that names a
file nobody kept is worse than no manifest.

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
# CEILING — contains the ADR index, which is append-only by design (ADR-0011). When 38000 is
# reached the answer is splitting the ADR bodies out (backlog X3), not another raise.
planning = 38000
  CLAUDE.md
  docs/_index.md
  docs/program/evaluation.md
  docs/program/WORKFLOW.md
  docs/10-decisions/README.md

# RATCHET — all members bounded.
# Adding or changing a concept node.
authoring-a-concept = 7200
  CLAUDE.md
  docs/_index.md
  docs/program/evaluation.md
  docs/00-governance/knowledge-architecture.md
  docs/program/templates/concept.md
  docs/30-foundation/scm-core/rule.md
  docs/30-foundation/measurement/rule.md

# RATCHET — all members bounded.
# Adding or changing a rule in any family.
changing-a-rule = 8000
  CLAUDE.md
  docs/_index.md
  docs/program/evaluation.md
  docs/00-governance/knowledge-architecture.md
  docs/00-governance/id-registry.md
  docs/50-engineering/rule.md

# CEILING — contains the improvement register AND the risk register, both append-only (closed
# risks stay listed; lessons are never deleted). A ratchet here went red 21 words over on the
# commit that added one lesson. When 12000 is reached, the answer is archiving closed rows to a
# dated file, not another raise.
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
| `every-task` | ratchet | 2,979 | 3,962 | 3,200 |
| `authoring-a-concept` | ratchet | 6,693 | 8,902 | 7,200 |
| `changing-a-rule` | ratchet | 7,440 | 9,895 | 8,000 |
| `reviewing-the-estate` | **ceiling** | 9,221 | 12,264 | 12,000 |
| **`planning`** | **ceiling** | **35,453** | **47,152** | 38,000 |

**`planning` is the outlier and it is not close.** Two documents account for 91 % of it: the ADR
index and `WORKFLOW.md`. Neither carries a G9 budget, because G9 budgets by `type` and no budget
exists for `adr` or `program` — so the two largest documents in the repository are the two
`CLAUDE.md` instructs a session to load on every planning task, and they are the two nothing had
ever bounded.

**The gate caught the same mistake twice in one day, which is how the ratchet/ceiling distinction
got made.**

- **First**, on the commit that introduced G14: `planning` measured 32,009 and the budget was set at
  33,000 as a ratchet. Writing the two ADRs that adopt G14 and the mutation harness added 1,674
  words to the ADR index and the gate went red. The change was right; the ratchet was wrong.
- **Then again, one commit later**, on `reviewing-the-estate` — 21 words over, from adding a single
  lesson to the improvement register. The lesson being added *was* the first occurrence. **Recording
  a lesson is not applying it** (improvement #15's point, demonstrated on itself), and the fix is
  not a bigger number: it is classifying every set as ratchet or ceiling by asking whether any
  member grows monotonically by design.

Both ceilings carry a structural answer, not just headroom. For `planning` it is splitting the ADR
bodies out of the index (backlog X3) — the index's own footer already anticipates it
(`NNNN-title.md` "when extensive"). For `reviewing-the-estate` it is archiving closed risk rows and
done improvement rows to a dated file. **When either ceiling is reached, that is what happens — not
another raise.**

## What this does not claim

- **It does not measure tokens.** Words × 1.33 is the approximation ADR-0012 already uses for G9.
  A real tokenizer would be more accurate and would add a dependency to a lane that has none.
- **It does not know what a session actually read.** The manifest is a declaration of intent. It
  binds the *instructions* — if `CLAUDE.md` or `WORKFLOW.md` tells a session to read something, it
  belongs in a set here, and G14 then prices it.
- **It sets no target for model behaviour.** The evidence in ADR-0041 says degradation is
  continuous and begins early; it does not fix a safe number, and no standards body does either.
  The budget is this repository's own engineering decision, in the same category as G9's.
