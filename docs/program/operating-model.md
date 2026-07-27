---
id: program-operating-model
title: "AI Operating Model — knowledge layers + lanes"
type: program
owner: orchestrator
status: active
since: 2026-07-19
updated: 2026-07-19
relations:
  - { type: part-of, target: index-program }
  - { type: governed-by, target: governance-root }
---
# AI Operating Model

> How AI-driven work is executed in this repo. Adopted with the context skeleton
> (ADR-0010); the lane split below is a **default pending the owner's decision**
> (open decision "Agent lanes" in `10-decisions/README.md`).

## 1. The four layers of knowledge

```
┌──────────────────────────────────────────────────────────────┐
│  GLOBAL RULES     →  CLAUDE.md + the decision INDEX          │
│                      (full ADR text on demand — ADR-0012)    │
├──────────────────────────────────────────────────────────────┤
│  AGENT PROFILE    →  .claude/agents/*.md (ADR-0027) + the      │
│                      technology skills in .claude/skills/*     │
├──────────────────────────────────────────────────────────────┤
│  AREA SKILL       →  .claude/skills/<dept>/SKILL.md          │
│                      + .claude/skills/<dept>/SKILL.md        │
│                      + rule IDs (SCM-Rx, dept families)      │
├──────────────────────────────────────────────────────────────┤
│  UNIT CONTRACT    →  docs/40-contexts/<dept>/specs/<key>.md  │
│                      (future — templates/spec.md)            │
└──────────────────────────────────────────────────────────────┘
```

**This repo already implements layer 3**: the 15 `.claude/skills` ARE the area-skill
layer. The skeleton adds layers 1 (decisions + stable rules) and 4 (spec template), and
leaves layer 2 optional.

**The exemplar unit (ADR-0012).** The first department completed to full satisfaction
(candidate: `01-procurement`) is declared the exemplar by an ADR that names it. Skills
cite it, sibling departments copy its shape, and the AI reads it before building a
sibling. Rules say what must hold; the exemplar shows what good looks like — models
imitate real code more reliably than they deduce from prose. It is always real code,
never fabricated samples.

## 2. Lanes (default trio — activate via the agent-lanes decision)

| Lane | Role | Owns here | Never does |
|---|---|---|---|
| **WHAT** | defines the business | specs, department rule.md files, glossary, acceptance criteria | write code |
| **HOW** | implements | `apps/`, `crates/`, tests, git | invent rules; skip the spec |
| **SPECIALTY** | augments | heavy ML/optimization models by contract | decide business rules alone |

**Lanes are now activated (ADR-0027).** The lanes are realized as 7 least-privilege agent
profiles in `.claude/agents/` drawing on 7 technology/practice skills in `.claude/skills/`
(alongside the 15 domain skills). The **main session orchestrates** — decomposes, assigns,
gates — and may run a task itself when spawning an agent is not worth the cold-start cost.
Each agent still obeys its "never does" column; the mapping of agents to lanes is in
ADR-0027.

## 3. Per-unit flow

```
① WHAT   spec from templates/spec.md (+ rule IDs from the registry)
② HOW    branch feat/<key> → implement + tests (every rule ID → a test) → green
③ SPECIALTY (if the unit needs a model) → delivered by contract, validated in ②'s lane
④ owner reviews → merge → annotated tag when a demonstrable state lands (ADR-0011)
```

## 4. Communication contract (how the AI reports — ADR-0012)

Every report — task completion, handoff or blocker — has the same shape:

1. **Outcome first.** What was produced or what happened, in one or two sentences.
2. **Gate evidence.** `make verify` / test results stated as they ran (green, or the
   actual failure output) — never "should pass".
3. **Assumptions and uncertainties, explicit.** Everything the task left open and how it
   was resolved (with its decision-ladder record — `evaluation.md` §2), plus anything
   still unknown. A silent assumption is a defect of the report.
4. **Proposed commit** in Conventional Commits form (ADR-0011) — the owner decides the
   merge.
5. **Follow-ups become backlog entries** in `WORKFLOW.md` — never prose-only mentions
   that evaporate.
6. **Conflicts stop work.** A task that would violate the contract or an ADR is not
   executed; the AI reports the conflict and waits.
7. **Corrections become pitfalls.** When the owner corrects the AI's output, the
   correction lands as a one-line "wrong → right" entry in the department's
   `.claude/skills/<dept>/SKILL.md` Known-pitfalls section. A correction that is not
   recorded will be repeated.
