---
id: program-state-of-project
title: "State of the Project — snapshot & improvement map"
type: program
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-program }
  - { type: governed-by, target: governance-root }
---
# State of the Project — snapshot & improvement map

> A **regenerated status snapshot** (non-authority): it *references* the authorities — ADRs
> (`10-decisions`), rules (`30-foundation`/`50-engineering`), the product model
> (`20-product-model`) and the backlog (`WORKFLOW.md`) — and never restates them as new truth
> (knowledge-architecture SSOT). Interpretive verdicts (% complete, practice grades) are
> estimates for steering, refreshed each iteration. A visual version is published as a private
> Artifact (see §6). **Snapshot: 2026-07-22.**

## 1. What the project is (one paragraph)

A project/workspace modeled as a **technology company** where **SCM is the operating
discipline** — the Global Context that governs a portfolio of Projects across all tech
branches, organized as a typed node+edge graph of Regions (ADR-0030; `20-product-model/
node-model.md`). Not a commercial product.

## 2. Completion by layer (estimate, for steering)

| Layer | State | Est. |
|---|---|---|
| Knowledge / Global Context (docs, 154 `CPT-*`, rules, ADRs, node model) | complete, gate-enforced | ~90% |
| Domain logic (TS) + calc models (Python) | real code; 0 Python tests, money not Decimal, ~30 TS/PY divergences | ~65% |
| Application (API, web UI, persistence, auth, ingest, gRPC, workspace/projects, monitoring) | scaffolds + governance only | ~2% |
| Per-tech-branch practice (AI/ML/Data/DevOps…) | only the existing engineering baseline | ~5% |
| **Overall vs the full ADR-0017/0030/0031/0032 vision** | | **~15%** |

## 3. Best-practices scorecard (verdict · evidence)

- **Clean Architecture** — *decided + partial*. Layers-as-packages exist; `domain` is
  framework-free (ENG-R2, true today); application/infrastructure rings are README-only and
  the boundary linter is unbuilt. (ADR-0018/0023, ENG-R1..R3)
- **SOLID / DRY / KISS / YAGNI** — *standard, reflected*. In `.claude/skills/engineering-standards`;
  domain is pure functions + single-responsibility modules; not formally audited.
- **DDD bounded contexts** — *partial*. 14 department contexts with aggregates; the modular-
  monolith module boundary (NestJS) is unbuilt. (ADR-0004/0023, ENG-R3)
- **Event Sourcing + CQRS** — *partial*. Inventory event log + projection built in-memory;
  durable event store unbuilt. (ADR-0005; P7)
- **Money precision (no float)** — *debt #1*. Decided Decimal end-to-end (ENG-R4/SCM-R8/ADR-0019)
  but TS code still used integer cents + `Math.round`; SQL uses `NUMERIC`. **P5 in progress**
  (see §5). Live rounding-mode bug being retired.
- **Immutability · Idempotency · Soft-delete** — *built* (SCM-R11/R12/R3).
- **UI design tokens / colour variables** — *specified only*. LED-cyan `#22d3ee`, octagon
  outline, interaction states and a11y are decided (ADR-0026); no UI/CSS/token set exists yet.
- **DB schema / data structure** — *authored, not deployed*. 15 `schema.sql` (per-dept + shared)
  with `NUMERIC` money, checks; conventions ISO-8601/UTC, GS1 UOM, soft-delete, event log,
  knowledge read model separate from project data (ADR-0024/0019/0005); no migrations/ingester.
- **Testing / TDD** — *partial*. 40 TS tests; 0 Python tests (U7); no golden vectors (U8);
  SCM-R13 mirror-coverage unmet.
- **Security (runtime)** — *gap*. Discipline-level protections exist (OSI-only supply chain,
  money integrity, idempotency, soft-delete, compliance logic, prompt-refinement gate PLT-R1);
  authN/authZ/RBAC, secrets management, audit wiring, input validation and tenancy are unbuilt
  (P7; candidate axis `30-foundation/security/`).
- **Knowledge governance** — *built, strong*. Tiered docs, one-way SSOT, append-only ADRs,
  stable IDs, 10 doc gates in CI, node model. The estate's strongest asset.
- **CI/CD / DevOps** — *partial*. GitHub Actions runs `make verify-full`; no deploy pipeline,
  containerization or observability.

## 4. Where improvement signals already come from

- `make verify` — gates + coverage census (fails on disconnected/undocumented knowledge).
- The **"Divergences surfaced"** section in each `25-concepts/<dept>/_index.md` (~30 TS/PY
  divergences to resolve — feeds U8/U15b).
- `docs/program/WORKFLOW.md` — the ordered U / P / W backlog with status.
- `docs/00-governance/risk-register.md` · `docs/program/improvement-register.md`.

## 5. Route (chosen path)

Three tracks, non-exclusive:
- **A — Harden the base:** U7 pytest suite · U8 golden vectors · U12 lint · **P5 Decimal money**.
- **B — Visible product (Stage A):** P3 ingester + read model + GraphQL · P4 Next.js octagon
  wiki · P6 gRPC calc service.
- **C — The workspace vision:** finish W2 (workspace/projects concept nodes) → W3 (workspace +
  projects + prompt gate) → W4 (real-time monitoring).

**Chosen (owner-directed 2026-07-22): partial A → C.** Do **P5 (Decimal money)** + **U8 (golden
vectors)** first — the money bug would contaminate any API/UI built on top — then advance on
**Track C (W3)**, pulling P3/P6 as C needs them.

**In progress:** **P5 slice 1** — the `@scm/shared` Decimal money core (see WORKFLOW P5). P5 is
sliced (L/high-risk): (1) shared money core + tests; (2) domain call-site migration by
department; (3) Python `Decimal` context; (4) `NUMERIC` columns + gRPC string encoding; (5)
golden vectors prove TS == PY == SQL (U8).

## 6. New-technology decisions still pending (owner-gated, per the speed/security rule)

Before adopting any of these I ask the owner with speed + security trade-offs: an **auth
library**, a **secrets vault**, a **container/orchestration** runtime, a **charting library**
for dashboards, and the **event/streaming** technology for real-time monitoring (W4). Everything
else is already decided and OSI (ADR-0002).

- **Visual dossier:** a private Artifact rendering of this snapshot is published from the
  session (octagon/LED-cyan console styling); regenerate it alongside this doc.
- **Governing refs:** `CLAUDE.md` · `10-decisions/README.md` (ADR-0001–0032) ·
  `50-engineering/rule.md` · `30-foundation/*/rule.md` · `20-product-model/*` · `WORKFLOW.md`.
