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
