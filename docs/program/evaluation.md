---
id: program-evaluation
title: "Evaluation & Reasoning — self-review protocol and decision ladder"
type: program
owner: orchestrator
status: draft
since: 2026-07-19
updated: 2026-08-03
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

6. **Search for a better implementation, then close what the request left open (PLT-R6 /
   ADR-0038).** The search is standing: algorithmic cost, compute and memory, data-structure and
   boundary choice, clean-code and structure, security — inside the **adopted lanes only**, never by
   proposing a new technology. When a detail is missing whose two plausible readings would produce
   **different work**, do not guess and do not ask in prose: present a **selectable list** of
   recommended options (§5). Implement what is selected in the same turn; record what is declined.

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

## 5. Reviewing a set of documents

Any review — a repository, a department, an ADR set, one specification — runs the procedure in
[review-protocol.md](review-protocol.md): enumerate the estate mechanically, name the finding
classes before looking, mark every item as reached, consolidate into the durable records, then fix
what needs no decision, mechanize what a gate could catch and raise the rest as a selectable list.
The checklist is transient and is deleted when the review closes; the outcome is not.

## 6. Asking well (the question craft PLT-R6 depends on)

A list of options is only as good as the thinking behind it. What makes the difference:

1. **Ask only what changes the work.** If both answers produce the same code, decide, state the
   assumption, and move. A question with no consequence spends the owner's attention for nothing.
2. **Do the independent work first.** Everything that does not depend on the answer is finished
   before the question is asked, so waiting costs nothing and the question arrives with context.
3. **Read before asking.** A question the repository, the ADRs or the rules already answer is a
   failure to look, not a clarification.
4. **Show the fork, not the abstraction.** "Pro-rata, priority-ordered, or minimum-viable-quantity?"
   beats "how should allocation work?" — concrete alternatives are answerable in seconds.
5. **Name the cost of every option, including the recommended one.** An option presented without its
   trade-off is a steer disguised as a choice.
6. **Recommend, and say why.** Withholding a recommendation is not neutrality; it hands back
   judgement the implementer is better placed to exercise.
7. **Surface tensions in the request itself.** When an instruction contains two statements that pull
   apart, quote both, say which reading will be taken, and let it be corrected. This is the cheapest
   correction point in the whole task.
8. **Bound the count.** A few load-bearing questions. A survey transfers the design back to the
   owner, which is the opposite of the point.
9. **Cover the space, and admit it when you cannot.** Options should be mutually exclusive; if they
   do not exhaust the possibilities, say what is missing rather than implying they do.
10. **Prefer a reversible default over a blocking question** when being wrong costs a small edit.
    Reserve blocking for choices that are expensive or unsafe to get wrong.
