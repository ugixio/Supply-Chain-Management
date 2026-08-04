---
id: engineering-practice-areas
title: "Engineering Practice Areas — the second knowledge axis, and what fixes each one"
type: engineering
owner: orchestrator
status: active
since: 2026-08-03
updated: 2026-08-04
relations:
  - { type: part-of, target: index-engineering }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: rule-engineering }
---
# Engineering practice areas — the second knowledge axis

> **What this is.** The Global Context carries two axes (ADR-0045): **how a company is run** — the
> fourteen supply-chain departments — and **how software is engineered**, which is this roster. Both
> exist for the projects that read the context, across every technology branch: AI, machine learning,
> data engineering, DevOps, databases, web.
>
> **What this is not.** It is **not** thirty-six sections of content. Nothing here is materialized
> yet, on purpose: W5 forbids speculative pre-build — a branch's knowledge is written **when a real
> project needs it**. What the roster fixes is the thing that cannot be improvised later: **which
> external authority anchors each area**, so the day someone writes it, they cannot invent it.

## Why the anchor column is the whole point

The supply-chain axis exists because standards bodies fix it — GS1, ISO, ICC, UN/CEFACT, ASCM. The
engineering axis has to meet the same bar (`CLAUDE.md` §The inclusion test) and it is **easier to get
wrong**, because software practice is full of respected advice that an organization can reasonably
decline. "Prefer composition over inheritance" is good counsel and it is not law.

So each area below names what would make a statement in it admissible. Three kinds of anchor appear,
and the difference decides what may be written:

| Anchor kind | What may be stated | Example |
|---|---|---|
| **Standard** — a standards body fixes it | The requirement itself, as law | ISO/IEC 25010 quality characteristics; SemVer's precedence rules |
| **Terminology** — a published work fixes the *vocabulary* | Definitions and taxonomy, with a vocabulary warning; **never a mandate to use the method** | GoF pattern names; DDD's bounded context; SRE's SLI/SLO |
| **Identity** — arithmetic or a proof fixes it | The identity, unconditionally | Complexity bounds; CAP; Little's Law (already CPT-0159) |

**A fourth kind does not exist here.** "Industry consensus", "widely accepted" and "best practice"
are not anchors. An area whose only support is consensus contributes **the decision a project must
make**, not an answer — exactly as the supply-chain nodes carry `Project-chosen inputs`.

## The roster

Order follows the owner's list. **Status is `—` for every row**: none is materialized, and a row
becomes work only when a project needs it (W5).

| # | Practice area | Anchor kind | What would fix it |
|---|---|---|---|
| 1 | Computer-science fundamentals | Identity | Computability and complexity results; IEEE 754 for floating point |
| 2 | Algorithms and data structures | Identity | Asymptotic bounds; proven optimality (e.g. comparison-sort lower bound) |
| 3 | Software-engineering principles | Terminology | ISO/IEC/IEEE 12207 (lifecycle processes), 24765 (vocabulary) |
| 4 | Clean code | Terminology | Martin, *Clean Code* — **the highest-risk row**: naming and structure advice is choosable, so only its vocabulary is admissible |
| 5 | Design patterns | Terminology | Gamma et al. (GoF); POSA. Pattern *names and intents*, never a mandate |
| 6 | Software architecture | Standard | ISO/IEC/IEEE 42010 — architecture description, viewpoints, stakeholders |
| 7 | Domain-Driven Design | Terminology | Evans; Vernon. Bounded context, aggregate, ubiquitous language |
| 8 | Distributed systems | Identity | CAP; FLP impossibility; Lamport on clocks and consensus |
| 9 | API design and service integration | Standard | OpenAPI; RFC 9110 (HTTP semantics); RFC 7807 (problem details); gRPC/protobuf specs |
| 10 | Databases and data modelling | Standard + Identity | ISO/IEC 9075 (SQL); normal forms and functional dependency as identities; ACID |
| 11 | Data engineering | Terminology | DAMA-DMBOK; W3C PROV-O for lineage |
| 12 | DevOps | Terminology + Identity | DORA delivery metrics (already CPT-0155..0167); Twelve-Factor as published methodology |
| 13 | Infrastructure as code | Terminology | Provider specifications; the idempotence property as an identity |
| 14 | Containers and orchestration | Standard | OCI image/runtime specs; Kubernetes API conventions |
| 15 | Cloud computing | Standard | NIST SP 800-145 (the cloud definition and service models) |
| 16 | Observability and SRE | Terminology | OpenTelemetry specification (**a real standard**); Google SRE for SLI/SLO/error-budget vocabulary — **levels are always the project's** |
| 17 | Application security / DevSecOps | Standard | OWASP ASVS; CWE; NIST SSDF (SP 800-218); CVSS scoring |
| 18 | Testing and QA | Standard + Terminology | ISO/IEC/IEEE 29119; ISTQB glossary; mutation-score as an identity over a suite |
| 19 | Source-code management and branching | Terminology | Git's own model; Conventional Commits; SemVer. **This repo's own choice is ENG-R11** |
| 20 | Performance engineering | Identity | Little's Law (CPT-0159); Amdahl's and Universal Scalability Law; queueing results |
| 21 | AI and machine learning | Standard + Identity | ISO/IEC 22989 (AI concepts and terminology); metric definitions as arithmetic |
| 22 | MLOps and LLMOps | Terminology | ISO/IEC 42001 (AI management systems — **certifiable**); NIST AI RMF functions |
| 23 | Product engineering | Terminology | ISO/IEC/IEEE 29148 (requirements engineering) |
| 24 | Technical documentation and communication | Standard | ISO/IEC/IEEE 26511/26514; Diátaxis for the form taxonomy (ADR-0044) |
| 25 | Technical leadership and architectural decisions | Terminology | ADR practice (Nygard, MADR) — **this repo's instance is ADR-0011** |
| 26 | Enterprise architecture | Terminology | TOGAF; ArchiMate (an Open Group standard) |
| 27 | Platform engineering | Terminology | CNCF platform definitions; Team Topologies vocabulary |
| 28 | Enterprise integration | Terminology | Hohpe & Woolf integration patterns; UN/EDIFACT already carried for the SCM axis |
| 29 | Cost management and FinOps | Terminology | FinOps Foundation framework — capabilities and domains, **not** cost targets |
| 30 | Technology governance and standards | Standard | ISO/IEC 38500 (IT governance); ISO/IEC 42001 for the AI slice |
| 31 | Design for scalability | Identity | Universal Scalability Law; Amdahl; queueing theory |
| 32 | Design for resilience | Terminology + Identity | Availability arithmetic (series/parallel); OpenTelemetry for the signals; chaos-engineering vocabulary |
| 33 | Design for high availability | Identity | Nines arithmetic and its budget consequences; redundancy formulas |
| 34 | Design for maintainability and evolution | Standard | ISO/IEC 25010 maintainability characteristics; coupling and cohesion measures |
| 35 | Technology strategy and roadmaps | **None found** | See below — this row is deliberately unanchored |
| 36 | Context engineering and agentic systems | Standard + Terminology | ISO/IEC 42001 (AI management systems — **certifiable**); ISO/IEC 22989 for the vocabulary; NIST AI RMF for the function taxonomy; OWASP Top 10 for LLM Applications and the Agentic Security Initiative for the **threat classes**; OpenTelemetry GenAI semantic conventions for the telemetry attributes; the Model Context Protocol specification for the interface (ADR-0053) |

## The rows that will fight the inclusion test

Recording these now, because they are where an invented "standard" would enter:

- **#35 Technology strategy and roadmaps** has **no external anchor at all.** A roadmap is a
  company's plan; there is no body that fixes what one must contain. It stays on the roster because
  the owner listed it, and what it can honestly contribute is **the decisions a strategy must
  record** — never their answers. If it is ever written as guidance, it is policy.
- **#4 Clean code** is the row most likely to become a rulebook. Its advice is largely choosable;
  what survives is vocabulary and the few measurable properties (cyclomatic complexity is defined,
  its acceptable value is not).
- **#16 Observability/SRE** carries a real standard (OpenTelemetry) *and* a book. Signals and
  vocabulary are admissible; **an SLO is a commitment a project makes**, and no level belongs here.
- **#29 FinOps** and **#26 TOGAF** are frameworks a company may reasonably decline. Their
  vocabulary and capability taxonomies are admissible; adopting them is a project decision.
- **#12 DevOps** already has its metrics in the platform catalogue with the bands deliberately
  excluded — that node group is the worked example for how the rest of this roster should look.

## How a row becomes knowledge

1. A real project needs it (W5 — nothing is pre-built).
2. Its scope is checked against the anchor column above. **No anchor, no statement** — only the
   decision the project must make.
3. Concepts land as `CPT-*` nodes in `docs/25-concepts/`; cross-cutting invariants land as rules in
   an existing family or, if genuinely a new axis, behind an ADR.
4. The selection is declared to the owner before development (**PLT-R7**), because a project that
   does not know which knowledge governs it is not being governed by it.
