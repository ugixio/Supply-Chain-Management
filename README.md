# Supply Chain Management — Global Context

**A source of knowledge, not a supply-chain product.** A project consults this repository to
learn **which supply-chain departments it needs and how to implement them**. It holds no
company's data and no company's policy (ADR-0037).

The one application built here is **monitoring** — real-time dashboards and delivery metrics over
a project's development progress (ADR-0031/0034/0036).

## The inclusion test

> A statement belongs here only if something **outside** this repository fixes it: a standards
> body (GS1, ISO, ICC, UN/CEFACT, ASCM), a regulator (CSDDD, UFLPA, REACH, UCC), or an arithmetic
> identity. **If an organization can reasonably choose it, it is project policy and does not
> belong here.**

Thresholds, targets, tolerances, weightings, rating bands and service levels all have that shape.
The context names the decision and the standard that constrains it, then stops. This test is why
~25,700 lines of invented application code were deleted, and it is the first thing to check
before adding anything. Details in [CLAUDE.md](CLAUDE.md).

## Layout

```
docs/              The context itself — tiered knowledge; start at docs/_index.md
  00-governance/     Knowledge architecture, ID registry, risk register
  10-decisions/      ADRs (append-only; the index is the entry point)
  20-product-model/  What this project is; the node model; glossary
  25-concepts/       CPT-NNNN concept nodes, per department
  30-foundation/     Cross-cutting rules (SCM-R*, PLT-*)
  40-contexts/       Per-department rules (PRC-*, DMD-*, INV-* …)
  50-engineering/    ENG-R* build-time rules
  program/           Backlog, operating model, evaluation protocol, templates
apps/              web · api — the monitoring application (not yet built)
packages/shared/   @scm/shared — standards reference data only
crates/scm-money/  Exact money arithmetic; no policy
crates/scm-ingest/ Telemetry ingestion core: normalize · validate · dedup · batch; no transport
crates/scm-ingest-clickhouse/  The transport half: RowBinary insert, retry, dead-letter
db/clickhouse/     The telemetry schema (ADR-0036): migrations + the schema gate
tools/verify.py    The doc gates
```

## The 14 departments

A department **is** its concept nodes, its rules and its practice skill — there is no department
code tree here. A project implements what it needs, in its own repository.

| # | Department | SCOR |
|---|---|---|
| 01 | Procurement & strategic sourcing | Source |
| 02 | Supplier management & evaluation | Enable |
| 03 | Demand planning & forecasting | Plan |
| 04 | Supply planning (MRP/MPS) | Plan · Make |
| 05 | Inventory management | Return |
| 06 | Warehouse management (WMS) | Enable |
| 07 | Logistics & transportation (TMS) | Deliver |
| 08 | Quality management (ISO 9001) | Enable |
| 09 | Regulatory compliance | Enable |
| 10 | Supply-chain risk management | Enable |
| 11 | Supply-chain finance & controlling | Enable |
| 12 | S&OP / integrated business planning | Plan |
| 13 | Order management (order-to-cash) | Deliver |
| 14 | Supplier development & ESG | Source |

Concepts: [docs/25-concepts](docs/25-concepts/_index.md) ·
rules: [docs/40-contexts](docs/40-contexts/_index.md).

**No KPI targets are published here.** OTIF, OTD, perfect-order rate, MAPE, PPM and the rest are
defined as concepts — what they mean, how they are computed, what they assume — and the level
that counts as good is the project's decision. A "world-class" figure quoted from a textbook is
an illustration, not a requirement.

## Standards and law carried

ISO 8601-1:2019 · ISO 4217 · ISO 3166-1 · UN/ECE Rec 20 · GS1 General Specifications v23 ·
Incoterms® 2020 (ICC) · SCOR Digital Standard (ASCM) · UN/EDIFACT · ISO 2859-1 ·
ISO 9001:2015 · ISO 28000:2022 · EU CSDDD 2024/1760 (amended by 2026/470) · US UFLPA ·
EU REACH 1907/2006 · EU CBAM · EU Deforestation Regulation 2023/1115 · EU CSRD · US UCC
Article 2 · IEEE 754-2019 §4.3.3.

Full reference: [docs/standards/REGULATORY_FRAMEWORK.md](docs/standards/REGULATORY_FRAMEWORK.md).

## Working on this repository

```bash
make verify        # doc gates G1-G13 + typecheck + Rust tests — run after every layer
make verify-full   # the merge gate: adds the lockfile check, cargo fmt and clippy
make verify-schema # the telemetry schema — needs a reachable ClickHouse; never skips
```

CI runs `make verify-full` **and** `make verify-schema`. The split is deliberate:
`verify-full` is portable and runs anywhere, `verify-schema` needs a server. The Makefile
header states why. Read [CLAUDE.md](CLAUDE.md) first, then
[docs/program/evaluation.md](docs/program/evaluation.md).

## References

Cited for **definitions**, never for target values: APICS Dictionary 16th Ed. (ASCM, 2024) ·
SCOR Digital Standard (ASCM, 2019) · ICC Incoterms® 2020 · GS1 General Specifications v23 ·
Chopra & Meindl, *Supply Chain Management* 6th Ed. · Christopher, *Logistics and Supply Chain
Management* 6th Ed. · Orlicky, *Material Requirements Planning* 3rd Ed. · Silver, Pyke &
Peterson, *Inventory Management and Production Planning* · Kraljic (HBR, 1983) ·
Lee, Padmanabhan & Whang (MIT Sloan, 1997) · Hyndman & Koehler (IJF, 2006).

## License

MIT — see [LICENSE](LICENSE).
