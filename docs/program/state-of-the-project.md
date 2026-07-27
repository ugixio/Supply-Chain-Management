---
id: program-state-of-project
title: "State of the Project — snapshot & improvement map"
type: program
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-27
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
  IDs, ten gates in CI, the node model. Still the estate's best asset, and the reason the reframe
  could be made surgically instead of by restart.
- **Standards fidelity** — *improving, was a real weakness*. The unit codes were wrong (`KG` for
  `KGM`) and the z-score was approximated by a hand-typed table. Both are fixed. The remaining
  exposure is that no gate can tell a standard from a plausible-looking invention — G10 checks that
  a source is *cited*, not that the content matches it.
- **Policy separation (the new central discipline)** — *decided, not yet swept*. `CLAUDE.md`,
  `SCM-R*` and the department index headers now carry the inclusion test; the 154 concept nodes and
  the 14 department rule files do not yet (Phase C1/C2).
- **Money precision (no float)** — *resolved*. One implementation, `crates/scm-money`: exact
  decimal, `roundTiesToEven`, sum-preserving apportionment, overflow reported rather than wrapped,
  no `unsafe`. The TypeScript and Python mirrors that used to disagree are gone.
- **Security (runtime)** — *not applicable yet*. There is no running system to secure. It becomes
  live with Phase M (authN/authZ, secrets, tenancy, ClickHouse split-privilege users).
- **CI/CD** — *partial*. GitHub Actions runs exactly `make verify-full`; no deploy pipeline,
  containerization or observability (Phase M5).
- **UI design tokens** — *specified only* (ADR-0026: octagon node-graph, LED-cyan `#22d3ee`); no
  UI exists.

## 4. Where improvement signals come from

- `make verify` — the ten doc gates; G10 now checks standards provenance.
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

**Next, in order:** **Phase C** — sweep the catalogue and the department rules for policy that the
inclusion test forbids (C1/C2 are judgement work no gate can do), then the citation and prose
cleanup (C3/C4). **Then Phase M** — define the delivery metrics as concept nodes, build the
ClickHouse telemetry tier per ADR-0036, the Rust ingester, the GraphQL gateway and the dashboards.

**Known inconsistency, stated plainly:** until C1/C2 land, the catalogue still contains
thresholds, targets and weightings that ADR-0037 forbids. The decision is recorded and the sweep
is scheduled; the content has not caught up yet.

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
