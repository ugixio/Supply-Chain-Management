---
id: program-workflow-archive
title: "Backlog — closed triages (archive)"
type: archive
owner: orchestrator
status: archived
since: 2026-08-03
updated: 2026-08-03
relations:
  - { type: part-of, target: index-program }
  - { type: governed-by, target: knowledge-architecture }
---
# Backlog — closed triages

> **Why this file exists, and it is not tidiness.** `docs/program/load-sets.md` prices what a session
> reads *together*, and the `planning` set reached its 20,000-word ceiling on 2026-08-03 during the
> file-by-file review. The manifest's declared exit for `planning` was *shorten the ADR index
> entries* — and measurement said that exit addressed the wrong term: `WORKFLOW.md` was **14,505** of
> the 20,142 words and the index slice only **2,427**. So the exit was named as not fitting rather
> than executed as written (known pitfall #29), and this is the instrument chosen instead: the same
> one the risk register already uses.
>
> **Nothing is deleted and no status changed.** These two triages are complete records of work that
> closed; a session asking *what should I do next?* does not need them, and a session asking *what
> was already decided about this marker?* comes here. `WORKFLOW.md` keeps a pointer so every
> reference still resolves.

### Triage of 2026-07-29 — what ADR-0037 did to this backlog

> **Why this block exists.** Phase L was voided explicitly when ADR-0037 landed. The Phase U and
> Phase P entries were not, and a file-by-file review of the estate found more than twenty of them
> still reading as live work — work that would have sent the next session to rebuild the
> application ADR-0037 deleted. A stale ⬜ is not a harmless leftover in a document whose whole
> purpose is telling a fresh session what to do next. Verdicts below; the entries keep their text.

| ID | Was | Now | Why |
|---|---|---|---|
| U3 | ⬜ | ✅ | The `CLAUDE.md` sections it deduplicated (§Critical Business Rules, §Code Standards) no longer exist — the contract was rewritten around the inclusion test, and it cites rule IDs rather than restating them. Done by rewrite. |
| U7 | 🟦 | ⛔ | The pytest suite and the TS coverage bar both governed deleted code. What survives is the Definition-of-Done requirement that a touched rule keeps its test, and the 26 Rust tests that honour it. |
| U8 | 🟦 | ✅ | The golden-vector mechanism landed (`tests/golden/money.golden.json`, read by `crates/scm-money/tests/golden_money.rs`). Its *purpose* — reconciling two languages — went away with the second implementation; the fixture stays because it pins the arithmetic. |
| U11 | 🟦 | ⛔ | The numbering collision was resolved by ADR-0029. The remaining item, splitting three agility/VaR functions into dept 10, has no functions left to split. |
| U11b | ⬜ | ⛔ | `Shipment.ts`, `TransportLane.ts` and the `python/NN_*` trees are deleted. The REACH item is real but belongs to a project: the obligation is stated as **CMP-R3**, and how a filer tracks an ECHA notification is its own design. |
| U12 | ⬜ | 🟦 | Rescoped, not void: a lint lane for one 175-line standards module buys nothing. It lands with the TypeScript that Phase M4 introduces, warnings-as-errors, in the same commit as the first NestJS module. |
| U13 | ⬜ | ⛔ | The `Shipment` type it would guard is deleted. **LOG-R3** still states the obligation; enforcing it is the implementing project's job, which is the whole point of ADR-0037. |
| U15 | 🟦 | ✅ | Item 1 was resolved by ADR-0028 (the exact inverse-normal is canonical, stated in CPT-0003). Items 2–7 are U15b's. |
| U15b | ⬜ | ⛔ | All seven divergences were disagreements *between two implementations*, and both are gone. The lesson is kept where it can still bite: **the same name over a different method** is the failure mode, and it is now a known pitfall in `evaluation.md`. |
| U16 | ⬜ | ⛔ | "No TypeScript implementation of Croston/SBA" is not a gap in a repository that holds no implementations. CPT-0006/0007/0009/0010 exist as nodes; that is the deliverable. |
| U17 | ⬜ | ⬜ | **Stays live.** Whether SCOR-DS *Make* and *Orchestrate* need departments is a knowledge question, not a code question, and ADR-0037 does not touch it. A 15th department still requires an ADR (id-registry §4). |
| U18 | 🟦 | ✅ | Closed the hard way: the 150,322 ungoverned words were deleted with the code they described (risk #7, closed). |
| U19 | ⬜ | ⛔ | CPT-0024 and CPT-0025 exist as concept nodes. "Implement them in whichever language ADR-0001 assigns" rests on the premise ADR-0037 superseded. |
| P1 | ⬜ | ✅ | `docs/50-engineering/` is materialized: `_index.md` plus the ENG-R family through ENG-R10. |
| P2 (original plan) | ⬜ | ⛔ | Superseded by what actually landed at P2. Half its layout (`packages/{domain,application,infrastructure}`, `services/calc`, `proto/`) was deleted three phases later. |
| P3 · P4 | ⬜ | ⚠ | **Owner decision needed**, and the only two entries here that are not mine to settle. ADR-0024/0025/0026 specify a Postgres read model, a GraphQL surface and an octagon wiki over `docs/`; ADR-0037 says the one application built here is monitoring. Both readings are defensible and they build different things. Raised with the options rather than guessed (PLT-R6). |
| P5 | 🟦 | ✅ | One exact-money implementation, `crates/scm-money`: `roundTiesToEven`, sum-preserving apportionment, overflow reported rather than wrapped. The TypeScript and Python mirrors that disagreed are gone. |
| P6 | ⬜ | ⛔ | The `scm.calc.v1` service and its proto are deleted. Python keeps its lane (ADR-0033/0035) and it now serves the monitoring platform's models, not an SCM calculator. |
| W2 | 🟦 | ✅ | The node model and the PLT family are live and gated (PLT-R1..R6; G4/G5/G6 enforce the graph). |
| W3 | ⬜ | 🟦 | Rescoped: the projects data domain and the GraphQL resolvers are Phase **M4**'s gateway work. The prompt-refinement gate inside it is already law — **PLT-R1** and **PLT-R6** — and is practised, not built. |
| W4 | ⬜ | ⛔ | Superseded by Phase M in full: M1 defines the delivery metrics as nodes, M2 the telemetry tier, M3 the ingester, M4 the dashboards. W4 *is* Phase M, described before Phase M existed. |
| C1 | 🟦 | ✅ | C1a–C1e swept all 160 nodes. The 2026-07-29 review found residue C1 missed — six nodes carrying benchmark *parameters*, and five figures needing a source or a project-decision label — and that residue is now fixed. A completed sweep is not a perfect one. |
| C2b | ⬜ | ✅ | Landed: QMS-R8 (corrective-action effectiveness), FEFO in CPT-0036, plan immutability in CPT-0150. |
| C4 | 🟦 | ✅ | C4 and C4b corrected the prose that described deleted code, across the docs and the operating layer. |
| M2 | 🟦 | ✅ | Five migrations, the rollup cascade, split-privilege roles and quotas, applied twice in CI against a real ClickHouse to prove idempotency. |
| M3 | 🟦 | ✅ | **M3a** the ingestion core (13 tests, no clock, no transport) and **M3b** the ClickHouse adapter (40 tests, no server needed to test any failure path). |

**Two further items the same review raised, both needing an owner decision rather than a fix:**

- ⚠ **The `implements` edge type is declared and never used.** `knowledge-architecture.md` §8,
  `20-product-model/node-model.md` §1 and `tools/verify.py` all carry it; zero documents use it.
  Post-ADR-0037 a concept node links to no implementation, so a live `implements` edge invites
  exactly the relinking ADR-0037 undid — and G4 would validate the first one happily. Retiring it
  changes the node/edge vocabulary, which knowledge-architecture §12 puts behind **an ADR**, so it
  is raised here rather than done. The alternative worth considering: keep it, reserved for the
  monitoring application's own nodes, which legitimately do trace to code this repository owns.
- ⚠ **`.claude/skills/**` KPI target tables** — swept on 2026-07-29 into "the decision plus what
  constrains it". Recorded here because the *class* is not closed: no gate can tell a target from a
  definition, so the next skill file added can reintroduce it (risk #13).

### Triage of 2026-08-02 — markers that stopped matching the estate

> **Why this block exists.** The 2026-07-29 triage swept Phases U, P, W, C and M. It did not reach
> **Phase L**, and it ran *before* M2/M3 landed, so two markers have been describing work as
> outstanding that is finished. A state-gathering sweep over the whole backlog found them by
> enumeration: 16 live markers read, 2 wrong. The rest were correct, including the two that look
> stale and are not — **U12** and **W3** are 🟦 by the 2026-07-29 ruling, each recording its state
> and its next step, which is what a 🟦 is required to do.

| ID | Was | Now | Why |
|---|---|---|---|
| L4 · L5 | ⬜ | ✅ | Delivered under Phase M, which is what "renumbered under Phase M when that work starts" anticipated. L4 (the ClickHouse telemetry tier) is **M2** — five migrations, the rollup cascade, split-privilege roles, applied twice in CI against a real server. L5 (the Rust ingestion workers) is **M3a/M3b** — 13 + 40 tests. Leaving them ⬜ tells a fresh session to build what exists. |
| L6 | ⬜ | ⛔ | Void as an L entry, live as **M5**: Docker images then Kubernetes, once two long-running services exist. One entry, not two, so the work is tracked in one place. |
| P2 | 🟦 | ✅ | Both slices landed 2026-07-20 with verify-full green. Its one recorded residual — the `07_order_management` / `13_order_management` merge — needs no domain call any more: ADR-0037 deleted both packages, closing risk #4 and voiding U11. A 🟦 whose next step has been overtaken is a ⬜ in disguise. |

**Owner decisions taken 2026-08-02**, recorded here because both were raised as ⚠ and both change
what gets built:

- **P3 · P4 — the octagon wiki stays live.** Asked as a selectable choice against "monitoring only"
  (PLT-R6), the owner kept it: ADR-0024 (Postgres read model), ADR-0025 (code-first GraphQL) and
  ADR-0026 (the octagon node-graph) remain in force. **Consequence for M4**, which is why this is
  recorded rather than just answered: the NestJS gateway serves **two** read surfaces — the
  knowledge read model built one-way from `docs/`, and the telemetry tier — so its module boundary
  and its drift guard are part of M4's scope from the start, not a later addition. The entries stay
  ⚠ only until their first slice is planned; the *decision* is no longer open.
- **W6b — no operational warehouse telemetry, and risk #14 is closed anyway.** The product stays
  project supervision (ADR-0031/0034/0036 unchanged, no new ADR). The owner separately chose to fix
  the defect that W6b would have exposed: today `samples_1m` computes `sumState`/`min`/`max`/p95
  only, so a **level** ingested through the cascade sums silently — a backlog of 40 read every ten
  seconds reports 240 per minute, in range, with nothing failing. The fix is a declared metric
  `kind` (flow · level · event-count) enforced at ingest, plus `argMaxState`/`anyLastState` in the
  rollup. It is worth doing without the scope change because the corruption is silent and the
  schema is young; it is queued as **M2b**.

- ⚠ **Branches — two steps are the owner's, 2026-08-02.** **ADR-0040 / ENG-R11** put the integration
  model in writing and `main` now exists at the same commit as the old trunk. What a session cannot
  do: **flip the default branch to `main`** (a repository setting with no API surface here) and
  **delete four stale refs** — `claude/bold-cannon-l7wtso` once the default moves, plus
  `feat/context-skeleton`, `fix/verify-rule-id-regex` and `feat/per-department-rules`, each carrying
  0 commits not already in the base. This environment's git proxy refuses `delete` with HTTP 403.
  Risk #3 closes when the default is `main`.
  **A third item joined the list 2026-08-03:** the first calendar tag. ADR-0046 adopts per-node
  digests plus an annotated `YYYY.MM` tag, and `git push origin refs/tags/2026.08` returns **HTTP 403**
  from the same proxy. The tag was created locally and dies with the container, so **the scheme is
  adopted and its first instance is pending** — one command for the owner:
  `git tag -a 2026.08 <sha> -m "…" && git push origin 2026.08`.

### Phase C — Clean the context after ADR-0037 (archived 2026-08-03)

> **Nine items, all closed.** Moved here when the `planning` load set reached its ceiling during the
> pre-M4 readiness check. The manifest's declared exit for `planning` names exactly this: WORKFLOW is
> the dominant term and its **closed phases are the supply**. Phase C is the largest fully-closed
> phase (3,010 words) and a session asking *what should I do next?* does not read it. Nothing was
> deleted or restated.

> The deletion is done; making the remaining knowledge consistent with it is not.

- ✅ **C1 · WHAT** — **Sweep the concept nodes for policy.**
  **C1a landed 2026-07-27 — the numeric policy is out.** Method: a detector for lines carrying a
  number *and* a normative word (target, threshold, tolerance, weight, band, default), minus
  citations, narrowed 169 flagged nodes to **47 real candidate lines in 37 nodes**, each then judged
  by hand. Removed: every "world-class ≥ X" bar (13 of them, one citing a `CLAUDE.md` section that
  no longer exists) · matching tolerances (0%/1%/2%) · the 25% carrying rate and its 20–30% "band" ·
  the 85–90% space-utilization band · warehouse throughput and dock-to-stock benchmarks ·
  MPS stability > 0.85 · fill ≥ 98% / backorder ≤ 2% · the 15% restocking default · compliance-score
  weightings · C2C rating bands · the 0.5% tracking dead band · α = 0.3 smoothing · the 85%
  capacity-strain onset.
  **Kept, because a regulator fixes them:** REACH 0.1% w/w (Reg. 1907/2006), CSDDD >5,000
  employees ∧ >€1.5B from 26 Jul 2029 (Directive 2026/470), CBAM 50% quarterly holding. Worked
  examples keep their illustrative numbers; mathematical domains (`α ∈ (0,1)`, `n ≥ 1`) are not
  policy.
  **Two nodes were policy end to end and were rewritten as definitions:** CPT-0060 (scorecard) now
  states only `Σwᵢ = 1` and why a compensatory composite must keep gates outside it; CPT-0061
  (rating bands) states only that a partition must be exhaustive, non-overlapping and explicit
  about boundary inclusivity.
  **C1b landed 2026-07-27 — no node compares deleted implementations any more.** All `(PY)`/`(TS)`
  annotations are gone, and several were hiding a real question rather than a formatting wart:
  · **HHI** never said which input scale it used. The published index is computed on **percentage
  points** (0–10,000) — that is definitional, not conventional, and computing it on fractions
  makes every published reference value read a factor of 10,000 off. Stated once, with the
  consequence.
  · **CV/XYZ** hid the **estimator** choice: population versus sample standard deviation differs
  by ~5% on ten observations, enough to move a borderline SKU across a class boundary. Now named
  as a project decision that must be applied consistently, because two SKUs measured differently
  are not comparable. Its 0.10/0.25 class table also survived C1a — the detector missed it
  because the number and the normative word sat in different table rows. **Detector blind spot
  worth remembering.**
  · **Safety stock "days of supply"** was two different formulas under one name (a flat day count
  versus the lead-time spread `LT_max − LT_avg`). Both survive as legitimate definitions; the node
  now insists the project say which it means, and the worked example shows the same SKU getting
  250 or 150 units.
  · **EAL** allowed impacts in currency and as a fraction of revenue in the same sum, and summed
  correlated scenarios. Both now stated as errors.
  · **Stock-balance projection** — where the non-negativity check belongs is recorded as a real
  choice: refusing the movement keeps the ledger always-valid, letting the projection report a
  negative surfaces the upstream gap. A *reader* of an event log can only do the latter.
  · **ABC slotting**, **risk matrix 5×5** and **Kraljic** had their break-points, bands and axis
  midpoints removed; what remains is the structure (rank-then-cut; an ordinal product is not an
  interval scale; a 2×2 on two dimensions).
  · **AQL** large-lot behaviour is ISO 2859-1 table data and is cited as such rather than
  described as a fallback.
  Also: the two department "Divergences" sections became **Regulatory drift to watch**, keeping
  the CSDDD/CBAM/REACH/EUDR movements and dropping the code-gap notes.
  **Lesson recorded:** three scripted line replacements produced broken prose that the gates
  cannot see. Prose edits get read back; only structural edits get scripted.
  **C1c remaining:** a **Project-chosen inputs** section on every node that needs values — about
  a dozen have one now, out of 154.
- ✅ **C2 · WHAT** — **All 14 department rule families swept and rewritten (2026-07-27).** This was
  where the bulk of the remaining problem sat, as suspected: the families had been extracted from
  the `throw` guards of the deleted code, so most "invariants" were invented workflows or field
  checks citing `.ts` files. Of **70** rules, **45 retired**, **25 survived**, **13 new IDs**
  allocated for externally-fixed statements that had never been written down.
  **What the sweep surfaced as genuinely fixed and previously unstated:** IAS 2's
  lower-of-cost-and-NRV rule and its **LIFO prohibition** (FIN-R4) · that only *non-recoverable*
  tax capitalizes into inventory cost (FIN-R5) · the Incoterms **sea-only** restriction on FAS/FOB/
  CFR/CIF, so naming one for an air movement is an error not a shorthand (LOG-R1) · dangerous-goods
  declaration per mode, a criminal matter rather than a data-quality one (LOG-R3) · chargeable
  weight as the greater of actual and volumetric (LOG-R4) · that an **ISO 2859-1 plan is read from
  the table, never interpolated**, because its operating-characteristic curve only holds for the
  tabulated combinations (QMS-R5) · that accepting a *sample* is not accepting a lot (QMS-R6) ·
  that a defect rate needs its **opportunity base** or PPM and DPMO get compared (QMS-R7) · that
  EUDR country risk is **read from the Commission benchmark**, so a hardcoded list is wrong the
  moment it is revised (SDV-R6) · that **absence of evidence is not evidence of compliance** — an
  unevidenced supplier is *unknown*, and flooring it at a mid-range score converts silence into
  adequacy (SDV-R5) · that a BOM must be **acyclic** or explosion never terminates (SPL-R1) · that
  a reorder point **contains** its safety stock by definition (INV-R1) · that a perfect-order rate,
  being a conjunction, is at most its worst component (ORD-R6) · and that an **ordinal product
  stays ordinal**, so risk scores may not be averaged (RSK-R5).
  **What was retired, by kind:** ~20 invented status machines and lifecycle guards · ~15 field
  range checks (`confidencePct ∈ [0,100]`, priority `∈ [1,5]`, horizon `∈ [1,52]`) · 4 money
  representation rules that belong to **ENG-R4** · the over-receipt tolerance and the
  mandated-safety-stock-method rules, which were policy.
  **Two corrections made during the sweep:** an ID must never be redefined — I first reused
  a retired ID for a new statement and had to reallocate it — three times over — and my first
  count of the retirements was wrong. The reallocations are recorded in the id-registry, which is
  the one place allowed to name a retired ID; the registry now carries the
  verified figures.
- ✅ **C2b · WHAT** — Several retired rules named a principle worth keeping *somewhere*: FIFO/FEFO
  picking discipline, corrective-action effectiveness verification, immutability of a committed
  plan. Each belongs to a concept node or a project's own process, not to a rule file — place them
  deliberately rather than letting them vanish.
- ✅ **C3 · WHAT** — **Stale rule citations swept, and mechanized so it cannot recur (2026-07-27).**
  ADR-0037 and Phase C2 retired **52** rule IDs; the estate carried **141 citations** of them across
  82 files. A citation of a retired ID is invisible to G4 — it is not a broken link, it silently
  resolves to nothing and reads as law — so this was worth a gate, not just a pass.
  **New gate G11:** no document cites a withdrawn rule ID. The retirement tables are the
  machine-readable source, read from the **first column only** (an ID named in the *why retired*
  prose is a live rule being pointed at). Exempt, on principle rather than convenience: the rule
  file that declares the retirement, the **id-registry** (a retirement is an allocation fact), and
  the **ADRs** (append-only history — editing an old decision to remove an ID would falsify it).
  **Substitutions were judged, not blanket-renamed** — a money rule split into an identity and a
  code duty; an inventory rule kept its physical impossibility and shed its policy exception;
  non-negativity bullets were deleted outright because a mean of absolute values is non-negative by
  arithmetic; invented lifecycles became "the project's own lifecycle". The full old→new map lives
  in the **id-registry**, which is the allocation authority and the one place allowed to name a
  withdrawn ID.
  **I repeated my own recorded mistake.** I ran broad regex substitutions over prose again and
  corrupted five places — including, with some irony, the registry line that *declares* the
  retirements, which came out asserting that a live inventory rule had been retired. Caught by
  reading the diff, fixed by hand. **G11 then caught 36 citations the sweep had missed**, and
  finally caught this very backlog entry naming withdrawn IDs while explaining them. That is the
  argument for the gate: the script was neither sufficient nor safe, and only the gate was
  reliable.
- ✅ **C4 · WHAT** — **Prose that still described deleted code (2026-07-27).**
  **The agent definitions came first, because they instruct future work** — an agent told to build
  `packages/domain` aggregates would have sent the next session straight back into the mistake.
  Four rewritten: `calc-engineer` (Python is the tools layer, and it now carries the lesson that a
  policy default in a signature is how one company's habits get inherited), `domain-knowledge`
  (leads with the inclusion test), `backend-engineer` (the only door to the frontend, serving
  monitoring), and the agents README.
  **A defect that would have propagated:** `templates/concept.md` still instructed authors to add
  an `## Implementations` section — which **G10 now rejects** — so every node created from it would
  have failed the build. It now teaches the current contract: unique CPT number, non-empty
  `## References`, no implementations, a **Project-chosen inputs** section, illustrative worked
  numbers, and a warning that G11 fails on a retired rule ID.
  **Risk register reconciled:** seven of eleven risks were **closed by the deletion itself** —
  the untested Python tree, the TS/PY divergence, the duplicate order-management packages, the
  heavy ML toolchain, the 84% of prose sitting outside the governed tree, the `IMPLEMENTATION.md`
  files specifying a different system (SAP/Superset/Airflow — itself evidence of the drift), and
  the spec-versus-code z-score contradiction. G10's structural blindness is superseded.
  **And the risk ADR-0037 created is now recorded as #11:** no gate can tell a standard from a
  plausible-looking invention. G10 checks that a source is *cited*, not that the content matches
  it. That is the residual, and it is how the original problem started.
  **ENG-R2 retired** — it governed `packages/domain`, which no longer exists; its intent survives
  as ENG-R10.1. ENG-R1's ring names updated to `apps → adapters → core`.
  Structural indices corrected: the knowledge-architecture allowlist, `docs/_index.md`,
  `40-contexts/_index.md`, the operating-model lane diagram, and the dept-03 section that framed
  two concepts as "specified but not implemented" (a code-state claim) rather than as measures of
  the planning process.
- ✅ **C4b · WHAT — the operating layer swept (2026-07-27).** The 22 `.claude/skills/`, the four
  `.claude/commands/`, the agent definitions and the root `README.md`. They are the department
  know-how a project consults for *how* to implement, so they stay — but under the inclusion test.
  Measured first: only **13** policy lines by the number-plus-normative-word detector, far fewer
  than feared, because most of the drift was **stale paths**, not stated policy.
  **G11 had been giving a false green.** It only scanned front-matter documents, so the skills
  tree cited retired rules unseen; extended to `.claude/**` and `CLAUDE.md`, it immediately found
  **13** more (10 in agents/skills, then 3 in `testing-quality` alone). *A gate over part of the
  estate certifies the part it can see.*
  **The two worst files were the two most-read.** `supply-chain-core/SKILL.md` carried
  `Money = { amount: number }`, the `KG`/`L`/`M` codes `CLAUDE.md` names as an anti-pattern, the
  $5,000 threshold, a "World-Class KPI Benchmarks" table, a `service_level: float = 0.98` default
  in a signature, and a test **asserting round-half-up** against SCM-R14 — rewritten. The root
  `README.md` — the front door — still opened with a `src/departments/` tree, `npm test`, a
  "World Benchmark" KPI table and 26 "Algorithms Implemented" naming deleted `.ts` files;
  rewritten around the inclusion test.
  **Half-edits found by reading the diff back** (the third time this lesson has paid): the ABC
  and defect-classification tables had policy stripped from the *first* row and left in the rows
  below, which reads as though those numbers were the standard. Also fixed: a known-pitfalls entry
  left dangling mid-sentence around a deleted constant and a deleted test path.
  **Dead JS test estate removed:** `jest.config.js` still mapped the deleted `@scm/domain`, and
  `package.json` declared `test`/`test:unit`/`test:integration` over a `tests/` tree holding only
  the Rust golden fixture. Jest, ts-jest, eslint (never configured), `ts-node` and `@types/uuid`
  dropped; lockfile regenerated. `turbo.json` and `tsconfig.json` paths cleaned. **A runner that
  passes because it found nothing is worse than no runner — it reads as coverage.**
- ✅ **C1d · WHAT — the divergence sections were a hiding place for policy (2026-07-27).**
  47 concept nodes still described differences between the **two deleted implementations**. That
  framing is why C1a missed real policy: its detector needed a number and a normative word on the
  same line, and `PY bands: <0 EXCELLENT · ≤30 GOOD` matches neither pattern. Removed here — the
  cash-to-cash rating bands, the bullwhip severity thresholds, the 5×5 risk-matrix level cuts,
  three competing AP matching tolerances, the 10% budget-variance bar, `Cpk ≥ 1.33 capable`, the
  0.5% bias dead band C1a had *reported removing*, and the 5% over-receipt default — the original
  ADR-0037 example, still sitting in a symbol table.
  **Questions the divergences were avoiding, now answered:** the σ estimate decides *which index
  you computed* (within-subgroup → Cp/Cpk, total-sample → Pp/Ppk — different names for exactly
  this reason); consensus forecasting is **two stages**, not two implementations; days-of-supply
  safety stock is two formulas, one of which collapses to zero on stable lead times; excluding
  in-transit shipments flatters OTD and the two bases never reconcile.
  **A correctness fix:** the statistical safety-stock example still used `z = 1.65` from the lookup
  table ADR-0028 retired in favour of the exact inverse normal.
  **G12 added — a rule citation names an ID.** `**FIN-R***` reads as law and resolves to nothing;
  it was invisible to G4 (not a broken link), G3 (not a duplicate) and G11 (not a retired ID). Most
  of the 47 stood in for *lifecycle* rules retired with the deleted application, so the wildcard
  was concealing precisely what it appeared to cover. The gate found one more in the core rule file
  itself, and was verified by planting a wildcard and watching it go red.
  **Eight `## Governing rules` sections were empty** — a heading promising law and delivering none.
  Filled with what actually governs each forecasting method (DMD-R6 on undefined percentage error,
  DMD-R9 on horizon and bucket, and Holt-Winters' two-season requirement as arithmetic).
  **The scripted-edit lesson paid for the fourth time:** four replacements left dangling tails
  because the original line continued onto the next. Caught by reading the diff, fixed by hand.
- ✅ **C1c · WHAT — the questions a project must answer, named (2026-07-27).** Every node that
  leaves a value to the project now carries a **Project-chosen inputs** table: **58 of 154**, up from
  9. The rest are pure identities (conservation, a sum, a ratio of two given quantities) and
  correctly have no free parameter — the section is omitted rather than filled with "none".
  Measured by cue phrase rather than guessed: 49 nodes said "the project must choose this" in prose
  while giving the reader nothing to scan.
  **A recurring second row nobody thinks of:** the *population, period or basis*. Two teams
  computing the same formula over different denominators disagree while both being right — labour
  productivity per paid/present/on-task hour, PPM over received/inspected/shipped units, OTD against
  requested/promised/confirmed dates, LTIFR per 200,000 or 1,000,000 hours (a factor of five).
  **Three more surviving targets, found only because the table forced the question:** MPS stability
  "below the 0.85 bar", a PPM target of 500, and `PO_APPROVAL_THRESHOLD_CENTS = 500,000` still shown
  as *the* worked example while the prose above it said the threshold was project-chosen. Showing
  the invented number is how it gets copied.
  **And two more stale z-values:** `z = 1.65` from the lookup table ADR-0028 retired, in the
  Average-Max and combined-variability examples. Correcting the combined example changed its
  conclusion (93 units of under-buffering, not 95).
  `templates/concept.md` aligned to the table form so new nodes inherit it.
- ✅ **C5 · WHAT — the regulatory framework was stating superseded law (2026-07-27).** Verified
  against the instruments themselves, not against the repository's own summaries — and the document
  was **wrong about CSDDD on three separate points**:
  it published the original three-phase scope (2027/2028/2029 at 5,000/3,000/1,000 employees), which
  **Directive (EU) 2026/470** replaced with a **single band — >5,000 employees ∧ >€1.5bn, from
  26 Jul 2029** (transposition 26 Jul 2028; roughly 13,000 undertakings became roughly 6,000);
  it stated penalties of **up to 5%** of worldwide turnover, now capped at **3%**;
  and it did not record that the **harmonised EU-wide civil liability regime was deleted**, so
  exposure now genuinely differs by Member State.
  **The catalogue was better than its own reference document** — CPT-0093 already recorded the
  Omnibus supersession — but it was *structured around the superseded test*, with the current law in
  a drift note underneath. A project reading its Formula section would have implemented the wrong
  directive. Current law now leads; the old phasing is kept below it, labelled as superseded and
  marked do-not-implement.
  **Rewritten around what the document is for:** the reference list behind the `CLAUDE.md` standards
  table, with a **verification date per entry** and a warning that the EU entries have changed three
  times in eighteen months. Added the instruments the catalogue cites but the framework had never
  listed — CBAM, EUDR, CSRD, IAS 2, ISO 2859-1, UN/ECE Rec 20, the ISO date/currency/country
  standards, IEEE 754 and the per-mode dangerous-goods regimes. Removed every `src/…` implementation
  reference and field name, and dropped the Gartner and McKinsey sections: a consultancy maturity
  model is not a standard, since an organisation can reasonably decline to use one.
  **Two more surviving thresholds found in passing:** the 85% space-utilization band C1a reported
  removing (still in an output description) and a 5%-of-exposure recommendation band in the SCOR
  agility node.
  **G12 had a blind spot of its own**, found while fixing a citation it should have caught:
  `**SCM-R7 / CMP-R***` escaped because the bold span opened on the *other* rule in the sentence.
  Narrowed to the bold citation form and widened to catch that shape; verified against both.
