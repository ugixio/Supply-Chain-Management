---
id: program-state-of-project
title: "State of the Project — snapshot & improvement map"
type: program
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-29
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
> Artifact (see §6). **Snapshot: 2026-07-27.**

## 1. What the project is (one paragraph)

A project/workspace modeled as a **technology company** where **SCM is the operating
discipline** — the Global Context that governs a portfolio of Projects across all tech
branches, organized as a typed node+edge graph of Regions (ADR-0030; `20-product-model/
node-model.md`). Not a commercial product.

## 2. Completion by layer (estimate, for steering)

> **Reset by ADR-0037.** The previous estimate counted an invented supply-chain application as
> ~60% of a product. That application was deleted: it was not progress toward this repository's
> purpose, so the percentages below measure something different from the ones before it.

| Layer | State | Est. |
|---|---|---|
| The context — standards, 154 concept nodes, rules, ADRs, node model, gates | substantial and gate-enforced, **but carries policy the inclusion test forbids** (Phase C1/C2) | ~70% |
| Standards reference data (`packages/shared`) | ISO 8601/4217/3166, UN/ECE Rec 20 units, GS1 keys + check digit, Incoterms 2020, SCOR — purged of policy | ~40% |
| Exact money arithmetic (`crates/scm-money`) | complete and tested; no policy | ~95% |
| Monitoring application (Phase M) | designed (ADR-0031/0034/0036), **no code** | ~2% |
| Workspace / projects layer | modelled, not built | ~5% |
| **Overall** | | **~20%** |

## 3. Best-practices scorecard (verdict · evidence)

> Most rows of the previous scorecard graded an application that ADR-0037 deleted (clean
> architecture rings, DDD aggregates, event sourcing, DB schema, TS/PY test parity). Those rows are
> gone rather than restated: grading absent code would be theatre. What is left is what the
> repository actually is.

- **Knowledge governance** — *built, strong*. Tiered docs, one-way SSOT, append-only ADRs, stable
  IDs, thirteen gates in CI, the node model. Still the estate's best asset, and the reason the reframe
  could be made surgically instead of by restart.
- **Standards fidelity** — *improving, was a real weakness*. The unit codes were wrong (`KG` for
  `KGM`) and the z-score was approximated by a hand-typed table. Both are fixed. The remaining
  exposure is that no gate can tell a standard from a plausible-looking invention — G10 checks that
  a source is *cited*, not that the content matches it.
- **Policy separation (the new central discipline)** — *swept, and the sweep is the discipline*.
  `CLAUDE.md`, `SCM-R*` and the department index headers carry the inclusion test; Phase C1 swept
  the 160 concept nodes and C2 rewrote all fourteen department rule families. The residue the
  2026-07-29 file-by-file review found was not in `docs/40-contexts` — it was in the glossary, in
  benchmark *parameters* left inside dept-06 node output descriptions, and above all in
  `.claude/skills/**`, which no gate reads and which instructs the next session's work.
- **Money precision (no float)** — *resolved*. One implementation, `crates/scm-money`: exact
  decimal, `roundTiesToEven`, sum-preserving apportionment, overflow reported rather than wrapped,
  no `unsafe`. The TypeScript and Python mirrors that used to disagree are gone.
- **Security (runtime)** — *beginning*. There is still no running system, but the first real
  boundary exists: migration 0005 creates a split-privilege ClickHouse pair (insert-only writer,
  SELECT-only reader) with quotas. AuthN/authZ, secrets and tenancy arrive with M4.
- **CI/CD** — *partial*. GitHub Actions runs `make verify-full` and `make verify-schema` (the
  latter against a real ClickHouse service container); no deploy pipeline, containerization or
  observability (Phase M5).
- **UI design tokens** — *specified only* (ADR-0026: octagon node-graph, LED-cyan `#22d3ee`); no
  UI exists.

## 4. Where improvement signals come from

- `make verify` — the thirteen doc gates; G10 checks standards provenance, G12 catches
  family-wildcard rule citations, G13 catches a stale `updated:` stamp.
- `docs/program/WORKFLOW.md` — the ordered backlog (Phase C cleanup, Phase M monitoring).
- `docs/00-governance/risk-register.md` · `docs/program/improvement-register.md`.
- **The gap no tool reports:** whether a node's content is genuinely externally fixed. The
  anti-states in `docs/30-foundation/scm-core/rule.md` are the checklist a reviewer applies by
  hand.

## 5. Route (chosen path)

**Reframed by the owner on 2026-07-27 (ADR-0037).** The repository is the context a project
consults to learn which supply-chain departments it needs and how to implement them — nothing
more — and the only application it builds is monitoring.

**Done in that direction:** ADR-0037 recorded · `SCM-R*` reclassified (7 of 13 retired as policy
or engineering convention; SCM-R14 added for the money identity) · ~25,700 lines of invented
application deleted (`packages/domain`, `services/calc`, `crates/scm-core`, `proto/`) ·
`packages/shared` purged to standards, with the wrong UOM codes corrected to UN/ECE Rec 20 ·
G10 rewritten from *code coverage* to *standards provenance* · `## Implementations` removed from
152 nodes · `CLAUDE.md` rewritten around the inclusion test.

**Since then:** Phase C ran — C1 swept the catalogue, C2 rewrote all fourteen department rule
families, C3 mechanized stale citations as G3/G12, C4/C4b corrected prose that described deleted
code, C5 rewrote the standards framework with per-entry verification dates. Phase M is under way:
**M1** the six platform concept nodes (CPT-0155..0160), **M2** the ClickHouse telemetry tier with
its own gate, **M3a** the Rust ingestion core.

**Next, in order:** **M3b** the transport adapter and ClickHouse client (retry, dead-letter),
**M4** NestJS + GraphQL and the Next.js dashboards, **M5** Docker then Kubernetes.

**Known inconsistency, stated plainly.** The catalogue and the department rules are swept; the
**agent and skill layer is not**. `.claude/skills/**` still publishes KPI *target* tables — `OTD
≥ 95%`, `Fill Rate ≥ 98%`, `CoPQ < 2% of revenue` — which are precisely what ADR-0037 forbids, and
`.claude/commands/**` still addresses application code that no longer exists. That layer sits
outside every gate but inside every session's working set, which makes it the worst remaining
place for the defect, not the least important. Found by the 2026-07-29 file-by-file review;
scoped, not yet swept.

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
