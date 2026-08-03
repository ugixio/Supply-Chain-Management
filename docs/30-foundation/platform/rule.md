---
id: rule-platform
title: "Rules — Platform / Workspace (PLT-R*)"
type: rule
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-08-03
relations:
  - { type: part-of, target: index-foundation }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: rule-scm-core }
---
# Rules — Platform / Workspace

> Cross-cutting law for the **workspace itself** and **every project** in it — the layer
> above the 14 SCM departments (ADR-0030 tech-company operating model; the Node Model,
> `20-product-model/node-model.md`). IDs append-only (family `PLT`, id-registry §1).
> Inherited `SCM-R*` / `ENG-R*` are referenced, never restated. Where a doc gate already
> enforces a rule at the knowledge layer, it is named; the application layer (W3+) must keep
> the same invariant in code.

## Invariants (NEVER violated — each verifiable)

- **PLT-R1 — Prompt-refinement gate (ADR-0032):** a user prompt is **improved first, then the
  improved prompt is executed**; the original and the improved prompt are both retained
  (traceability). No path executes an unrefined prompt. Enforcement surface is the platform
  runtime (assumption A4, owner-confirmable). This is the incoming-quality control on
  instructions — the SCM incoming-inspection analogue (dept 08) applied to the input itself.
- **PLT-R6 — Improvement-recommendation gate (ADR-0038):** two obligations, one standing and one
  triggered.
  **(a) The search is always on.** Every task carries a search for a better implementation *within
  the lanes already adopted* — algorithmic complexity, compute and memory cost, data-structure and
  boundary choice, clean-code and structural quality, security. Finding nothing is a valid result;
  **not looking is not**. A recommendation may never introduce a new language, framework, service or
  out-of-lane dependency: that is **ADR-0002 / ENG-R8** and takes its own decision.
  **(b) What the request left open is chosen, not guessed.** When a detail is absent whose two
  plausible readings would produce **different work**, it is presented as a **selectable list of
  recommended options** — each stating what it means and what it costs, recommendation first — never
  guessed and never buried in prose. Selected options are implemented in the same turn under the
  normal gates; declined ones are recorded in `program/improvement-register.md` as `accepted-as-is`
  with the reason, so the same recommendation is not re-proposed. Extends **PLT-R1** from refining
  the prompt to resolving what the prompt left open.
- **PLT-R2 — Projects reference the Global Context read-only:** a Project **never mutates** a
  Global Context node. Project-specific change lives only in the project's **overlay**
  (project-scoped nodes + parameter/threshold overrides); reads resolve *global node, then
  overlay override*. Preserves the one-way SSOT (ADR-0024 / ENG-R7). A write path from a
  project into `docs/`-sourced knowledge is a violation.
- **PLT-R3 — Everything is connected (no orphan node, no dangling edge):** every node in the
  workspace graph is reachable via `part-of` to its region index, and every typed edge
  resolves to an existing node. Checked at the knowledge layer by **G4 (link integrity), G5
  (no orphans), G6 (authority acyclicity)**; the projected read model (ADR-0024) and the
  application graph must preserve it (a node with no edge, or an edge to a missing node,
  fails).
- **PLT-R4 — Everything is typed:** every node declares a `type` from the controlled
  vocabulary (knowledge-architecture §8) and every edge a relation kind from the controlled
  set; untyped nodes or free-text relations are rejected (**G2 front-matter validity**). No
  node or edge exists outside the type system.
- **PLT-R5 — One region per project, always attached:** a Project belongs to exactly one
  **tech branch** (ADR-0030) and its region attaches to the Global Context by at least one
  reference edge — no free-floating project, no project spanning two branches at the top
  level (sub-work in another branch is a linked node, not a second home).

- **PLT-R7 — Governing knowledge is selected and declared, never assumed (ADR-0045):** no project
  uses the whole context. Before development, the parts that apply are **chosen and reported to the
  owner**. Knowledge nobody named does not govern; no reader can tell omission from decision.

## Anti-states (the system must never allow)

- An unrefined prompt reaching execution (PLT-R1).
- Development under unnamed governing knowledge (PLT-R7).
- A project writing to, or forking-and-editing, Global Context knowledge (PLT-R2).
- Guessing a detail whose absence changes the result, or asking for it in prose when a selectable
  list is required (PLT-R6).
- A recommendation list padded with options that could not honestly be taken, or one that smuggles in
  a new technology (PLT-R6 / ENG-R8).
- Re-proposing a recommendation already recorded as declined (PLT-R6).
- Handing back a choice that is the implementer's — which loop, which name, which library inside an
  adopted lane — as though it were the owner's (PLT-R6).
- A node reachable from nothing, or an edge pointing at a missing node (PLT-R3).
- A node without a declared type, or an untyped/free-text relation (PLT-R4).
- A project with no branch, two top-level branches, or no link to the Global Context (PLT-R5).

## Inherited rules (referenced, not restated)

- **ENG-R7 / ADR-0024** — the read model is rebuilt one-way from `docs/`; `docs/` stays SSOT
  (PLT-R2 depends on this).
- **ENG-R1** — inward-only dependency direction; the `workspace`/`projects` bounded contexts
  live in the application/interface rings, never in `domain` (ADR-0018/0023).
- **SCM-R3** — soft-delete for records; project data deletion follows the same discipline.

## Materialization status

- **PLT-R1** is the recorded decision (ADR-0032); its **runtime enforcement + refinement
  criteria** are built at W3 (Stage B). PLT-R2..R5 are enforced at the knowledge layer today
  (G2/G4/G5/G6) and must be carried into the application layer as it is built. Each PLT-R gets its
  test when its code lands — a build-time discipline, so it belongs to the `ENG-R*` family.
- **PLT-R6 is not mechanically checkable**, and saying otherwise would be the false comfort this
  estate has already paid for. Like **G8** (English-only) it is a review gate: the anti-states above
  are its checklist, and the question craft it depends on is in
  [program/evaluation.md](../../program/evaluation.md) §6. What *is* checkable is its output — a
  declined recommendation leaves a row in the improvement register, so a gate-that-never-fires and a
  gate-that-fired-and-was-declined are distinguishable after the fact.
