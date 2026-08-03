---
id: index-concepts-00-platform
title: "Concepts — Platform delivery metrics (00)"
type: concept
owner: orchestrator
status: active
since: 2026-07-27
updated: 2026-08-03
relations:
  - { type: part-of, target: index-concepts }
  - { type: governed-by, target: index-adr }
  - { type: traces-to, target: rule-platform }
---
# Concepts — Platform delivery metrics (00)

> The metrics the **monitoring application** computes over a project's development progress — the
> one application this repository builds (ADR-0031/0034/0036). They are **platform** concepts, not
> a supply-chain department: the product statement puts them in this same `CPT-*` catalogue rather
> than a second one, because a project consults one catalogue for what a number means.
>
> Same contract as every other node: what the metric *means*, the identity where one exists, its
> units, its assumptions, the values a project must choose — and **no targets**.

## The trap these metrics attract

Published delivery benchmarks come with **performance bands** — labels like "elite" or "high"
attached to numeric cut-offs, derived from a survey population. They are the exact shape of the
mistake ADR-0037 corrected: *"world-class OTD ≥ 95%"* is a textbook illustration, and
*"elite teams deploy on demand"* is a survey finding. Both read as requirements the moment they
appear in a table headed **target**.

**No node here carries a band.** A project comparing itself against its own history is doing
something meaningful; a project comparing itself against a survey's cut-off has adopted another
population's distribution as a goal.

The second trap is subtler and is called out per node: **each of these metrics is gameable in
isolation.** Deployment frequency rises if you split one change into five. Change failure rate falls
if you stop calling incidents failures. Lead time shortens if you branch later. Rework rate falls if
you put the hotfix on the plan. Each node names what it can be traded against, because a monitoring
dashboard that shows one of them alone is an invitation.

## Catalogue

### Throughput

| ID | Concept | What it answers |
|---|---|---|
| [CPT-0155](deployment-frequency.md) | Deployment frequency | How often change reaches production |
| [CPT-0156](lead-time-for-changes.md) | Lead time for changes | How long a change takes to get there |
| [CPT-0158](failed-deployment-recovery-time.md) | Failed-deployment recovery time | How quickly a degradation is resolved |

### Instability

| ID | Concept | What it answers |
|---|---|---|
| [CPT-0157](change-failure-rate.md) | Change failure rate | What share of changes degrade the service |
| [CPT-0167](deployment-rework-rate.md) | Deployment rework rate | What share of the release stream went backwards |

**The grouping is DORA's own and it changed; this catalogue followed on 2026-08-03.** It previously
read as "two pairs" — 0155/0156 against 0157/0158 — which is a defensible way to think and is not the
published taxonomy. Three measures describe **throughput**, including recovery time (how fast the
stream resumes), and two describe **instability**. The argument the old framing carried survives and
is what matters: **either group alone can be improved by damaging the other**, so a dashboard shows
both or it misleads.

**Rework rate (CPT-0167) is the one the original four miss.** A team can post good numbers on all of
them and still spend its release stream going back over work that already shipped. It matters
particularly here: published research associates AI-assisted development with higher throughput and
worse stability, so a monitoring product for AI-assisted projects that measures only throughput will
report improvement while the thing it is meant to watch degrades.

### Flow

| ID | Concept | What it answers |
|---|---|---|
| [CPT-0159](littles-law.md) | Little's Law — WIP, throughput, cycle time | The identity that ties the three together |
| [CPT-0160](flow-efficiency.md) | Flow efficiency | How much of the elapsed time was actual work |

## How to extend

1. Allocate the next `CPT-NNNN` in [id-registry §1](../../00-governance/id-registry.md).
2. Copy [templates/concept.md](../../program/templates/concept.md) into this directory.
3. Add its row above.
4. A metric belongs here only if **a project's development actually produces the signal**. A metric
   that would need a field nobody emits is a wish, not a measurement.
5. Run `make verify`.

- **Governing refs:** [30-foundation/platform/rule.md](../../30-foundation/platform/rule.md) ·
  [ADR-0031/0034/0036](../../10-decisions/README.md).
