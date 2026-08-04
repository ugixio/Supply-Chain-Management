---
id: program-state-of-project
title: "State of the Project — the dossier the owner steers by"
type: program
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-08-04
relations:
  - { type: part-of, target: index-program }
  - { type: depends-on, target: program-agentic-context-assessment }
  - { type: governed-by, target: governance-root }
---
# State of the Project — the dossier

> **What this is.** The one document written to be read *before deciding*: what exists, what it is
> worth, what is missing, what is blocked and what the next decision is. **Non-authority** — it cites
> the ADRs, the rules, the product model and `WORKFLOW.md` and never restates them as new truth.
>
> **Two kinds of statement live here and they are marked apart.** The **counted facts** in §1 are
> recomputed from the estate by **gate G21** and cannot go stale silently: any change that moves one
> of them reddens the gate until this file is updated in the same commit (ADR-0052). Everything else —
> percentages, grades, verdicts — is **interpretation for steering**, refreshed whenever the dossier
> is, and never gated, because a gate over a judgement would only make the judgement look official.
>
> **Why it is not on a calendar.** A staleness check on wall-clock age reddens correct work during a
> quiet week, and a gate that reddens correct work gets disabled rather than obeyed (known pitfall,
> improvement #16). So the trigger is **drift, not time**: the dossier is refreshed on the change that
> makes it wrong.

## 1. Counted facts — recomputed by G21

```dossier
snapshot         2026-08-04
governed-docs    245
concept-nodes    167
departments      14
graph-edges      574
adr-decisions    55
gates            22
gate-mutants     33
eval-checkers    6
eval-samples     12
load-sets        6
```

Read as: **245 governed documents** carrying **574 typed edges**, of which **167** are concept nodes
across **14** departments; **55** recorded decisions; **22** doc gates proved by **33** planted
mutants; a context-adherence measurement with **6** checkers and **12** discriminating samples; and
**6** declared load sets pricing what a session reads together.

## 2. What the project is

The **Global Context** a technology company consults to run itself and to build software well —
two axes (ADR-0045): the fourteen supply-chain departments as the operating disciplines, and the
engineering practice areas as the build disciplines. It governs a **portfolio of projects** that
reference its nodes by stable ID and overlay their own policy (ADR-0030), and it holds **no company's
data** (ADR-0037). The **one application it builds is monitoring**, because a company selling
technology has to see the state of what it is building (ADR-0031/0034/0036).

## 3. Completion by layer (estimate, for steering)

| Layer | State | Est. |
|---|---|---|
| The context — standards, 167 concept nodes, rule families, 55 ADRs, the node model | substantial, gate-enforced, and **the policy sweep is complete** across nodes, department rules and the agent layer | ~85% |
| The context *mechanism* — load sets, the graph resolver, the adherence measurement, 22 gates | the estate's strongest asset and now measured against an external reference model | ~80% |
| Standards reference data (`packages/shared`) | ISO 8601/4217/3166, UN/ECE Rec 20, GS1 keys + check digit, Incoterms 2020, SCOR | ~40% |
| Exact money arithmetic (`crates/scm-money`) | complete, tested, no policy | ~95% |
| Telemetry tier (`db/clickhouse`, `crates/scm-ingest*`) | schema with its own gate, split-privilege identities, ingestion core **and** transport half, flow/level split enforced structurally | ~70% |
| Monitoring application (M4/M5) | decided in ADR-0049, **no binary in the tree** | ~5% |
| Workspace / projects layer | modelled, not built; **no machine interface** for a project to read a node by ID | ~5% |
| **Overall** | | **~40%** |

The overall figure moved from ~20% to ~40% without a line of application code, and that is the honest
reading rather than a generous one: what was ~20% counted a context that carried policy the inclusion
test forbids, had no measurement of its own use, and reached 7% of itself. All three are now false.

## 4. Scorecard (verdict · evidence)

- **Knowledge governance** — *strong, and the estate's differentiator*. Tiered docs, one-way SSOT,
  append-only decisions, stable IDs, 22 gates in CI, a typed graph proved acyclic. **And the gates are
  themselves tested** — `tools/test_gates.py` plants one violation per *claim* and requires that gate
  and no other to fire (ADR-0042), which is the step most estates skip.
- **Context engineering** — *measured against an external reference model for the first time*. See
  [agentic-context-assessment.md](agentic-context-assessment.md): of 33 applicable capabilities across
  context engineering, RAG, memory and agentic AI, **21 have · 5 partial · 6 gap**, with 4 declared
  non-goals. The shape is consistent — strong wherever a property can be checked deterministically,
  absent wherever it requires something to be running.
- **Policy separation** — *complete as a sweep, permanent as a discipline*. Nodes (C1), all fourteen
  department rule families (C2) and `.claude/**` (risk #13, swept 2026-07-29) carry the inclusion
  test. The residual is the **class**, not the instances: no gate can distinguish a target from a
  definition, so the next file added can reintroduce it.
- **Standards fidelity** — *improving; two named residuals*. Risk #11 — no gate tells a standard from
  a plausible-looking invention. Risk #12 — a citation can stop matching its source without anything
  changing here, which C5 caught publishing a superseded CSDDD phase-in. Both open on purpose.
- **Money precision** — *resolved*. One implementation, `crates/scm-money`: exact decimal,
  `roundTiesToEven` (SCM-R14), sum-preserving apportionment, overflow reported not wrapped, no
  `unsafe`. ADR-0047 fixed it as the Rust core's responsibility; the TypeScript and Python mirrors
  that used to disagree are gone.
- **Measurement discipline** — *rare, and worth protecting*. MSR-R2's forbidden aggregation is not
  something a dashboard can select by mistake: `telemetry.levels_1m` exposes no sum column at all and
  `apply.py` fails if it grows one (risk #14). The invariant is enforced by the **shape of the read
  surface**, not by a warning.
- **Security** — *two halves, one covered*. Data-plane: split-privilege ClickHouse identities with
  quotas; the ingester refuses non-finite values, ungoverned metrics and future timestamps.
  **Agent-plane: opened 2026-08-04 (ADR-0054).** `50-engineering/agentic-threat-model.md` maps the
  OWASP Agentic Security Initiative's fifteen classes onto this repository — **six live, four latent
  until M4, five inapplicable** — and knowledge-architecture §7 now prohibits undeclared external
  content, with **G22** gating the one part a gate can decide. **What is still open is the
  undecidable half**: whether a session was *redirected* by something it read, and a claim that
  arrives with no URL at all. Risk #16 stays open for those.
- **CI/CD** — *partial*. Actions runs `make verify-full` and `make verify-schema` against a real
  ClickHouse service container. No deploy pipeline, no containerization, no runtime observability (M5).
- **UI** — *specified only* (ADR-0026: octagon node-graph, LED-cyan `#22d3ee`). No UI exists.

## 5. The six open gaps, ranked

From §2 of the assessment. Ranked by value over new technology; **none of the first three adds a
runtime dependency.**

| # | Gap | Why it matters | Disposition |
|---|---|---|---|
| 1 | ~~No agentic threat model~~ | **closed 2026-08-04 (ADR-0054, G22).** The estate had zero external URLs and the tree had one, so the guard is on an *absence*: no sweep, green on landing. The residual is the undecidable half — intent, and a claim with no URL | **done**; risk #16 narrowed, not closed |
| 2 | **No agent-session telemetry** | nothing traces what a session read, did, or spent. Closes capabilities 9, 34, 35 and 37 at once | **sequenced with M4** — emit OTel GenAI spans into the tier ADR-0036 already built |
| 3 | **No trajectory evaluation** | outcome is measured (ADR-0043); *process* is not. Whether the six ENG-R9 checks ran, or a gate was run before a green claim, is caught only by a human reading a transcript | after 2, which supplies the trace it would score |
| 4 | **Utilization unmeasured** | G19 proves a set *can* answer its question; nothing proves the answer used it. The literature puts ~40% of RAG quality variance here | offered, needs a decision about what a task asks for |
| 5 | **No machine interface for consuming projects** | ADR-0030 promises reference-by-ID; the only mechanism today is cloning the repository | **owner-gated** — an MCP server is a *second application*, which ADR-0037 does not permit quietly |
| 6 | **Retrieval stack absent** | embeddings, vector store, reranker, cache | **not recommended**; ADR-0050 records the condition that would change this |

## 6. Decisions waiting on the owner

Nothing blocks M4. These are the choices that will be asked with speed and security trade-offs when
their moment arrives (ADR-0002: OSI, commercially usable, modifiable):

- an **auth library** — Zitadel went AGPL in 2025, so licence first;
- a **secrets vault** — Vault is BUSL, so **OpenBao**;
- a **charting library** for the dashboards;
- the **broker/cache** pair (NATS or Kafka + Valkey), which ADR-0034/0036 keep gated until
  measurement shows the Rust ingester plus ClickHouse cannot absorb the rate;
- **gap 5 above** — whether this repository gains a second application, or a consuming project owns
  the interface.

## 7. Route

**Done:** the ADR-0037 reframe and its sweep · Phase C (nine items) · M1 platform nodes · M2
ClickHouse telemetry tier with its own gate and the flow/level split · M3a ingestion core · M3b
transport half · the context layer (ADR-0050/0051: the graph resolver, G19, G20, the fabricated-citation
fix) · this assessment and the dossier's gate (ADR-0052/0053).

**Next, in order:** **gap 1** (the agentic threat model, cheap and outstanding) → **M4** NestJS +
GraphQL and the Next.js dashboards, per ADR-0049 → **gap 2** riding on M4's telemetry → **M5** Docker
then Kubernetes.

## 8. How this document stays true

1. **The counted facts are gated.** G21 recomputes all eleven and fails on drift, so this file cannot
   quietly describe a repository that no longer exists — the failure mode of every status document.
2. **G21 refuses a fact it cannot measure.** A key it does not know how to recompute is a failure, not
   a pass: the load-set manifest paid for that lesson when an unimplemented selector priced the wrong
   thing, and a dossier that can declare unverifiable numbers is the same defect.
3. **`snapshot` must equal `updated:`,** which G13 already proves is the file's real last change. So
   the date cannot be older than the content and cannot be newer than the work.
4. **The interpretation is refreshed with the facts,** in the same change. A gated §1 beside a stale
   §4 would be worse than no gate, because the true numbers would lend the stale verdicts authority.
5. **Governing refs:** `CLAUDE.md` · `docs/10-decisions/README.md` · `50-engineering/rule.md` ·
   `30-foundation/*/rule.md` · `20-product-model/*` · `WORKFLOW.md` ·
   [agentic-context-assessment.md](agentic-context-assessment.md) ·
   [context-architecture-audit.md](context-architecture-audit.md).
