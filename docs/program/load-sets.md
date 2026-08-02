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

```load-sets
# Loaded before anything else, every single task.
every-task = 3200
  CLAUDE.md
  docs/_index.md
  docs/program/evaluation.md

# "What should I do next?" — the state of the estate plus the decisions behind it.
# NOT a ratchet, and see below for why: the ADR index is append-only by design, so a tight
# budget here goes red on ordinary decision-writing. 36000 is a ceiling with a structural
# answer attached — when it is next reached, split the ADR bodies out; do not raise it again.
planning = 36000
  CLAUDE.md
  docs/_index.md
  docs/program/evaluation.md
  docs/program/WORKFLOW.md
  docs/10-decisions/README.md

# Adding or changing a concept node.
authoring-a-concept = 7200
  CLAUDE.md
  docs/_index.md
  docs/program/evaluation.md
  docs/00-governance/knowledge-architecture.md
  docs/program/templates/concept.md
  docs/30-foundation/scm-core/rule.md
  docs/30-foundation/measurement/rule.md

# Adding or changing a rule in any family.
changing-a-rule = 8000
  CLAUDE.md
  docs/_index.md
  docs/program/evaluation.md
  docs/00-governance/knowledge-architecture.md
  docs/00-governance/id-registry.md
  docs/50-engineering/rule.md

# Running the review protocol over a set of documents.
reviewing-the-estate = 9200
  CLAUDE.md
  docs/_index.md
  docs/program/evaluation.md
  docs/program/review-protocol.md
  docs/00-governance/risk-register.md
  docs/program/improvement-register.md
```

## What the numbers say today

Measured 2026-08-02, at the moment the gate was written:

| Set | Words | ≈ Tokens | Budget | Headroom |
|---|---|---|---|---|
| `every-task` | 2,908 | 3,867 | 3,200 | 9 % |
| `authoring-a-concept` | 6,546 | 8,706 | 7,200 | 10 % |
| `changing-a-rule` | 7,293 | 9,699 | 8,000 | 10 % |
| `reviewing-the-estate` | 8,309 | 11,050 | 9,200 | 11 % |
| **`planning`** | **33,683** | **44,798** | 36,000 | 6 % |

**`planning` is the outlier and it is not close.** Two documents account for 91 % of it:
`docs/10-decisions/README.md` at ~19,100 words and `docs/program/WORKFLOW.md` at ~11,700. Neither
carries a G9 budget, because G9 budgets by `type` and no budget exists for `adr` or `program` — so
the two largest documents in the repository are the two `CLAUDE.md` instructs a session to load on
every planning task, and they are the two nothing has ever bounded.

**The gate proved this on the commit that introduced it.** `planning` measured 32,009 words, the
budget was set at 33,000 as a ratchet — and then writing the two ADRs that adopt G14 and the
mutation harness added 1,674 words to the ADR index and turned the gate red. Nothing was wrong with
the change; **the ratchet was wrong**. The ADR index is append-only by design (ADR-0011: history is
never rewritten), so any budget a few percent above it goes red the next time anyone records a
decision — which would make the gate an obstacle to the practice it is supposed to protect.

So `planning` carries a **ceiling with a structural answer attached, not a ratchet**: 36,000, and
when it is next reached the answer is **the split, not another raise**. The ADR index is an index
*and* forty-two decision bodies in one file, and its own footer already anticipates the separation
(`NNNN-title.md` "when extensive"). The other four sets stay ratcheted, because none of them
contains an append-only document.

## What this does not claim

- **It does not measure tokens.** Words × 1.33 is the approximation ADR-0012 already uses for G9.
  A real tokenizer would be more accurate and would add a dependency to a lane that has none.
- **It does not know what a session actually read.** The manifest is a declaration of intent. It
  binds the *instructions* — if `CLAUDE.md` or `WORKFLOW.md` tells a session to read something, it
  belongs in a set here, and G14 then prices it.
- **It sets no target for model behaviour.** The evidence in ADR-0041 says degradation is
  continuous and begins early; it does not fix a safe number, and no standards body does either.
  The budget is this repository's own engineering decision, in the same category as G9's.
