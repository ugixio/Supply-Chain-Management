---
id: index-engineering
title: "Engineering — build-time architecture rules"
type: engineering
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-20
relations:
  - { type: part-of, target: index-docs }
  - { type: governed-by, target: index-adr }
---
# Engineering — build-time architecture rules

- **Belongs here:** the rules that govern **how the code is built and layered** — the
  Clean-Architecture dependency direction (ADR-0018), the monorepo structure (ADR-0023),
  the module boundaries and the toolchain contract. Materialized now that the app surface
  is real (the reserved `50-engineering` slot, knowledge-architecture §1).
- **Authority:** these are Tier 6 (build-time know-how). They constrain *code structure*,
  not *business meaning*: a domain invariant in a `40-contexts/*/rule.md` (Tier 4) outranks
  a layering rule here. Engineering rules are `governed-by` the ADRs that set them.
- **Distinct from:** `docs/25-concepts` (what a calculation means) and `rule.md` (business
  law). This tier answers "where may this import point" and "which package owns this".

## Contents

- [rule.md](rule.md) — the `ENG-*` engineering rule family (dependency direction, module
  boundaries, money/precision at the code boundary, toolchain).

## To be materialized as the build lands

- `50-engineering/frontend/` — component and design-token rules once `apps/web` exists
  (the octagon node-graph UX ADR is the seed).
- `60-operations/` — CI/CD, deployment and runbooks (still reserved; materialize when they
  exist).

- **Governing refs:** `CLAUDE.md` · [ADR-0018](../10-decisions/README.md) (Clean Arch) ·
  [ADR-0022/0023](../10-decisions/README.md) (toolchain & structure).
