---
id: program-context-architecture-audit
title: "Context Architecture — audit before any Context-OS work"
type: program
owner: orchestrator
status: active
since: 2026-08-04
updated: 2026-08-04
relations:
  - { type: part-of, target: index-program }
  - { type: governed-by, target: governance-root }
---
# Context architecture — the audit that comes before any Context-OS work

> **Why this document exists.** A proposal arrived to evolve this repository's context system into a
> *Context OS*: hybrid retrieval, embeddings, reranking, recursive retrieval, claim verification,
> reflection loops, hierarchical memory, multi-level caches. Its own first requirement is an audit
> before any code. This is that audit, and it reaches a conclusion the proposal did not anticipate.

## 1. The fact that reframes the request

**There is no retrieval system here to improve.** Measured, not assumed:

| Component the proposal asks to audit | Present |
|---|---|
| Embeddings, vector store, reranker, BM25 library | **none** |
| LLM SDK or any model call from repository code | **none** |
| Cache layer of any kind | **none** |
| Runtime dependency, npm | **`dependencies: {}`** — five dev-only packages |
| Runtime dependency, Cargo | **two** (`rust_decimal`, `serde_json`) |

The context mechanism is a **declared manifest plus a typed graph plus deterministic gates**. An agent
reads files directly; nothing ranks, embeds or fetches. So roughly two thirds of the proposal is not
*improvement* — it is a greenfield subsystem, and the audit's job is to say which parts of it this
estate needs.

## 2. What exists, and it is more than the proposal assumes

- **A typed knowledge graph: 240 nodes, 559 edges** over five relation types in use
  (`governed-by` 240, `part-of` 239, `depends-on` 49, `traces-to` 23, `refines` 8). **G4** proves every
  edge resolves, **G5** proves no orphan by `part-of` traversal, **G6** proves authority never cycles.
  The proposal's *Context Graph* requirement is already met at the storage layer.
- **Deterministic answer verification (ADR-0043).** Ten checkers, each carrying a compliant and a
  violating sample and self-tested. Three tasks are scored on a **declared `answer` block** — which is
  the proposal's *claim extraction* and *claim verification*, implemented without a model in the loop.
- **A context-diff mechanism (G15).** A `sha256:12` digest per context-defining file; a measurement is
  invalidated the moment an input moves, and the watched set is **derived from the manifest** so it
  cannot drift.
- **Token accounting (G14, ADR-0041).** Six load sets priced by total words, each with a declared
  ceiling and a *structural exit* recorded for when it is reached.
- **Curated memory.** `improvement-register.md` is the append-only record (40 incidents),
  `known-pitfalls.md` its distillation into decision rules, `risk-register.md` the standing exposures.
  This is the proposal's *semantic memory* — knowledge extracted from events, not transcripts kept.

## 3. The five real weaknesses

**W1 — Retrieval reaches 7% of the estate.** The six declared load sets name **17 distinct files** out
of 240 governed documents. Among those 17 there are **zero concept nodes** (of 167) and **zero
department rule files** (of 14). A session authoring a concept node is given the template and two
foundation rule files and **no example node, and no sibling from its department**. The knowledge this
repository exists to hold is unreachable by any declared context path. *This is the finding that
matters most, and it is not addressed by adding embeddings — it is addressed by using the 559 edges
that already exist.*

**W2 — Coverage is never checked against the question.** Nothing asks whether the assembled context
can answer what was asked. Evidence: the `unit-codes` evaluation task was declared against a set
carrying no unit codes; two correct answers were scored as failures before the *manifest* was
identified as the defect (improvement #34). That was found by accident, not by a check.

**W3 — Contradiction detection does not exist, and the cost is measured.** **ENG-R10.7 instructed
exactly what gate G10 rejects — for six weeks — while citing G10 as its enforcer.** ADR-0035 wrote the
clause; ADR-0037 reversed its premise seven days later and nothing swept the rules. No gate can catch
a semantic contradiction between prose and code. This is the proposal's requirement 11, and it is the
one with a proven, dated failure behind it.

**W4 — The graph is proven but unused for assembly.** 559 typed edges exist and nothing traverses them
to build context. `depends-on` and `traces-to` — 72 edges that state exactly *what a node needs* —
are read by no retrieval path.

**W5 — G14 prices the declaration, not the session.** The ceiling is checked against the manifest. What
a session actually opens is unmeasured, so a set can be respected on paper and exceeded in practice.

## 4. The proposal's 28 requirements, sorted

**Already satisfied, deterministically (do not rebuild):** Context Graph (6) · Context Diff (19) ·
Claim Extraction (13) · Claim Verification (14) · Semantic memory (18) · Configuration (24) · modular
design, code quality, documentation (22, 25, 26). The estate is unusually strong here **because these
are gates rather than model judgements** — and ADR-0043 rejected an LLM judge on recorded bias
grounds. Replacing a deterministic check with a model would be a regression.

**Worth building, and cheap because the substrate exists:** graph-driven retrieval (3 in part, 5, 6) ·
coverage analysis (8) · gap detection (9) · contradiction detection (11) · sufficiency check (10) ·
observability over what was read and discarded (23).

**Greenfield and requiring an owner decision before any code:** embeddings, vector search, BM25,
reranking (2, 3) · multi-level caches (20) · the full 18-stage pipeline (21) · reflection loops and
model-scored confidence (15, 16) · hierarchical memory tiers (17).

**Does not apply here:** query rewriting and intent detection (4, 12) as described. There is no query
endpoint — the "query" is a session's task, and the manifest already binds task kind to inputs.

## 5. Three collisions the owner must resolve first

1. **New technology.** A vector store, an embedding model and a reranker are each an adoption
   decision: **ENG-R8** (exclusive lanes), **ADR-0002** (OSI, commercially usable), and `CLAUDE.md`
   — *ask before adopting a new language or framework*. Today the repository has **zero runtime
   dependencies**, which is a position worth pricing before giving it up.
2. **Where it would live.** **ADR-0037** holds that this repository carries only externally-fixed
   knowledge, and **ADR-0031/0034/0036** hold that monitoring is *the one application built here*. A
   Context OS is application code. Either it becomes a **second** application — reversing that
   decision explicitly — or it belongs to a project that consumes this context. It cannot quietly
   become a third thing.
3. **Sequencing against M4.** There is **no binary in the tree**. The monitoring application is what
   makes the portfolio visible and is the reason a knowledge repository ships a dashboard at all.
   Building a Context OS first delays it.

## 6. What this audit recommends

**Do W1 through W4 as gates and generated artefacts, not as a pipeline.** Derive load sets from the
graph so authoring a node reaches its department and its exemplar; assert coverage of a task's declared
concepts; extend the gates to catch a rule clause that contradicts a gate. Every one of those is
deterministic, costs no new dependency, and attacks a failure this estate has actually suffered.

**Defer the retrieval stack until a corpus exists that a manifest cannot serve.** At 240 documents and
559 edges, exhaustive graph traversal is cheaper and more auditable than approximate similarity
search. The proposal's own requirement 28 says not to implement a technique merely because it appears
on the list — this audit takes that seriously.

## 7. What was built, and what the building found (2026-08-04)

**ADR-0050 and ADR-0051 implemented §6's recommendation.** The four weaknesses this audit named are
now mechanised, and the work found two defects the audit had not:

| Weakness | Closed by | Status |
|---|---|---|
| W1 retrieval reaches 7% | `tools/context_set.py` + the `graph:` selector + exemplar reach | done |
| W2 coverage unchecked | **G19** — `Must reach:` per task, asserted against its set | done |
| W3 no contradiction detection | **G20** — vocabulary exercised or reserved; `implements` retired | done, narrowly |
| W4 graph unused for assembly | the resolver traverses `part-of`/`depends-on`/`traces-to`/`refines` | done |
| W5 G14 prices the declaration | the resolver reports both quantities, separately | done |

**W3 deserves its qualifier.** A semantic contradiction between prose and code is **not decidable**,
and this estate has paid four times for prose heuristics that fire on text merely *naming* a defect.
G20 does not attempt the general problem: it removes the **affordance**. ENG-R10.7 could express its
contradiction because the vocabulary still offered an `implements` edge; with the type retired, the
sentence has nothing to point at. That is a narrower claim than the proposal's requirement 11, and it
is one a gate can honestly make.

**Two defects the audit missed, found by building rather than by reading.**

- **A fabricated concept ID passed the evidence check.** `CPT_ID` was only ever asked whether
  *something* CPT-shaped appeared; `CPT-4242` satisfied the check whose whole purpose is that answers
  rest on evidence — the mirror of a validation rule IDs had all along. This is the single clearest
  hallucination vector the estate had, and the audit did not see it because it read the *architecture*
  and not the *predicates*.
- **The exemplar was unreadable.** ADR-0048 declared `01-procurement` the exemplar *because a model
  imitates a real example more reliably than it deduces from prose*, and then it sat in no load set.
  Declared and unreachable is the same failure as W1, one layer up.

**The lesson for the next audit: read the predicates, not only the components.** W1 through W5 were
found by measuring structure. Both of these were found by measuring what a check actually *asserts*,
which is a different sweep and the one that caught the hallucination.

## References

- Measurements taken 2026-08-04 against commit `32d9140`: `git ls-files`, front-matter relation parse,
  `load-sets.md` manifest expansion, dependency manifests.
- ADR-0041 (load sets) · ADR-0043 (context-adherence evaluation, and the rejection of a judge model) ·
  ADR-0037 (what this repository may hold) · ENG-R8 · ADR-0002.
