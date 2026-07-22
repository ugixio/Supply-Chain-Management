---
id: product-statement
title: "Product Statement — what the project is"
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

> The authoritative WHAT, materialized from the owner's direction (2026-07-22) and recorded
> per the plan⇄context rule (ADR-0010). Concepts are **defined here** and referenced by
> stable name everywhere else. Note on the word "product": the `20-product-model` tier names
> *what we are building*; **this is not a commercial product — it is a project / workspace**
> (see §1). Decisions live in ADR-0030/0031/0032 (Accepted, owner-directed).

## 1. What it is

A **project / workspace modeled as a technology company**, where **supply-chain management is
the operating discipline of the company itself**. The SCM flow — plan → source → make →
deliver → return → enable, with its KPIs, quality control, risk, procurement and S&OP logic —
is applied not to physical goods but to **the flow of technical work**. That discipline is the
**Global Context** that plans, governs, produces, delivers and monitors a **portfolio of
Projects**, each a deliverable in some **branch of technology**.

Three layers:

1. **Global Context** — the company's operating context, read-only and versioned, with a wiki
   front end (octagon node-graph, ADR-0026):
   - the **SCM operating discipline** (14 SCOR-DS departments, `CPT-*` concept catalogue,
     `SCM-R*`/department rules) reused as the operating system for running work;
   - the **engineering & professional-practice knowledge** (the `50-engineering` `ENG-R*`
     rules + the `.claude/skills` practice layer);
   - the standards the company applies to every project: **best practices, technical
     concepts, applied professionalism, design, processes, organization, structure** — and
     more as they are justified.
   `docs/` stays the single source of truth; the served graph is a one-way projection
   (ADR-0024).
2. **Workspace** — the company space that holds **Projects**. A project **consumes** the
   Global Context (references concepts/rules by stable ID, plus a local **overlay** of its own
   concepts and parameter overrides) and owns its transactional data. Projects never mutate
   the Global Context.
3. **Monitoring** (future, complementary — ADR-0031) — real-time dashboards + delivery metrics
   over a project's development/progress.

## 2. Who / what it serves

The company's own delivery of technical work across **every branch of technology**. A Project
lives in a branch — **non-exhaustive**: AI · Machine Learning · Data Science · Data Analysis ·
Data Engineering · software development · Backend · Frontend / web · UI/UX · Databases ·
DevOps · MLOps · Cloud & Infrastructure / SRE · Security · QA & testing · Mobile · Systems /
embedded · Product & Project management · Technical writing. The list is open; new branches
are onboarded as real projects need them (not pre-built — §5).

Across every branch, the Global Context supplies the same governing dimensions —
**non-exhaustive**: engineering best practices · architecture & design · coding standards &
code quality · testing & QA discipline · security-by-default · data governance · CI/CD &
DevOps practice · documentation & knowledge management · project/process organization &
structure · professionalism & ways of working · KPIs & delivery metrics · risk & compliance.

## 3. Delivery form

Full-stack web application on the recorded stack (Next.js · NestJS code-first GraphQL ·
PostgreSQL · Python calc core over gRPC — ADR-0017/0020/0022/0025). Staged:

- **Stage A (exists / in build):** the Global Context wiki — octagon node-graph from the
  one-way Postgres read model of `docs/`.
- **Stage B (this direction — ADR-0030):** the Workspace + Projects layer — new bounded
  contexts (`workspace`/`projects`) with their own persistence, tenancy and lifecycle,
  reading the knowledge read model and referencing global nodes by ID + overlay. Includes the
  **prompt-refinement gate** (ADR-0032).
- **Stage C (future, complementary — ADR-0031):** the Monitoring connector — dashboards +
  metrics over project development; metrics defined as `CPT-*` nodes.

## 4. Core concepts (defined here; referenced elsewhere)

| Concept | Definition | Authority |
|---|---|---|
| **Global Context** | The read-only, versioned operating context: SCM discipline + engineering/professional practice + standards, surfaced as a wiki. | ADR-0030 |
| **Workspace** | The company space that contains Projects. | ADR-0030 |
| **Project** | A unit of technical work in a tech branch; references the Global Context by stable ID and owns its transactional data; never mutates the context. | ADR-0030 |
| **Project Overlay** | A project's local layer of project-scoped concepts + parameter/threshold overrides referencing (never rewriting) global nodes; reads resolve global-then-override. | ADR-0030 |
| **Tech Branch** | The technical discipline a project belongs to (AI, ML, DevOps, frontend, …); an open, incrementally-materialized set. | ADR-0030 |
| **Prompt-Refinement Gate** | A user prompt is first improved, then the improved prompt is executed; original + improved retained. The company's incoming-quality control on instructions. | ADR-0032 |
| **Connector** | Ingests a project's development/progress signals (external dev tools and/or internal project data). | ADR-0031 |
| **Delivery Metric** | A progress/velocity calculation over project signals, defined as a `CPT-*` concept node. | ADR-0031 |

## 5. Invariants this statement commits to

- **Knowledge SSOT is one-way (ADR-0024):** projects read the Global Context; never write it.
  Global corrections propagate; project tuning lives only in the overlay.
- **One calculation catalogue (ADR-0015):** delivery/monitoring metrics and any refinement
  metric are `CPT-*` nodes — no parallel registry.
- **Platform ≠ department:** workspace/projects/monitoring and per-branch practice are platform
  concerns (reserved family `PLT`, id-registry §2), **materialized only per justified build
  task** — no speculative directories/skills for every branch or concept up front.
- **Prompt-refinement gate (ADR-0032):** applies across all projects and branches; enforced at
  the platform runtime (A4 — owner-confirmable).
- **OSI-only (ADR-0002)** extends to connectors and dashboard tooling.

## 6. Owner decisions — resolved 2026-07-22

- **A1 — context scope:** RESOLVED — **SCM-specific as the operating discipline**; the governed
  portfolio spans all tech branches (breadth in data + per-branch practice, not a generalized
  engine). Domain-agnostic engine reserved for a future ADR.
- **A2 — project relationship:** RESOLVED — **reference + overlay**.
- **A3 — monitoring source:** RESOLVED — **both (external + internal), internal-first**.
- **A4 — prompt-gate enforcement surface:** working default **platform runtime feature**;
  owner may narrow (ADR-0032).

## 7. Still missing (owner input / future)

- `context-map.md` — the concept relationship map (Global Context ↔ Workspace ↔ Project ↔
  Monitoring; SCM-discipline ↔ tech-branch governance; SCOR-DS ↔ department map now in
  `README.md`). Promote here when it needs to grow.

- **Governing refs:** `CLAUDE.md` · [ADR-0030](../10-decisions/README.md) ·
  [ADR-0031](../10-decisions/README.md) · [ADR-0032](../10-decisions/README.md) ·
  ADR-0017/0021/0024/0026/0008.
