---
id: concept-bcp-readiness-score
title: "BCP Readiness Score (CPT-0080)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-08-03
relations:
  - { type: part-of, target: index-concepts-10-risk-management }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: concept-bcp-objectives-validation }
---
# BCP Readiness Score (CPT-0080)

> How exercise-ready the continuity plan is, judged on **drill evidence** rather than on the plan's
> existence: how recent the last exercise was, whether it met its RTO and RPO, and whether critical
> findings remain open.

## Definition

Readiness is a **composite over drill evidence**, and what this node fixes is which evidence is
admissible and how it combines — not the weights:

    readiness = Σᵢ wᵢ · cᵢ        with  Σᵢ wᵢ = 1  and  cᵢ ∈ [0, 100]

The four components a drill programme can evidence (ISO 22301 §8.5, §9): **recency** of the last
completed exercise, **RTO attainment** and **RPO attainment** across drills, and whether a
**critical finding** is open.

**Only the structure is fixed.** The weights, the recency bands and the rating cut-offs are the
project's, named below — a weighting copied from elsewhere imports its judgement about what
readiness means.

| Symbol | Meaning | Unit |
|---|---|---|
| days_since_last_drill | recency of last completed drill | days |
| rto_met_pct / rpo_met_pct | share of drills meeting RTO / RPO | 0–100 |
| open_critical_findings | unresolved CRITICAL drill findings | count |
| wᵢ | weight of component *i* | fraction, Σ = 1 |

## Project-chosen inputs

| Decision | Why the context cannot fix it |
|---|---|
| The four weights | A weighting expresses whether the organization fears staleness or unmet objectives more. ISO 22301 requires exercising; it sets no weights. |
| The recency bands | ISO 22301 §8.5 requires exercising **at planned intervals** and does not name one. A critical activity may warrant quarterly where an annual cycle suffices elsewhere. |
| The rating cut-offs over the score | A rating band is a management threshold, not a standard. |
| Whether the findings component is binary or graded | Both are defensible; the choice says whether a known gap invalidates the evidence or degrades it. |

## Inputs and outputs

- **Inputs:** validated ranges (percentages 0–100, counts ≥ 0).
- **Output:** `{score, rating, components}` — the component breakdown shows what to fix first,
  and is the part worth reporting: a single readiness number cannot distinguish an untested plan
  from a tested one with open findings.

## Assumptions and limits

- Attainment percentages need a denominator: with one drill, 100% RTO-met is weak evidence — report
  the drill count alongside, or the score overstates what was demonstrated.
- ISO 22301 §8.5 requires exercising at **planned intervals** and names none, which is why the
  recency bands are the project's.
- **Does not apply when:** no drill has ever run — score computes (RED) but is a
  statement about *evidence absence*, not plan quality.

## Worked example

Weights and bands **chosen for the illustration** (recency 30, RTO 35, RPO 25, findings 10; recency
full marks under 180 days): last drill 90 days ago → 30, RTO met 80% → 28, RPO met 60% → 15, one open
critical → 0, total **73**. Resolving the finding adds 10 — which is the reportable insight, and it
does not depend on the weights being these.

## Governing rules

- **RSK-R2** — residual risk cannot exceed inherent risk, so a readiness score can only claim what
  the drills actually demonstrated: an untested plan is *unproven*, not ready. This score reads
  drill outcomes; the process that produces them, and the bands over the score, are the project's.

## Related

- CPT-0079 RTO/RPO/MTPD validation — the objectives the drills test.

## References

- ISO 22301:2019 §8.5 — exercise programme; §9 — performance evaluation.
