---
id: program-review-protocol
title: "Review Protocol — how a body of documents is reviewed"
type: program
owner: orchestrator
status: active
since: 2026-07-29
updated: 2026-07-29
relations:
  - { type: part-of, target: index-program }
  - { type: governed-by, target: governance-root }
  - { type: refines, target: program-evaluation }
---
# Review Protocol — how a body of documents is reviewed

> **What this is for.** Ask for a review of any set of documents — the whole repository, one
> department, the ADRs, a single pull request, a specification, a contract, a set of notes — and
> this is the procedure that runs. It is deliberately independent of *what* is being reviewed and
> of *what* is being looked for: the estate and the finding classes are named at the start of each
> review, the mechanics below never change.
>
> **Why it is written down.** The 2026-07-29 review of this repository found 53 files carrying
> residue after four completed sweeps had each reported success. Two of its findings had been
> *reported in writing* by an earlier phase and never fixed. The difference was not diligence; it
> was that the earlier passes had no enumerated estate, so nothing distinguished "checked and
> clean" from "not reached". This protocol exists to remove that ambiguity.

## 1. The five steps

1. **Name the estate, then enumerate it.** Not "the docs" — a list, produced mechanically, with a
   count. `git ls-files` for a repository, an explicit path list otherwise. The count is the
   denominator every later claim is measured against.
2. **Name the finding classes before looking.** Two or five named classes, written down first.
   Reviewing without them produces a list of whatever caught the eye, which is not a review of the
   estate; it is a sample of it. Derive the classes from what the project has *already* got wrong —
   its ADRs, its risk register, its known pitfalls — because a defect that happened once has a
   mechanism that is still in place.
3. **Mark every item as it is reached.** A checklist with three states: not reached, reached and
   clean, reached with a finding. Marking is not bookkeeping — it is the only thing that makes
   "there is no residue in the remaining 130 files" a statement rather than a hope, and it lets a
   review survive being interrupted halfway.
4. **Consolidate findings into their durable homes**, one class at a time, each with the file, the
   line and *why it is wrong* rather than only what it says.
5. **Close the loop.** Fix what needs no decision; mechanize what a gate could catch; raise what
   needs a decision as a selectable list (PLT-R6); and record what is deliberately left.

## 2. Where the checklist lives, and whether it survives

The enumerated checklist is a **transient working file** (knowledge-architecture §5): it is kept
untracked, outside the repository, for the duration of the review. When the review closes its
content has been consolidated into the durable records, and the listing is deleted — a
half-marked checklist committed to the tree becomes a document that outranks its own successor.

**This project keeps no per-review log.** What it keeps is the *outcome*, in the records that
already exist:

| Finding | Home |
|---|---|
| A concrete defect, fixed | the commit — its message states the class and the reason, not only the diff |
| A defect the gates could have caught | a new or widened gate in `tools/verify.py`, plus its entry in `00-governance/knowledge-architecture.md` §11 |
| A standing exposure that cannot be mechanized | `00-governance/risk-register.md` |
| A recurring mistake in *how* the work is done | `program/improvement-register.md`, and a known pitfall in `program/evaluation.md` |
| Something needing an owner decision | a selectable list now, an ADR when answered |
| Status that was wrong | corrected at the source, with the correction visible (a triage block, not a silent edit) |

## 3. What makes a finding, and what does not

A finding needs a **reason that outlives the reviewer**: the statement contradicts a decision, or
a standard, or another statement in the same estate, or it describes something that no longer
exists. "I would have written this differently" is not a finding.

Three shapes recur, and all three are quiet:

- **A statement the estate has since falsified.** A gate count, a path, an invariant ("CI runs
  exactly `X`") that was true when written. Nothing breaks; a reader is simply misled. Grep for the
  claim, not for the topic.
- **A partially completed correction.** One row fixed and eleven left, a replacement sentence
  inserted above the sentence it replaced, a heading updated and its body not. These are evidence
  that a sweep *started* here, which makes them likelier, not less likely, to be in the file that
  looks already handled.
- **A finding recorded but not closed.** Search the project's own registers for reported problems
  and verify each one is actually fixed. Two of the 2026-07-29 findings were sitting in
  `WORKFLOW.md` in the reviewer's own words.

## 4. Where residue hides

- **Wherever the gates do not reach.** A gate over part of an estate certifies only that part, and
  the part left out is usually the part hardest to check — which is where the exposure
  concentrates. In this repository that is `.claude/**`, which no gate read and which instructs
  every session's work.
- **In the file the reader trusts most.** A glossary, a README, an index: the more authoritative
  the document, the further a wrong statement in it travels.
- **In parameters, not in prose.** The prose says "the level is a project's choice" and the output
  description three lines below says `benchmark_hours: 2.0`. The second one is the one that gets
  copied.
- **In anything produced by a scripted edit.** Read the resulting diff back as prose. Every
  mangled sentence and duplicated clause this project has had came from a scripted edit that was
  not read back afterwards.

## 5. Reporting

Report the denominator, the number of items carrying findings, the classes with counts, what was
fixed, what was mechanized, and what is left with the reason. A review that reports only its
findings has not said whether it looked everywhere.

## 6. Governing refs

`CLAUDE.md` (Definition of Done, the inclusion test) · `program/evaluation.md` §3 self-review, §6
asking well · `00-governance/knowledge-architecture.md` §5 (transient knowledge), §11 (gates) ·
**PLT-R6** for raising what needs a decision.
