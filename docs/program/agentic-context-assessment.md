---
id: program-agentic-context-assessment
title: "Context Engineering · RAG · Memory · Agentic AI — the reference model and what this estate is missing"
type: program
owner: orchestrator
status: active
since: 2026-08-04
updated: 2026-08-04
relations:
  - { type: part-of, target: index-program }
  - { type: refines, target: program-context-architecture-audit }
  - { type: governed-by, target: governance-root }
---
# Four pillars — the reference model, and the gap measured against it

> **What this adds to the audit next door.**
> [context-architecture-audit.md](context-architecture-audit.md) answered *one proposal* — 28
> requirements someone wrote — and found two thirds of it greenfield. This document asks the harder
> question in the other direction: **not "is this proposal right?" but "what would a complete system
> in these four disciplines have, and which of those does this estate lack?"** The difference matters,
> because a proposal can only surface the gaps its author happened to think of. A reference model
> surfaces the ones nobody proposed.
>
> **Non-authority.** Like the audit, this is a program document. It cites the authorities and states
> no rule of its own. Where it recommends, it recommends as a **selectable list** (PLT-R6).

## 1. The reference model

Assembled from current practice rather than from memory — the sources are listed in §6. Four pillars,
and the ordering is deliberate: each one is a consumer of the one before it.

**Context engineering** is the discipline of deciding what occupies the model's attention at each
step. The field converged on four verbs — **write** (persist outside the window), **select** (pull in
what the step needs), **compress** (keep only the tokens that still matter), **isolate** (split work
so sub-tasks do not contaminate each other) — plus two properties that make the verbs honest: a
**measured budget** and a **freshness signal**.

**RAG** is one implementation of *select*. Its mature form is not "embed and search": it is chunking
with intent, a lexical and a dense channel fused, a reranker over the fusion, an optional graph
channel for questions that span documents, and — the part most systems skip — **measurement of the
retrieval itself**, separately from measurement of the answer.

**Memory** is what survives a session. The three-tier taxonomy is stable across the 2026 surveys —
**episodic** (what happened, when), **semantic** (what is known), **procedural** (how a task is
performed) — over a working tier that is the window itself. A memory system is judged by five
operations: **store, retrieve, update, compress, forget** — and by whether anything defends the store
against being poisoned.

**Agentic AI** is what acts on all of it. The pattern catalogue is likewise settled: **planning**
against an explicit plan object, **tool use**, **reflection**, **orchestrator-worker**,
**evaluator-optimizer**, **human-in-the-loop** — with the standing warning that the failures of
2024–2026 in production were **architectural, not model-quality** failures, so each control is added
against a named failure mode rather than because it is on the list.

**The evidence that binds the four together** is context rot: across eighteen frontier models,
accuracy degrades with input length **non-uniformly**, and it degrades *faster* when distractors are
semantically close to the answer than when the input is merely long. That is the finding that makes a
word budget a real instrument and not bookkeeping — and it is the reason a *smaller, better-selected*
context beats a larger one.

## 2. The gap matrix

Status is measured, not estimated. **Have** = a mechanism exists and something enforces it. **Partial**
= the mechanism exists and its claim is narrower than the capability. **Gap** = absent. **Non-goal** =
absent on purpose, with the reason and the reversal condition stated.

### Context engineering

| # | Capability | Status | Evidence |
|---|---|---|---|
| 1 | Attention budget measured, not assumed | **have** | G14 prices six load sets by what a session reads *together*; largest is `planning` at 18,916 words ≈ 25,200 tokens (ADR-0041) |
| 2 | Write — context that survives the window | **have** | ADRs, `WORKFLOW.md`, the three registers, the two archives |
| 3 | Select — task kind bound to inputs | **have** | the `load-sets` manifest; `tools/context_set.py` resolves and prices a session (ADR-0050) |
| 4 | Compress | **partial** | the **structural exit** each set declares, taken four times (slice selectors, archive files). No summarization: compaction of a live session is the harness's job, not the repository's |
| 5 | Isolate | **have** | seven lane-scoped agent profiles in `.claude/agents/`; the critic is read-only, so generator and critic cannot share a state |
| 6 | Instruction layering | **have** | `CLAUDE.md` → skills → `how-to/` → templates, with the form taxonomy fixed by ADR-0044 |
| 7 | A machine interface for consuming projects | **gap** | ADR-0030 says a project references nodes **by stable ID**; the only way to do that today is to clone the repository and open files |
| 8 | Freshness / context diff | **have** | G15 digests every watched file; G13 proves `updated:` is the real last change |
| 9 | Observability of what was actually read | **gap** | the resolver prints a *plan*; nothing records the *actual*, so no session can be re-examined after the fact |

### RAG

| # | Capability | Status | Evidence |
|---|---|---|---|
| 10 | Chunking with intent | **have** | one concept per node, G9-budgeted at 700 words — semantic chunking done at authoring time instead of at indexing time |
| 11 | Lexical channel (BM25) | **non-goal** | `grep` over 284 tracked Markdown files is exhaustive and exact; reversal condition in ADR-0050 |
| 12 | Dense channel (embeddings) | **non-goal** | same condition. Today the repository has **zero runtime dependencies** — a position worth pricing before giving it up |
| 13 | Fusion + cross-encoder rerank | **non-goal** | there is nothing to fuse until 11 and 12 exist |
| 14 | Graph channel | **have, and stronger than the usual form** | 243 nodes / 568 typed edges, **authored and gate-verified** — G4 every edge resolves, G5 no orphan, G6 authority never cycles. GraphRAG's advantage on cross-document questions comes from a graph *extracted* by a model; this one is declared and checked, so it cannot hallucinate an edge |
| 15 | Query understanding / decomposition | **not applicable** | there is no query endpoint. The "query" is the session's task, and the manifest binds task kind to inputs |
| 16 | Retrieval **recall** measured | **have** | G19 — every evaluation task declares `Must reach:` and the gate asserts its set carries those tokens (ADR-0051) |
| 17 | Retrieval **precision / utilization** measured | **gap** | nothing measures whether loaded context was *used*. The literature puts roughly 40% of RAG quality variance in utilization rather than retrieval, and this estate measures the other 60% only |
| 18 | Faithfulness — the answer rests on the context | **have** | `tools/context_eval.py` — six checkers over twelve discriminating samples, each self-tested; `live_concept_ids()` rejects a citation to a concept that does not exist. This is RAGAS-faithfulness **without a judge model**, which ADR-0043 rejected on recorded bias grounds |
| 19 | Source freshness | **partial** | per-entry verification dates in the regulatory reference; risk #12 stays open because no gate can check that a source still says what was quoted |

### Memory

| # | Capability | Status | Evidence |
|---|---|---|---|
| 20 | Working tier | **have** | the window, priced by G14 |
| 21 | Episodic — what happened and when | **have** | `improvement-register.md`, 47 dated incidents; `WORKFLOW-archive.md`; the evaluation records |
| 22 | Semantic — what is known | **have** | the governed estate: 167 concept nodes, 14 department rule families, the foundation rules |
| 23 | Procedural — how a task is performed | **have** | `how-to/`, `review-protocol.md`, the skills, the `Makefile` targets |
| 24 | **Consolidation** — episodic distilled into semantic | **have, and it carries an invariant** | `known-pitfalls.md` distils the register into decision rules, each citing its row, under a written rule: *a lesson added to the register is distilled here in the same change*. Most memory systems store episodes and never derive from them |
| 25 | Update / supersession | **have** | append-only with a retired roster that stays listed; G7, G11, G16 |
| 26 | Forget / decay | **non-goal** | an estate whose old citations must keep resolving cannot forget. The cost is paid by **compression** instead — archive files, nothing deleted. Stated so that the absence is a decision rather than an oversight |
| 27 | Defence against a poisoned store | **partial, and this is the sharp edge** | the gates cover *structure* — unique IDs, resolving links, a cited source, a live concept ID. Nothing covers *content truth*: risk #11 is open, and no gate can tell a standard from a plausible-looking invention. **New exposure:** sessions now read web pages, GitHub comments and CI logs, and no rule governs what may be written from an untrusted source into a register that every later session loads |

### Agentic AI

| # | Capability | Status | Evidence |
|---|---|---|---|
| 28 | Planning against an explicit plan object | **have** | `WORKFLOW.md` as the ordered backlog; the phase structure |
| 29 | Reflection / self-critique | **have** | `evaluation.md`'s self-review; the read-only `quality-reviewer` profile |
| 30 | Orchestrator-worker | **have** | seven profiles, each scoped to one lane (ENG-R8) |
| 31 | Evaluator-optimizer | **have, and the evaluator is itself tested** | the gates are the evaluator; `tools/test_gates.py` plants one violation per **claim** and requires that gate — and no other — to fire (ADR-0042). Testing the evaluator is the step almost nobody takes |
| 32 | Human-in-the-loop | **have** | PLT-R6 selectable lists; new-technology adoption is owner-gated |
| 33 | **Outcome** evaluation of a cold agent | **have** | ADR-0043: cold subagents, a declared load set, deterministic scoring, freshness-gated |
| 34 | **Trajectory** evaluation — did it follow the process? | **gap** | nothing measures whether the six ENG-R9 checks ran, whether the prompt was refined first, or whether a gate was run before a green claim was made. Every failure of that class in the register was caught by a human reading a transcript |
| 35 | Session observability | **gap** | no trace of an agent session exists. The OpenTelemetry GenAI semantic conventions are the settled shape for this — LLM spans, agent spans, tool spans, session metrics |
| 36 | Agentic threat model | **gap** | practice area #17 anchors application security (OWASP ASVS, CWE, NIST SSDF). Nothing anchors the agent layer: goal hijacking, tool misuse, memory and context poisoning |
| 37 | Cost accounting | **partial** | words serve as a token proxy; no runtime cost or latency is recorded, because nothing runs yet |

**Count: 33 applicable capabilities — 21 have, 5 partial, 6 gap; 4 declared non-goals with a reversal
condition.** The shape of that result is consistent and worth saying plainly: **this estate is
unusually strong wherever a property can be checked deterministically, and absent wherever a property
requires something to be running.** That is not a coincidence — it is the direct consequence of
ADR-0037 leaving one application in the tree, and that application not yet being built.

## 3. The finding the reference model surfaced and no proposal did

**The engineering axis has no practice area for the discipline this repository runs on.**

`practice-areas.md` rosters thirty-five areas and anchors each one. Area #21 is *AI and machine
learning* (ISO/IEC 22989), #22 is *MLOps and LLMOps* (ISO/IEC 42001, NIST AI RMF), #30 is *technology
governance* (ISO/IEC 38500, 42001 for the AI slice). **Building software with agents — context
assembly, retrieval, memory, tool design, agent evaluation, agent security — appears in none of
them.** Every project in the portfolio this context governs will be built the way this repository is
being built, and the axis that exists to say *how software is engineered* is silent about it.

It is also **anchorable**, which is the test that matters: ISO/IEC 42001 is certifiable, ISO/IEC 22989
fixes the vocabulary, NIST AI RMF fixes the function taxonomy, the OWASP LLM and Agentic top-ten lists
fix the threat classes, the OpenTelemetry GenAI semantic conventions fix the telemetry attributes, and
the Model Context Protocol is a published specification. An area with six candidate anchors is not a
consensus area — it is one that was simply never rostered.

## 4. The recommendation, as a selectable list (PLT-R6)

Ranked by ratio of value to new technology. **None of A–D adds a runtime dependency.**

- **A — Roster the missing practice area.** Add area #36, *context engineering and agentic systems*,
  with its anchors, status `—` like every other row (W5 forbids speculative pre-build). Cost: one
  table row and an ADR. This is the cheapest item and the one that stops the gap being reintroduced.
  **Recommended, and taken in this change** — see ADR-0053.
- **B — Give the dossier a gate.** The steering document was 6 days stale and wrong about six
  counted facts. Mechanize it: the dossier declares its numbers, a gate recomputes them, and drift
  reddens. **Recommended, and taken in this change** — G21, ADR-0052.
- **C — Write the agentic threat model, and one rule with it.** The specific hole is that untrusted
  text — a fetched page, a PR comment, a CI log — can be written into a register that every later
  session loads, and nothing says it may not. This is *memory poisoning* in the OWASP sense, on an
  estate whose whole value is that its memory is trustworthy. **Recommended next**; it is a risk-register
  entry plus one clause, not a project.
- **D — Emit agent-session telemetry into the tier already being built.** ADR-0036 gives the
  repository a ClickHouse telemetry tier and a Rust ingester; ADR-0031/0034 give it a monitoring
  application whose job is to make the portfolio visible. An agent session is portfolio activity. Emit
  OpenTelemetry GenAI spans into the same tier and capabilities 9, 34, 35 and 37 close **as a
  by-product of M4** rather than as a second system. **Recommended, sequenced with M4** — not before
  it, because it needs the ingester's read surface.
- **E — Measure utilization, not only reach.** G19 proves a set *can* answer its question; nothing
  proves the answer *used* it. A deterministic form exists — require an answer to cite the member it
  rests on, then check the citation resolves, which is what `live_concept_ids()` already does for
  concepts. **Offered, not recommended yet**: it changes what an evaluation task asks for, and that is
  a decision about the measurement rather than a fix to it.
- **F — Build the retrieval stack** (embeddings, vector store, reranker, cache, pipeline).
  **Not recommended.** Unchanged from the audit: at 243 governed documents exhaustive graph traversal is exact,
  cheap and auditable, and ADR-0050 records the condition under which that stops being true. Adopting
  it now would also collide with ENG-R8, ADR-0002 and the zero-runtime-dependency position.
- **G — Expose the context over MCP** so a project can reference a node by ID without cloning.
  **Offered, owner-gated.** It is the honest mechanism for ADR-0030's promise and it is a **second
  application**, which ADR-0037 and ADR-0031/0034/0036 do not permit quietly — it needs a decision,
  not an implementation.

## 5. What this does not claim

The matrix scores **presence of a mechanism**, not quality of outcome. A capability marked *have* can
still be weak, and two of them are known to be: risk #11 (no gate distinguishes a standard from a
plausible invention) and risk #12 (a citation can stop matching its source). Both stay open on
purpose, because the alternative is a check that would have to be believed rather than run.

And the four non-goals are the load-bearing part of this assessment, not the leftovers. A system that
implemented all 33 capabilities on a corpus this size would be **worse** than this one: slower to
audit, impossible to reproduce deterministically, and dependent on a model's judgement in exactly the
places where a gate currently gives a yes or a no. The reference model is a checklist to *reason
against*, never a specification to satisfy.

## References

- Measurements taken 2026-08-04 against `git ls-files`, front-matter relation parse, the `load-sets`
  manifest and `tools/verify.py`'s own reported totals.
- Anthropic, *Effective context engineering for AI agents* — the attention-budget framing, and
  compaction, structured note-taking and sub-agents as the three long-horizon techniques.
- LangChain, *Context engineering for agents* — the write / select / compress / isolate decomposition.
- Chroma Research, *Context Rot: how increasing input tokens impacts LLM performance* — eighteen
  models, non-uniform degradation, semantic distractors dominating length.
- *Anatomy of Agentic Memory* (arXiv 2602.19320) and the 2026 agent-memory surveys — the
  episodic / semantic / procedural taxonomy and the five memory operations.
- RAGAS metric definitions (context precision, context recall, faithfulness); GraphRAG on
  cross-document questions; hybrid retrieval with cross-encoder reranking as the current default.
- OWASP Top 10 for LLM Applications and the Agentic Security Initiative's threat taxonomy — agent
  design, agent memory, planning and autonomy, tool use, deployment.
- OpenTelemetry GenAI semantic conventions — LLM, agent and tool spans; session metrics.
- Internal authorities cited above: ADR-0030, ADR-0031/0034/0036, ADR-0037, ADR-0041, ADR-0042,
  ADR-0043, ADR-0044, ADR-0050, ADR-0051 · ENG-R8 · PLT-R6 · G4, G5, G6, G9, G13, G14, G15, G19 ·
  risk #11, risk #12.
