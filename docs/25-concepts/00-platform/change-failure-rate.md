---
id: concept-change-failure-rate
title: "Change Failure Rate (CPT-0157)"
type: concept
owner: orchestrator
status: active
since: 2026-07-27
updated: 2026-07-27
relations:
  - { type: part-of, target: index-concepts-00-platform }
  - { type: governed-by, target: index-adr }
---
# Change Failure Rate (CPT-0157)

> The share of changes reaching production that degrade the service and require remediation — a
> hotfix, a rollback, a patch forward. The **stability** counterweight to deployment frequency
> (CPT-0155): raising throughput while this rises is not an improvement.

## Formula

    CFR = failed_changes(window) / changes_to_production(window)

The denominator **must be the same population** counted by CPT-0155 over the same window. A rate
whose numerator and denominator come from different definitions is not a rate.

| Symbol | Meaning | Unit |
|---|---|---|
| failed_changes | changes that degraded service and needed remediation | count |
| changes_to_production | all changes reaching production in the window | count |
| CFR | fraction, reported with both counts | fraction or % |

## Inputs and outputs

- **Inputs:** the deployment population, and per deployment whether it was followed by remediation
  attributable to it.
- **Output:** the fraction **and both counts**. `1/8` and `50/400` are both 12.5% and are not
  equally informative — the first is one bad afternoon.
- **Attribution is a judgement, not a lookup.** A degradation surfacing hours later, after three
  deployments, has no mechanical owner. Whatever rule a project uses, it decides the numerator, so it
  must be applied consistently.

## Assumptions and limits

- **Gameable in three directions, all of which look like improvement:**
  1. **Stop calling things failures** — narrow "degradation" until few incidents qualify.
  2. **Inflate the denominator** — split changes into more deployments (CPT-0155) and the same
     number of failures becomes a smaller share.
  3. **Delay production** — a change held back cannot fail in production.
  A falling CFR alongside a falling deployment frequency is usually the third.
- **A zero rate is not evidence of quality.** Over a small window it is the expected outcome of
  shipping little, and it is indistinguishable from a project that has stopped reporting failures.
- **This measures changes, not availability.** An outage from a dependency, an expired certificate
  or traffic is a real incident and not a change failure; counting all incidents here leaves the
  metric unable to say anything about change quality.
- **Does not apply when:** the remediation *is* the normal path — an environment where every
  deployment is followed by tuning has no meaningful failure/success split.

## Project-chosen inputs

| Input | Why the project must choose it |
|---|---|
| What counts as a degradation | Any user-visible error, a threshold breach, or a declared incident — this single choice can move the metric several-fold |
| The attribution rule | Which deployment a degradation is charged to when several are candidates |
| The window | Long enough that the denominator is not a handful of changes |
| Whether reverts count as failures | A revert is remediation; a *planned* revert of an experiment is not a failure |

## Worked example

*Illustrative.* 400 changes, 18 followed by remediation → **CFR = 4.5%**.

Now suppose the same work had shipped as 80 larger deployments with the same 18 remediations: the
rate becomes **22.5%**. Nothing about the software changed. Batch size alone moved the metric by a
factor of five — which is why this number is only interpretable next to deployment frequency and a
fixed definition of a change.

## Governing rules

- **SCM-R9** — deployment and remediation instants are ISO 8601, UTC, which is what makes
  attribution over a time window possible at all.
- **QMS-R7** applies by analogy: a defect rate is stated **with its opportunity base**. A change
  failure rate without its denominator definition is the same error QMS-R7 names for PPM and DPMO.

## Related

- CPT-0155 Deployment frequency — the shared denominator, and the batch-size trap above.
- CPT-0158 Failed-deployment recovery time — how bad the failures were, not how many.

## References

- Forsgren, Humble & Kim, *Accelerate* (2018) — definition of change failure rate.
- DORA / Google Cloud *State of DevOps* — cited for the definition; its bands are survey findings.
