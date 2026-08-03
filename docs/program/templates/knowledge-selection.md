---
id: program-knowledge-selection-template
title: "Knowledge Selection Template (PLT-R7)"
type: program
owner: orchestrator
status: active
since: 2026-08-03
updated: 2026-08-03
relations:
  - { type: part-of, target: index-program }
  - { type: governed-by, target: index-adr }
---
# Knowledge selection template

> **What this is for.** PLT-R7 requires that the parts of the Global Context governing a project are
> **chosen and declared to the owner before development begins**. This is the form that declaration
> takes.
>
> **Where the filled-in copy lives: in the project's own repository, not here.** PLT-R2 keeps
> project-specific material out of the context, and ADR-0037 keeps company data out of it. The
> context provides the **form**; the project holds the **instance** (ADR-0046). The consequence is
> honest and worth knowing: **no gate in this repository can check that a project made its
> declaration.** The artefact exists so the project and its reviewers can audit it later, not so this
> repo can police it.

## Why the digest column is not optional

The context is versioned **per node by content digest**, with a calendar tag as the human-readable
reference (ADR-0046). A declaration naming `CPT-0157` without a digest says which node was consulted
and not **what it said at the time** — and a concept node's meaning can be sharpened, its assumptions
extended, its project-chosen inputs re-scoped, all without changing its ID. Recording the digest is
what makes "we built against this" a checkable claim a year later.

    python3 -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest()[:12])" <file>

## The form

```markdown
# Knowledge selection — <project name>

**Declared:** <YYYY-MM-DD>  ·  **Declared by:** <who>  ·  **Accepted by:** <owner>
**Context tag:** <e.g. 2026.08>  ·  **Context commit:** <sha>
**Tech branch:** <AI | ML | data | DevOps | database | web | …>  (PLT-R5: exactly one)

## In scope — company-operating axis

| Node / rule | Digest | Why this project needs it |
|---|---|---|
| CPT-NNNN <name> | <sha256:12> | <one line> |
| XXX-RN | <sha256:12 of its rule file> | <one line> |

## In scope — engineering-practice axis

| Practice area | Anchor kind | What is being taken from it |
|---|---|---|
| <area, from 50-engineering/practice-areas.md> | standard / terminology / identity | <one line> |

## Considered and excluded

| Not used | Why not |
|---|---|
| <department, area, node or rule> | <one line — this is the column that matters> |

## Project decisions this selection leaves open

| Decision | Where it is recorded in this project |
|---|---|
| <e.g. the over-receipt tolerance CPT-0027 names> | <path in the project> |
```

## The section that earns the document

**"Considered and excluded" is the reason this form exists.** A list of what a project uses is
mildly useful; a reader can get most of it from the imports. What no reader can reconstruct is
**whether something absent was rejected or forgotten** — and PLT-R7 exists because those two look
identical from the outside, both to a reviewer later and to the next agent picking up the work.

An empty exclusions table on a project that uses four of fourteen departments is not a clean
declaration. It is an undeclared one.

## Filling it in for a project that uses very little

Most projects will. A web app in this workspace might take **one** practice area and **no**
supply-chain department, and that is a complete, correct declaration — the point is that the choice
was made and named, not that the list is long. Say so plainly in the exclusions column: *"the
thirteen other departments: this project buys, builds and delivers nothing."*
