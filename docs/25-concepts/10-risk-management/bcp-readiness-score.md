---
id: concept-bcp-readiness-score
title: "BCP Readiness Score (CPT-0080)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-10-risk-management }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: concept-bcp-objectives-validation }
---
# BCP Readiness Score (CPT-0080)

> How exercise-ready the continuity plan actually is, on drill evidence: recency of the
> last drill, RTO/RPO attainment rates, and open critical findings — 0–100 with a
> GREEN/AMBER/RED rating.

## Formula

    recency (30): <180 days → 30 · 180–365 → 15 · >365/never → 0
    rto (35):     rto_met_pct/100 × 35
    rpo (25):     rpo_met_pct/100 × 25
    findings (10): 10 if open_critical_findings = 0 else 0
    score = Σ · GREEN ≥ 75 · AMBER 50–74 · RED < 50

| Symbol | Meaning | Unit |
|---|---|---|
| days_since_last_drill | recency of last completed drill (9999 = never) | days |
| rto_met_pct / rpo_met_pct | share of drills meeting RTO / RPO | 0–100 |
| open_critical_findings | unresolved CRITICAL drill findings | count |

## Inputs and outputs

- **Inputs:** validated ranges (percentages 0–100, counts ≥ 0).
- **Output:** `{score, rating, components}` — the component breakdown shows what to
  fix first. The TS `openCriticalFindings` selector supplies the findings input from
  the drill aggregate.

## Assumptions and limits

- The findings component is **binary** — one open critical zeroes all 10 points; there
  is no partial credit, by design (a known critical gap invalidates the plan's
  evidence).
- Attainment percentages need a denominator: with 1 drill, 100% RTO-met is weak
  evidence; report drill count alongside.
- Recency bands align with the ISO 22301 practice of at-least-annual exercising; more
  critical activities may warrant quarterly (tighten bands per plan criticality).
- **Does not apply when:** no drill has ever run — score computes (RED) but is a
  statement about *evidence absence*, not plan quality.

## Worked example

Last drill 90 days ago (30), RTO met 80% (28), RPO met 60% (15), 1 open critical (0)
→ **73 = AMBER** — resolve the finding (+10) to reach GREEN before the next audit.

## Governing rules

- **RSK-R*** — drill lifecycle (plan→start→complete/fail, findings resolve) is
  state-machine law; this score only reads its outcomes.

## Related

- CPT-0079 RTO/RPO/MTPD validation — the objectives the drills test.

## References

- ISO 22301:2019 §8.5 — exercise programme; §9 — performance evaluation.
