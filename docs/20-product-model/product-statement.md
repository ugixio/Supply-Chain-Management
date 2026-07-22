---
id: product-statement
title: "Product Statement — what the platform is"
type: product-model
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-product-model }
  - { type: governed-by, target: index-adr }
  - { type: refines, target: glossary }
---
# Product Statement

> The authoritative WHAT of the product, materialized from the owner's direction
> (2026-07-22) and recorded per the plan⇄context rule (ADR-0010). Concepts are **defined
> here** and referenced by stable name everywhere else. Load-bearing scope choices carry
> **assumption tags (A1/A2/A3)** ratified in ADR-0030/0031 — until ratified they are the
> working default, not settled law.

## 1. What the product is

A **platform** built in two layers:

1. **Global Context** — the estate's governed supply-chain knowledge (the `docs/` tier
   tree, the `CPT-*` concept catalogue, the `SCM-R*`/department rules) exposed as a
   **read-only, versioned knowledge substrate** with a **wiki** front end (the octagon
   node-graph, ADR-0026). `docs/` remains the single source of truth; the served graph is a
   one-way projection (ADR-0024).
2. **Workspace** — a tenant space containing **Projects**. A project is a unit of work that
   **consumes** the Global Context (references its concepts, rules and calculations by
   stable ID) and holds its own transactional data. Projects never mutate the Global
   Context.

A future, complementary third layer (**Monitoring**, ADR-0031) adds real-time dashboards
and metrics over a project's development and progress.

## 2. Who it serves

Supply-chain and operations teams who need (a) a trustworthy, citable body of SCM
calculations, rules and regulatory logic — the Global Context — and (b) a place to apply
it to concrete pieces of work — Projects — without re-deriving the domain each time.
**[A1]** the domain is supply chain for now; a domain-agnostic context engine is reserved
for a future ADR.

## 3. Delivery form

Full-stack web application on the recorded stack (Next.js · NestJS code-first GraphQL ·
PostgreSQL · Python calc core over gRPC — ADR-0017/0020/0022/0025). Staged:

- **Stage A (exists / in build):** the Global Context wiki — octagon node-graph served from
  the one-way Postgres read model of `docs/`.
- **Stage B (this direction):** the Workspace + Projects layer — a new bounded context with
  its own persistence, tenancy and lifecycle, reading the knowledge read model and
  referencing global nodes by ID.
- **Stage C (future, complementary):** the Monitoring connector — dashboards + metrics over
  project development, metrics defined as `CPT-*` nodes.

## 4. Core concepts (defined here; referenced elsewhere)

| Concept | Definition | Authority |
|---|---|---|
| **Global Context** | The read-only, versioned SCM knowledge substrate (`docs/` SSOT + `CPT-*` + rules), surfaced as a wiki. | ADR-0030 |
| **Workspace** | Top-level tenant space that contains Projects. | ADR-0030 |
| **Project** | A unit of work that references the Global Context by stable ID and owns its transactional data; cannot mutate the context. | ADR-0030 |
| **Project Overlay** | A project's local layer of project-scoped concepts and parameter/threshold overrides that reference — never rewrite — global nodes. Reads resolve *global, then override*. **[A2]** | ADR-0030 |
| **Connector** | Ingests development/progress signals for a project (external dev tools and/or internal project data). **[A3]** | ADR-0031 |
| **Monitoring / Dashboard** | Near-real-time rendering of project development metrics. | ADR-0031 |
| **Delivery Metric** | A progress/velocity calculation over project signals, defined as a `CPT-*` concept node like any other calculation. | ADR-0031 |

## 5. Invariants this statement commits to

- **Knowledge SSOT is one-way (ADR-0024):** projects read the Global Context; they never
  write to it. Global corrections propagate to all projects; project overrides live only in
  the project's overlay.
- **One calculation catalogue (ADR-0015):** delivery/monitoring metrics are `CPT-*` nodes —
  no parallel metric registry.
- **Platform ≠ department:** workspace/project/monitoring are platform bounded contexts,
  outside the 14-department SCM taxonomy; they get their own rule family only when a build
  task justifies it (no speculative directories — knowledge-architecture).
- **OSI-only (ADR-0002)** extends to connectors and dashboard tooling.

## 6. Open owner decisions (gate the build)

- **A1** — Global Context scope: SCM-specific (default) vs domain-agnostic engine.
- **A2** — Project relationship: reference + overlay (default) vs read-only-only vs
  versioned snapshot/fork.
- **A3** — Monitoring source: both external + internal unified (default, internal-first) vs
  one only.

Ratifying ADR-0030/0031 resolves these; the Stage-B/C build stays gated until then.

## 7. Still missing (owner input)

- `context-map.md` — the concept relationship map (Global Context ↔ Workspace ↔ Project ↔
  Monitoring, plus the SCOR-DS ↔ department map currently in `README.md`). Promote here when
  it needs to grow.

- **Governing refs:** `CLAUDE.md` · [ADR-0030](../10-decisions/README.md) ·
  [ADR-0031](../10-decisions/README.md) · ADR-0017/0021/0024/0026.
