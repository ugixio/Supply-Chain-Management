---
id: program-known-pitfalls
title: "Known Pitfalls — the decision rules the incidents distil to"
type: program
owner: orchestrator
status: active
since: 2026-08-03
updated: 2026-08-03
relations:
  - { type: part-of, target: index-program }
  - { type: refines, target: program-improvement-register }
  - { type: governed-by, target: governance-root }
---
# Known pitfalls — what the register's incidents distil to

> **This is the document [review-protocol.md](review-protocol.md) and WORKFLOW U15b already pointed
> at, and it did not exist.** The incidents live in
> [improvement-register.md](improvement-register.md), which is the *record*; a reviewer needs the
> *rules*. Each line names the row it came from, so the evidence is one lookup away and the register
> never has to be read whole — which is also why the register left the `reviewing-the-estate` load
> set and this document took its place (`load-sets.md`).
>
> **A lesson added to the register is distilled here in the same change.** A distillation that lags
> its source is worse than no distillation, because it reads as complete.


**This is the section `review-protocol.md` §Where findings land and WORKFLOW U15b already pointed
at, and it did not exist.** The incidents live in
[improvement-register.md](improvement-register.md), which is the *record*; a reviewer needs the
*rules*. Each line names the row it came from, so the evidence is one lookup away and the register
never has to be read whole. **A lesson added to the register is distilled here in the same change.**

### About checks and gates

- **A gate over part of an estate certifies only that part.** G11 shipped green while the skills tree
  cited three retired rules, because it read front-matter documents only. Ask what the gate does
  *not* see before trusting a pass. (#7, #11)
- **A gate must be verified against the environment that runs it,** not the one that wrote it. (#12)
- **One mutant per gate is not one mutant per claim.** Count what a gate asserts; G3 asserts three
  things and only one had a planted violation. (#18)
- **A check that searches for the shape of a defect fires on text that names the defect** — and in a
  corpus about avoiding defects, that text concentrates in the *correct* answers. Prefer changing the
  document; weaken the check only when the document cannot say what it needs to. (#19, #20, #22)
- **A staleness check is only as precise as the unit it hashes.** Widening the unit to something
  cheap to compute buys false alarms; say what they mean rather than removing the check. (#22)
- **A suite tightened after a defect is evidence about that defect's shape, not proof of coverage.**
  The same defect in a well-formed wrapper walks straight through. (#17)
- **Delegation transfers authority over a decision, not over a scope.** A check that defers to a
  whole suite must say which of the suite's findings are its own. (#24)
- **Prefer removing an invalid operation from the surface to documenting that it is forbidden** — and
  gate the *absence*. A warning depends on being read; a missing column cannot be selected. (#30)
- **A test must draw identifiers from a pool the allocation authority has reserved.** (#26)
- **When a table encodes a claim about its own fields, the claim is checkable** — and *"it renders
  fine"* is not evidence, because a Markdown row missing its last cell renders fine by design. (#31)
- **A stated threshold is only worth writing if it is honoured on the occurrence that hits it** —
  and that occurrence always arrives looking like one more small widening. The prose-disowning
  heuristic reached its declared sixth and was replaced, not widened. (#33)
- **When a check fires, keep diagnosing after the first cause is found.** One defect that explains
  the symptom is not evidence that it is the only one — the `unit-codes` regression had two, and
  the second was the one that mattered. (#34)
- **A task can only be scored against a set that can answer it.** When the subject was never given
  what the question needs, the manifest is the defect and the answer is not. (#34, ADR-0043)

### About rules, thresholds and sweeps

- **Before setting a threshold, ask whether the quantity is bounded, ratcheting or monotonic.** The
  three need different mechanisms, and a ratchet over an append-only quantity schedules a false
  alarm. (#16)
- **A classification rule is applied by sweeping every existing instance the day it is written** —
  fixing only what failed is how a rule becomes a rule for new work only. This one has recurred five
  times. (#28)
- **Ask the monotonic question of *sections*, not of documents.** A roster of identifiers inside a
  bounded file is an append-only part, and the file's boundedness says nothing about it. This is the
  correction to the line above, not a repetition of it. (#32)
- **Before adding words to a document, check how many load sets contain it.** Placement is a budget
  decision even when it does not feel like one. (#32)
- **If the mechanism performing a discipline is "a person remembering", the entry is not done.** (#15)
- **A prescribed mechanism is re-derived at implementation time, not executed as written.** A
  mitigation column is prose that no gate evaluates, so it can carry a technical error for days —
  and quoting it forward gives the error a second appearance that reads as corroboration. (#29)
- **State an identity once and cite it;** restating it per department is how the versions diverge.
  (#13, ADR-0039)
- **A completed sweep and a clean estate are different claims,** and only one of them is usually
  checked. (#11)
- **A statement attributed to two implementations escapes a sweep written for one.** (#8)

### About knowledge and its sources

- **The reference document is the stalest thing in the repository.** A citation stops matching its
  source without anything changing here. (#9, risk #12)
- **Structural completeness is not model impact.** Exemplars, budgets and a fast gate move results
  more than added rules do. (#3)
- **Purpose belongs at the entry point, not in the decision log.** An ADR explains why a choice was
  made, never what the thing is — and the two get confused because both feel like documentation.
  (#27)
- **When a rule has been read, loaded and still broken, the gap is a missing *form*, not insufficient
  emphasis.** And when a whole category of document seems absent, check whether its most obvious
  instances are the forbidden ones. (#23)
- **Enumerate the estate before recommending an addition to it.** "Missing" is a fact about the
  estate, not about the source you read. (#25)
- **An evaluation built from past failures can only test the classes that already failed.** Ask
  periodically what question the corpus cannot answer. (#27)

### About agents and prompts

- **When an agent gets something wrong, ask what it was given before asking what it did.** A failure
  that traces to an absent input is a manifest defect wearing an agent's clothes, and the cheapest
  fix is usually to make a document already in the set carry the missing fact. (#21)
- **If the subject already knows what the artefact is supposed to teach, the measurement is of the
  subject.** (#17)
- **A refined prompt can still be underspecified, and both default responses — guess, or ask in
  prose — are wrong.** Present the fork as a selectable list (§6). (#10)

### About code

- **Duplicated logic without a shared oracle will drift.** (#1)
- **Verify the toolchain itself, with the real commands, in CI.** Declared dev tooling was once
  mutually uninstallable and nothing had ever checked. (#2, #6)
- **An instantiated script drifts from the skeleton it came from.** (#4)
