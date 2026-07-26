---
id: program-state-of-project
title: "State of the Project — snapshot & improvement map"
type: program
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-26
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
> Artifact (see §6). **Snapshot: 2026-07-26.**

## 1. What the project is (one paragraph)

A project/workspace modeled as a **technology company** where **SCM is the operating
discipline** — the Global Context that governs a portfolio of Projects across all tech
branches, organized as a typed node+edge graph of Regions (ADR-0030; `20-product-model/
node-model.md`). Not a commercial product.

## 2. Completion by layer (estimate, for steering)

| Layer | State | Est. |
|---|---|---|
| Knowledge / Global Context (docs, 153 `CPT-*`, rules, ADRs, node model) | complete, gate-enforced | ~90% |
| Domain logic + calc models | real code (12,388 TS / 12,771 PY lines); Decimal money core landed both sides, Python tests in CI, first divergence closed; ~29 TS/PY divergences left — **and the TS half is now scheduled for retirement into the Rust core (ADR-0035)** | ~60% |
| Application (API, web UI, persistence, auth, ingest, gRPC, workspace/projects, monitoring) | scaffolds + governance only | ~2% |
| Per-tech-branch practice (AI/ML/Data/DevOps…) | only the existing engineering baseline | ~5% |
| **Overall vs the full ADR-0017/0030/0031/0032 vision** | | **~15%** |

## 3. Best-practices scorecard (verdict · evidence)

- **Clean Architecture** — *decided + partial, innermost ring changing owner*. Layers-as-packages
  exist; `packages/domain` is framework-free (ENG-R2, true today); application/infrastructure rings
  are README-only and the boundary linter is unbuilt. **ADR-0035 moves the innermost ring to
  Rust** — the direction is unchanged, the language of the core is not (ENG-R10).
  (ADR-0018/0023/0035, ENG-R1..R3, ENG-R10)
- **SOLID / DRY / KISS / YAGNI** — *standard, reflected*. In `.claude/skills/engineering-standards`;
  domain is pure functions + single-responsibility modules; not formally audited.
- **DDD bounded contexts** — *partial*. 14 department contexts with aggregates; the modular-
  monolith module boundary (NestJS) is unbuilt. (ADR-0004/0023, ENG-R3)
- **Event Sourcing + CQRS** — *partial*. Inventory event log + projection built in-memory;
  durable event store unbuilt. (ADR-0005; P7)
- **Money precision (no float)** — *largely retired*. `decimal.js` core in `@scm/shared`
  (`ROUND_HALF_EVEN`, sum-preserving `allocateMoney`) mirrored in `services/calc/shared`; the four
  live `Math.round(amount * factor)` sites (goods receipt, landed cost, inventory valuation, risk
  exposure) migrated. Remaining: `NUMERIC`/gRPC-string end-to-end proof (P5 slices 4/5) — and the
  two mirrors collapse to **one Rust implementation** at L2. (ENG-R4/R5, SCM-R8, ADR-0019/0035)
- **Immutability · Idempotency · Soft-delete** — *built* (SCM-R11/R12/R3).
- **UI design tokens / colour variables** — *specified only*. LED-cyan `#22d3ee`, octagon
  outline, interaction states and a11y are decided (ADR-0026); no UI/CSS/token set exists yet.
- **DB schema / data structure** — *authored, not deployed*. 15 `schema.sql` (per-dept + shared)
  with `NUMERIC` money, checks; conventions ISO-8601/UTC, GS1 UOM, soft-delete, event log,
  knowledge read model separate from project data (ADR-0024/0019/0005); no migrations/ingester.
- **Testing / TDD** — *partial, improving*. TS unit suites plus the **first enforced Python
  tests in CI** (`make test-py` in `verify-full`, `requirements-dev.txt`, setup-python in the
  workflow — U7) and the **golden-vector mechanism** (U8): one fixture
  `tests/golden/money.golden.json` read by both Jest and pytest, so a TS/PY divergence fails the
  build instead of being discovered later. SCM-R13 mirror-coverage still unmet estate-wide.
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
- The **"Divergences surfaced"** section in each `25-concepts/<dept>/_index.md` (~29 TS/PY
  divergences left to resolve — feeds U8/U15b, and each one is a ported-unit acceptance test at
  L2/L3).
- The **golden vectors** (`tests/golden/*.json`) — the only place a cross-language disagreement
  becomes a red build; also ADR-0035's Rust↔Python contract tests.
- `docs/program/WORKFLOW.md` — the ordered U / P / W / L backlog with status.
- `docs/00-governance/risk-register.md` · `docs/program/improvement-register.md`.

## 5. Route (chosen path)

Three tracks, non-exclusive:
- **A — Harden the base:** U7 pytest suite · U8 golden vectors · U12 lint · **P5 Decimal money**.
- **B — Visible product (Stage A):** P3 ingester + read model + GraphQL · P4 Next.js octagon
  wiki · P6 gRPC calc service.
- **C — The workspace vision:** finish W2 (workspace/projects concept nodes) → W3 (workspace +
  projects + prompt gate) → W4 (real-time monitoring).

**Chosen (owner-directed 2026-07-22): partial A → C, now preceded by Phase L.** Track A's money
work is done where it mattered most (see §3) and U7/U8 are live. The owner then set the lane and
core direction (ADR-0033/0034/0035/0036), which inserts **Phase L** ahead of the rest: the core
moves to **Rust**, Python becomes the **tools layer**, TypeScript keeps only NestJS/Next.js, and
the ClickHouse telemetry tier is designed for tens of thousands of supervision series.

**Landed since the last snapshot:** U14 (118 concept nodes, all 14 departments `enforced`) ·
W2 (node model + PLT rules) · P5 slices 1/2 (Decimal core + four migrated sites) · U7 (Python
tests in CI) · U8 (golden-vector mechanism + first divergence closed: refund = two-step
quantization, `ROUND_HALF_EVEN`) · L0/L1 (ENG-R8/R9/R10 + ADR-0033..0036).

**Next:** **L2 — the Rust money core.** Its acceptance criterion already exists:
`tests/golden/money.golden.json` must pass unchanged from a Rust reader alongside the Jest and
pytest readers. Then L3 (collapse the 49 duplicated calculations as the core absorbs them),
L4 (ClickHouse per ADR-0036), L5 (Rust ingestion), L6 (Docker → Kubernetes) — with Track C (W3)
pulled in as the workspace layer needs it.

## 6. New-technology decisions still pending (owner-gated, per the speed/security rule)

Adopted since the last snapshot (owner-directed): **Rust** (core — ADR-0035), **ClickHouse**,
**Docker**, **Kubernetes** (ADR-0034). Still owner-gated, asked with speed + security trade-offs
before adoption: an **auth library** (note: Zitadel went AGPL in 2025 — licence check first), a
**secrets vault** (Vault is BUSL → **OpenBao**), a **charting library** for dashboards, and the
**broker/cache** pair for monitoring (NATS/Kafka + Valkey), which ADR-0034/0036 keep gated until
measurement shows the Rust ingester plus ClickHouse cannot absorb the rate. Everything else is
already decided and OSI (ADR-0002).

- **Visual dossier:** a private Artifact rendering of this snapshot is published from the
  session (octagon/LED-cyan console styling); regenerate it alongside this doc.
- **Governing refs:** `CLAUDE.md` · `10-decisions/README.md` (ADR-0001–0036) ·
  `50-engineering/rule.md` · `30-foundation/*/rule.md` · `20-product-model/*` · `WORKFLOW.md`.
