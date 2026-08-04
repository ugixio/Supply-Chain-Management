---
id: program-known-pitfalls
title: "Known Pitfalls — the decision rules the incidents distil to"
type: program
owner: orchestrator
status: active
since: 2026-08-03
updated: 2026-08-04
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
- **A two-sided invariant needs a two-sided check.** G9 verified that every ADR body had an index
  entry and never the reverse, so two decisions shipped as summaries with no decision. When a gate
  asserts that two lists agree, assert it in both directions or it half-passes. (#36)
- **A hand-written list that mirrors a machine-readable one will drift, and the gate reading it will
  not notice.** G15's watched files lagged its own load-set manifest by two commits. Derive the list
  from the source instead of maintaining a copy. (#36)
- **Refresh a freshness digest only for the file whose task you just scored.** A loop over the whole
  block turns the claim into a formality: the gate goes green while the measurement no longer
  describes its input, which is the exact state it exists to forbid. (#42)
- **When a false positive recurs, ask whether the previous fix named the concept or an instance of
  it.** `QUOTED_SPAN` fixed three *spellings* of quotation and the same correct answer failed one
  cycle later using a fourth. Prefer structure over vocabulary. (#37)
- **On the third occurrence of a class, stop fixing instances and check whether an earlier author
  already named the instrument.** `DISOWNS` had written down "ask for a structured answer" as the
  remedy before any of the three failures; three local patches were applied instead. (#38)
- **Score a declared block, not free prose, whenever the answer is a set of identifiers.** Prose
  scoring punishes the discussion that makes an answer good — writing off a retired ID, naming a
  near-miss — because the disowning word wraps onto another line. (#38)
- **Generalised, after four occurrences: a check for “asserted something it should not” reads a
  declared block, never prose.** The three tasks of that shape all do; tasks checking for the
  *presence* of correct reasoning do not need it. (#39)
- **Three consecutive fixes that each add one more way of writing the same thing means the scan is
  wrong, not incomplete.** A word list, three quote syntaxes, then blockquotes — and the next answer
  used plain prose. (#39)
- **A line is an artefact of wrapping; a paragraph is what someone wrote.** Five false positives had
  one cause — checkers reading `splitlines()` while a claim and its disowning word sat on different
  lines. Four fixes treated symptoms first. Analyse the paragraph. (#43)
- **Widening a *positive presence* vocabulary is safe; widening a *defect-shape* pattern is not.** The
  first lowers false negatives and cannot accuse anyone; the second is how four false positives were
  built. (#43)
- **When you write a generalisation, apply it by re-classifying every case, not the ones that
  prompted it.** #39's rule was correct and `what-is-this-for` was exempted on its dominant shape
  while carrying exactly the clause the rule was about. (#43)
- **Gate the numbers a document is believed for, on *drift* rather than on a calendar.** The dossier
  was wrong about six counted facts while twenty other properties were gated — and the gated ones lent
  the stale ones authority. A wall-clock check would have reddened a quiet week instead. (#45)
- **A declared quantity a check cannot recompute must be refused, not tolerated.** Otherwise the block
  becomes a place to publish an interpretation in the typography of a measurement — and the mirror
  case: a measurable quantity left *undeclared* is where the inconvenient number hides. (#45)
- **A collateral declaration can encode measurement *state*, not just a file set — derive it.** Three
  `also` columns broke in one commit when five digests returned to `(unmeasured)`, reporting gates as
  failing to fire while nothing about any gate had changed. (#47)

### About budgets that keep being breached

- **Compression is a one-time payment on a recurring bill.** A load set's declared exit was executed in
  full and the set was still over, because halving the copies does not stop the surviving copy growing.
  **When the part that breaches a ceiling is a part that grows by design, move the part out of every
  member** — do not compress it, and do not raise the number. (#46)
- **Ask where a growing roster is *carried*, not only how big it is.** The gate list cost two load sets
  twice for five occurrences because it lived in two files that both sat inside sets. (#46)

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
- **Prose admitting a number is policy does not stop the number being copied.** Four nodes said
  "the numbers are policy" in *Assumptions* while printing them in `## Formula`, and the formula is
  what a reader lifts. State the shape parametrically and put the values in
  `Project-chosen inputs` — disclosure is not placement. (#36)
- **A sweep reaches the departments it was named after.** Four completed C1 phases left the scoring
  schemes in demand-planning, risk and supplier-development untouched because no phase listed those
  nodes. Enumerate the estate, not the phases. (#36)
- **A decision recorded as a rule clause is invisible to a search of the decision log.** The
  NestJS↔Rust transport was fixed in ENG-R10.1, and reading the ADR index concluded it was undecided.
  Search the rule families too, before reporting a gap. (#40)
- **When a decision reverses a premise, grep the rule text for clauses built on it.** ADR-0037 swept
  the nodes and left ENG-R10.7 ordering the opposite of what G10 enforces, for six weeks. (#40)

- **Audit what exists before accepting a proposal's framing.** Two thirds of a Context-OS proposal
  was greenfield described as improvement, and the estate's real weakness — retrieval reaching 7% of
  it — was in the reach of a mechanism it already had. (#41)
- **Then score the estate against a reference model, because a proposal only surfaces the gaps its
  author thought of.** Doing that found six more, including a practice-area roster with no row for the
  discipline the repository itself runs on — anchorable all along, and simply never rostered. (#44)
- **Ask where a document's content is allowed to come from, not only whether it is sound.** Every
  review checked the estate's claims; none asked what may be written into the memory every session
  loads from a page, a comment or a log fetched from outside it. (#44, risk #16)
- **A budget calibrated against a set that reaches nothing prices a session that reads nothing.**
  Measure what a session actually opens before trusting a ceiling. (#41)

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
- **A sweep that corrects the governed documents leaves the instructions pointing at the old world.**
  ADR-0037 deleted the code and fixed the docs; thirteen skill files went on naming the deleted files
  as though a reader could open them. `.claude/**` is loaded by every session and read by no gate —
  check it explicitly, or it keeps the previous estate alive. (#35)
- **Before believing a path-scan, resolve relative to the citing file, not to the repo root.** Half of
  a 121-hit sweep was citations that were correct all along. (#35)
- **If the subject already knows what the artefact is supposed to teach, the measurement is of the
  subject.** (#17)
- **A refined prompt can still be underspecified, and both default responses — guess, or ask in
  prose — are wrong.** Present the fork as a selectable list (§6). (#10)

### About code

- **Duplicated logic without a shared oracle will drift.** (#1)
- **Verify the toolchain itself, with the real commands, in CI.** Declared dev tooling was once
  mutually uninstallable and nothing had ever checked. (#2, #6)
- **An instantiated script drifts from the skeleton it came from.** (#4)
