# Supply Chain Management — Development Contract

## What this repository is

A **Global Context**: the source a project consults to learn **which supply-chain departments it
needs and how to implement them**. It is not a supply-chain product and holds no company's data
(ADR-0037).

The one application built here is **monitoring** — real-time dashboards and delivery metrics over
a project's development progress (ADR-0031/0034/0036). Everything else in this repository is
knowledge: standards, department definitions, concepts, and the rules that keep all of it honest.

## The inclusion test — apply it to every change

> A statement belongs here only if something **outside** this repository fixes it: a standards
> body (GS1, ISO, ICC, UN/CEFACT, ASCM), a regulator (CSDDD, UFLPA, REACH, UCC), or an arithmetic
> identity. **If an organization can reasonably choose it, it is project policy and does not
> belong here.**

Policy has a recognizable shape: a threshold, a target, a tolerance, a weighting, a rating band, a
service level, or a mandate to use one legitimate method over another. The context names the
decision and the standard that constrains it, then **stops** — see
`docs/30-foundation/scm-core/rule.md` §Project decisions.

This test is why ~25,700 lines of invented application code were deleted, and it is the first
thing to check when adding anything.

## Anti-patterns (all of these happened here)

- **Policy dressed as law.** A USD 5,000 approval threshold, a 5% receipt tolerance and a
  40/30/20/10 scorecard weighting were once stated as binding rules. Every future project would
  have inherited one company's habits as though they were standards.
- **Invented data wearing a standard's name.** The unit list read `KG`, `L`, `M`. The real UN/ECE
  Rec 20 codes are `KGM`, `LTR`, `MTR` — the invented shorthand was silently non-conformant.
- **A default hidden in a signature.** `over_tolerance_pct: float = 5.0` is worse than a named
  constant: it gets inherited without anyone deciding.
- **A textbook example read as a specification.** "World-class OTD ≥ 95%" is an illustration, not
  a requirement. Numbers from a reference get quoted as targets unless the node says otherwise.

## Layout

```
docs/              The context itself — tiered knowledge; map: docs/_index.md
  00-governance/     Knowledge architecture, ID registry, risk register
  10-decisions/      ADRs (append-only; the index is the entry point)
  20-product-model/  What this project is; the node model; glossary
  25-concepts/       CPT-NNNN concept nodes, per department
  30-foundation/     Cross-cutting rules (SCM-R*, PLT-*, MSR-*)
  40-contexts/       Per-department rules (PRC-*, DMD-*, INV-* …)
  50-engineering/    ENG-R* build-time rules
  program/           Backlog, operating model, evaluation protocol, templates
apps/              web · api — the monitoring application (not yet built)
packages/shared/   @scm/shared — standards reference data only
crates/scm-money   Exact money arithmetic; no policy
crates/scm-ingest  Telemetry ingestion core: normalize · validate · dedup · batch; no transport
crates/scm-ingest-clickhouse  The transport half: RowBinary insert, retry, dead-letter
db/clickhouse      The telemetry schema (ADR-0036): migrations, apply.py, the schema gate
tools/verify.py    The doc gates
```

## Standards this context carries

| Standard / law | Scope |
|---|---|
| ISO 8601-1:2019 | Dates and instants (SCM-R9) |
| ISO 4217 | Currency codes and minor units |
| ISO 3166-1 | Country codes |
| UN/ECE Rec 20 · GS1 Gen. Specs. v23 | Units of measure; GTIN, GLN, SSCC, GSIN and their check digit (SCM-R10) |
| Incoterms® 2020 (ICC) | The eleven trade rules; DPU replaced DAT; four are sea-only |
| SCOR Digital Standard (ASCM) | Plan · Source · Make · Deliver · Return · Enable |
| UN/EDIFACT | ORDERS, DESADV, INVOIC, RECADV message semantics |
| ISO 2859-1 | AQL sampling plans — the *plan* is fixed, the AQL level is a project's choice |
| ISO 9001:2015 · ISO 28000:2022 | Quality and supply-chain security management |
| EU CSDDD 2024/1760 (amended by 2026/470) | Due diligence; ≥ 5-year retention (SCM-R7) |
| US UFLPA (Pub. L. 117-78) | Xinjiang forced-labour presumption (SCM-R6) |
| EU REACH 1907/2006 | Substance obligations |
| US UCC Article 2 | Sale of goods; a quantity must be stated |
| IEEE 754-2019 §4.3.3 | `roundTiesToEven` — the money rounding rule (SCM-R14) |

Full reference: `docs/standards/REGULATORY_FRAMEWORK.md`.

## Rules (cited by ID, never restated)

- **`SCM-R*`** — `docs/30-foundation/scm-core/rule.md`. Externally-fixed statements only. Retired
  IDs stay listed as retired so old citations still resolve.
- **`ENG-R*`** — `docs/50-engineering/rule.md`. Build-time law: dependency direction, exact money
  (ENG-R4/R5), generated artefacts, exclusive technology lanes (ENG-R8), the six-check
  best-option gate (ENG-R9), the Rust core boundary (ENG-R10).
- **`PLT-*`** — `docs/30-foundation/platform/rule.md`. Prompt-refinement gate, read-only project
  reference, everything-connected, node/edge typing.
- **`MSR-*`** — `docs/30-foundation/measurement/rule.md`. Measurement identities: a ratio aggregates
  from its components (MSR-R1), a level is never summed (MSR-R2). Cited, never restated.
- Per-department families live in `docs/40-contexts/<NN-dept>/rule.md`.

## Concept nodes

One node per concept (`CPT-NNNN`, `docs/25-concepts/`). A node states meaning, the canonical
formula where one exists, symbols and units, assumptions and non-applicability, **project-chosen
inputs**, and the source that fixes it. It holds **no** parameter value and links to **no**
implementation. Gate **G10** enforces: unique CPT number, a cited source, no `## Implementations`.

## Technology lanes (ADR-0033/0035; ENG-R8/R10)

Each technology owns one responsibility and no other may perform it:

| Lane | Owner |
|---|---|
| Presentation | **Next.js** (talks only to NestJS) |
| The only counterpart the frontend has | **NestJS + GraphQL** |
| Core: rules, invariants, exact arithmetic, hot path, ingestion | **Rust** |
| Models, statistics, optimization, ML | **Python** |
| Transactional truth | **PostgreSQL** |
| Project telemetry at scale (never truth) | **ClickHouse** |
| Images · orchestration | **Docker** · **Kubernetes** |

TypeScript is not a lane owner: it lives inside NestJS and Next.js, plus the standards module.
Dependencies stay OSI-licensed, commercially usable and modifiable (ADR-0002).

## Working agreements

- **Improve the prompt first.** A request is refined before it is executed; the original and the
  improved form are both retained (PLT-R1, ADR-0032).
- **Then close what it left open — by choice, not by guess (PLT-R6, ADR-0038).** The search for a
  better implementation is standing: algorithmic cost, compute, structure, clean code, security,
  **inside the adopted lanes only** — a recommendation never introduces a new technology. When a
  missing detail would change what gets built, it is offered as a **selectable list** of recommended
  options with their trade-offs, never guessed and never buried in prose. Selected options are built
  the same turn; declined ones are recorded so they are not re-proposed. Question craft:
  `docs/program/evaluation.md` §6.
- **Review by enumeration, never by impression.** Asked to review documents — any set, any type —
  run `docs/program/review-protocol.md`: enumerate the estate mechanically and state its count,
  name the finding classes before looking, mark every item as reached, then fix what needs no
  decision, mechanize what a gate could catch, and raise the rest as a selectable list. The
  marking checklist is transient and is deleted at the close; the findings land in the registers.
  Report the denominator, not only the findings.
- **Ask before adopting a new language or framework**, with its speed and security trade-offs.
  A library inside an existing lane does not need a decision.
- **Plan⇄context first (ADR-0010).** A change that introduces or renames a concept lands in the
  model, the ADR and the rules **before** it lands in code.
- **Run the ENG-R9 six checks before writing code** — lane, best practice, security, speed,
  scalability, licence — and state the result at handoff.
- **English only** in code, comments, documentation, configuration and commit messages.
- **Before acting**, read `docs/program/evaluation.md` (reasoning protocol, decision ladder,
  self-review). Corrections land as known-pitfalls entries; risks in
  `docs/00-governance/risk-register.md`; structural lessons in
  `docs/program/improvement-register.md`.

## Gates

`make verify` — doc gates G1–G13, typecheck, Rust tests. Run after **every** layer.
`make verify-full` — the merge gate: adds `cargo fmt --check` and `clippy -D warnings`.
`make verify-schema` — the telemetry schema against a real ClickHouse. CI runs both gates.

G1 no stray docs · G2 front-matter · G3 unique IDs · G4 link integrity · G5 no orphans ·
G6 authority acyclicity · G7 status and supersession · G8 English-only (screened) ·
G9 context budget · G10 standards provenance · G11 retired rules stay retired ·
G12 a rule citation names an ID (never a family wildcard) · G13 `updated:` is true.

**Definition of Done:** `make verify-full` green · touched rules keep their tests · spec and model
updated first if a concept changed · knowledge placed per
`docs/00-governance/knowledge-architecture.md` (no stray `.md`) · self-review run · commit message
proposed (Conventional Commits, ADR-0011).

## References

Cited for **definitions**, never for target values:

- APICS Dictionary 16th Ed. (ASCM, 2024) — terminology.
- SCOR Digital Standard (ASCM, 2019) — process taxonomy.
- ICC Incoterms® 2020 (ICC, 2019); GS1 General Specifications v23.
- Chopra & Meindl, *Supply Chain Management* 6th Ed.; Christopher, *Logistics and Supply Chain
  Management* 6th Ed.
