---
id: program-evaluation
title: "Evaluation & Reasoning — self-review protocol and decision ladder"
type: program
owner: orchestrator
status: draft
since: 2026-07-19
updated: 2026-07-19
relations:
  - { type: part-of, target: index-program }
  - { type: governed-by, target: governance-root }
---
# Evaluation & Reasoning — self-review protocol

> HOW the AI reasons before acting and reviews itself before handing off (ADR-0012). The
> contract's Definition of Done says WHAT must be true; this says HOW to get there and
> where a choice gets recorded when the spec leaves room. Applies to every task and every
> lane (including the single session playing all lanes — operating-model §2).

## 1. Before acting (reasoning protocol)

1. **Load the bounded context** (operating-model §1): contract + decision index → the
   department's SKILL + README → the unit spec (when one exists). Never the whole repo.
2. **Plan⇄context check (ADR-0010):** does this change introduce, rename or reshape a
   product concept? If yes, the model/ADR/rules are updated FIRST.
3. **State assumptions before resolving them.** Anything the task leaves open is named as
   an assumption, resolved via the decision ladder (§2), and reported at handoff — never
   silently absorbed.
4. **For every non-trivial design choice:** list at least two alternatives, name the
   trade-offs (complexity now vs. maintenance later, performance, security,
   reversibility), and pick the simplest thing that respects the rules. In this repo that
   includes the cross-language rule: a formula that exists in both TS and Python is
   changed in both or not at all (see the `a12c114` divergence — risk register #2).
5. **Run the ENG-R9 best-option gate before writing code** (`50-engineering/rule.md`), and
   state the result at handoff — six checks, no exceptions: **lane** (is this the owning
   technology? ENG-R8/ADR-0033) · **best practice** (idiomatic for *that* technology, not
   imported from another) · **security** (boundary validation, least privilege, no secrets in
   code, nothing trusted from the client) · **speed** (complexity and round trips suit the path;
   a hot path acquires no network hop) · **scalability** (holds at the target scale of many
   projects and large data volumes, ADR-0034, or the limit is documented) · **license** (OSI,
   commercially usable, modifiable — ADR-0002). If a check fails, the design changes before the
   code is written, not after.

## 2. Decision ladder (where a choice gets recorded)

| Weight of the choice | Test | Recorded as |
|---|---|---|
| Load-bearing / hard to reverse | reversing it touches more than one department, or it binds a technology/contract/policy | **ADR** (proposed to the owner) |
| Shapes a unit's observable behavior | a future reader of the spec/README would be surprised not to find it | **the unit spec / department README** |
| Local implementation detail | invisible outside the module boundary | **code + its tests** |

When in doubt, go one row up. A choice recorded too high costs a paragraph; a choice
recorded too low costs a re-derivation every time someone hits it.

## 3. Self-review before handoff (checklist)

- [ ] Re-read the full diff **as the reviewer**, not the author — every change traceable
      to the task; nothing smuggled in.
- [ ] The contract's Definition of Done actually run, not assumed: `make verify` green
      (typecheck + unit tests + doc gates); `make verify-full` before proposing a merge.
- [ ] Every rule ID touched (SCM-Rx / department families) keeps its test.
- [ ] TS/Python mirrored logic changed on both sides, or explicitly flagged.
- [ ] Assumptions and open uncertainties written down for the handoff
      (operating-model §4).
- [ ] Estimate honesty: if the task grew beyond its bound, say so — a bounded task that
      doubled is a backlog signal, not something to absorb silently.

## 4. Coarse estimation (before starting)

Size the task S / M / L and risk low / medium / high. An L-or-larger or high-risk task is
**split or escalated to the owner before work starts** — never discovered at the end.
Record the estimate in the task entry so drift is visible in the backlog.
