---
id: concept-failed-deployment-recovery-time
title: "Failed-Deployment Recovery Time (CPT-0158)"
type: concept
owner: orchestrator
status: active
since: 2026-07-27
updated: 2026-07-27
relations:
  - { type: part-of, target: index-concepts-00-platform }
  - { type: governed-by, target: index-adr }
---
# Failed-Deployment Recovery Time (CPT-0158)

> How long service degradation caused by a change lasts, from detection to restoration. The second
> **stability** measure: change failure rate (CPT-0157) counts how often, this says how much it cost.

## Formula

    recovery_time(failure) = restored_instant − detected_instant

    reported as a distribution:  p50, p85, worst   (not a mean)

| Symbol | Meaning | Unit |
|---|---|---|
| detected_instant | when the degradation was detected — **not** when it began | ISO 8601 instant |
| restored_instant | when service returned to its normal level | ISO 8601 instant |
| p50 / p85 / worst | percentiles and the maximum over the window | duration |

## Inputs and outputs

- **Inputs:** per failure (the CPT-0157 numerator), the detection and restoration instants.
- **Output:** the distribution **and the count of failures behind it**. With few failures every
  percentile is a single incident, so the honest report is the list, not a statistic.
- **The worst case belongs in the report.** For a recovery measure the tail *is* the risk: a p50 of
  ten minutes alongside a worst case of nine hours describes a real exposure that the median hides.

## Assumptions and limits

- **Detection is not onset.** The clock starts when something noticed, so a project that detects
  slowly reports *short* recoveries — the undetected interval is invisible here and is often the
  larger part of user impact. Without a separate time-to-detect, an improvement here can be a
  monitoring regression.
- **"Restored" needs a definition.** Mitigated behind a flag, rolled back, or actually fixed are
  three different states. Rollback is usually the fastest and leaves the defect present, so a metric
  that treats rollback as restoration measures **reaction speed, not resolution**.
- **Gameable by reclassification.** An incident downgraded to "degraded, not failed" leaves both this
  metric and CPT-0157 — the two moving together is the tell.
- **Small numbers, heavy tails.** These are the most skewed of the four measures; averaging them
  across a quarter is close to meaningless.
- **Does not apply when:** the failure never reached users (caught in a canary and reverted before
  exposure) — worth recording, but as a pipeline event rather than a service recovery.

## Project-chosen inputs

| Input | Why the project must choose it |
|---|---|
| What "restored" means | Mitigated, rolled back, or fixed forward — each answers a different question |
| Whether time-to-detect is measured separately | Without it, slow detection reads as fast recovery |
| Which severities are in scope | Mixing a total outage with a degraded background job makes the distribution unreadable |
| Manual or automated timestamps | Human-entered instants are rounded and optimistic; both are usable, but not interchangeably |

## Worked example

*Illustrative.* Eight failures in a quarter: `6 min, 9 min, 14 min, 22 min, 25 min, 40 min, 3 h,
9 h`.

p50 = 23 minutes; mean = 1.7 hours; worst = 9 hours — three summaries, three stories, and the eight
raw values more informative than any of them. The two long ones are what a project would investigate,
and an average would have buried them.

## Governing rules

- **SCM-R9** — both instants are ISO 8601, UTC; a duration computed across mixed local times during
  an incident is exactly when clock confusion happens.
- **RSK-R6** applies by analogy: **expectation is not exposure.** A mean recovery time is not the
  recovery a project should plan for, in the same way an expected annual loss is not the loss to
  plan against.

## Related

- CPT-0157 Change failure rate — the population this measures.
- CPT-0079 RTO/RPO validation — the business-continuity analogue: an objective is not met until it
  has been demonstrated.

## References

- Forsgren, Humble & Kim, *Accelerate* (2018) — the four key measures, of which this is the fourth.
- DORA / Google Cloud *State of DevOps* — cited for the definition; its bands are survey findings.
