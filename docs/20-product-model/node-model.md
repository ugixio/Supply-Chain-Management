---
id: node-model
title: "Node Model — the workspace as a typed graph"
type: product-model
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-29
relations:
  - { type: part-of, target: index-product-model }
  - { type: governed-by, target: index-adr }
  - { type: refines, target: product-statement }
---
# Node Model — the workspace as a typed graph

> How the enterprise workspace is organized so a developer can interpret every part of it
> (ADR-0030 direction). The organizing principle is a **typed node + typed edge graph**: the
> same shape already validated by the doc gates (G5 no-orphans, G6 authority-acyclicity) and
> rendered by the octagon front end (ADR-0026), now stated as the product's structure — for
> the current SCM project **and every future project**. Grounded in the industry-standard
> **C4 model** (abstraction-first: system → container → component → code) and **arc42**
> docs-as-code practice, so the workspace reads like a navigable architecture, not a folder
> dump.

## 1. Everything is a node; every link is a typed edge

- A **Node** is any addressable unit of the workspace with a stable `id` and a declared
  **type** (`type` ∈ the knowledge-architecture §8 vocabulary: `governance | adr |
  product-model | concept | rule | context-spec | skill | engineering | operations |
  program`). Concept nodes carry `CPT-*`; rules carry stable IDs (`SCM-R*`, `ENG-R*`, dept
  families, `PLT-*`).
- An **Edge** is a typed relation between nodes, from the controlled set (§8):
  `part-of · governed-by · implements · refines · depends-on · traces-to ·
  supersedes/superseded-by`. Authority edges (`governed-by`) always point **up** the tier
  ladder (G6); structural edges (`part-of`) reach the parent index (G5).
- **No node is an island, no edge dangles:** every node is reachable and every edge resolves
  to a real node — enforced as **PLT-R3** and already checked by G4/G5/G6. This is the
  guarantee that everything is connected.

## 2. Regions — the current project and the next ones

The workspace graph is partitioned into **Regions**, each a connected subgraph:

- The **Global Context region** — the SCM operating discipline (14 departments, `CPT-*`,
  `SCM-R*`) + engineering & professional practice (`ENG-R*`, `.claude/skills`) + product
  model + decisions. Read-only, versioned, the shared substrate (ADR-0030). Today this is the
  *only* fully-materialized region.
- A **Project region** (future) — one connected subgraph per project (ADR-0030 Workspace/
  Projects). A project region attaches to the Global Context by **reference edges**
  (`depends-on`/`traces-to`) to global node IDs — read-only (PLT-R2) — plus a local
  **overlay** of project-scoped nodes and parameter overrides. Reads resolve *global node,
  then project override*.

A future project therefore does not copy the context; it **connects to it**. The node model
is the contract that lets project N+1 slot into the same graph the developer already knows.

## 3. C4 abstraction levels ↔ this workspace (so a developer can navigate)

| C4 level | In this workspace | Rendered as (ADR-0026) |
|---|---|---|
| System landscape | the **Workspace** (all regions) | the whole node-graph |
| System / container | a **Region** — Global Context or a Project | a cluster of nodes |
| Component | a **department** / a platform bounded context (`workspace`, `projects`) | department node, expands |
| Code | a **`CPT-*` concept** / a rule / a source symbol | leaf node → right sidebar |

The octagon front end (ADR-0026) is the **context/container view** of this same graph; the
sidebar drills to the **code level** (formula, worked example, source links). arc42's 12
sections map onto existing tiers (context→`20-product-model`, building blocks→`40-contexts`,
crosscutting→`30-foundation`, decisions→`10-decisions`), so no parallel documentation is
introduced — the workspace *is* the architecture doc.

## 4. Why this shape (design rationale)

- **One mental model reused everywhere** — a developer learns "typed nodes + typed edges +
  regions" once and reads any project the same way (comprehension is the goal, ADR-0030).
- **Connectivity is mechanically guaranteed** — the gates that already keep the SCM docs
  honest (G4/G5/G6) extend to every region; nothing can be added off-graph (PLT-R3/R4).
- **SSOT preserved** — projects reference, never mutate (PLT-R2, ADR-0024 one-way projection).
- **Open-source, portable** — the graph lives in front-matter + relations (plain Markdown),
  projected one-way to Postgres (ADR-0024) and served via GraphQL (ADR-0025); no proprietary
  graph engine (Neo4j is prohibited, ADR-0002/out-of-scope), keeping it commercial-safe and
  modifiable.

## 5. Law and references

- **Invariants:** [30-foundation/platform/rule.md](../30-foundation/platform/rule.md) —
  **PLT-R1..R5** (prompt-refinement gate, read-only reference, everything-connected, node/edge
  typing, one-branch-per-project). Concept semantics stay in `25-concepts`; this node defines
  *structure*, `rule.md` states *law* (knowledge-architecture SSOT).
- **Governing refs:** `CLAUDE.md` · [ADR-0030](../10-decisions/README.md) ·
  [ADR-0026](../10-decisions/README.md) (octagon view) · [ADR-0024](../10-decisions/README.md)
  (one-way read model) · knowledge-architecture §8 (node/edge vocabulary).
- **External grounding:** the C4 model (Brown) — abstraction-first architecture diagrams;
  arc42 (Starke & Hruschka) — docs-as-code architecture template. Both OSI-friendly, free,
  and node/relationship-oriented.
