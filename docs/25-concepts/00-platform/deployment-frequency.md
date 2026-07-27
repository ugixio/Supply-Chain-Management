---
id: concept-deployment-frequency
title: "Deployment Frequency (CPT-0155)"
type: concept
owner: orchestrator
status: active
since: 2026-07-27
updated: 2026-07-27
relations:
  - { type: part-of, target: index-concepts-00-platform }
  - { type: governed-by, target: index-adr }
---
# Deployment Frequency (CPT-0155)

> How often a project gets change into production. A **throughput** measure: it says nothing about
> whether the change was any good, which is why it is never read without its stability pair
> (CPT-0157/0158).

## Formula

    frequency = deployments_to_production(window) / window_length

A **rate**, so it needs its window stated. Reporting it as a bare count ("14 deployments") is not a
frequency — 14 in a week and 14 in a quarter describe different projects.

| Symbol | Meaning | Unit |
|---|---|---|
| deployments_to_production | successful deployments reaching the production environment | count |
| window_length | the observation period | days or weeks |

## Inputs and outputs

- **Inputs:** one event per deployment, each carrying its target environment and completion instant
  (ISO 8601, UTC — SCM-R9).
- **Output:** the rate and the window it was measured over.
- **Report the count alongside the rate.** A rate derived from two deployments is arithmetic, not
  evidence, and only the count shows that.
- **Distribution over average.** Deployments cluster (a release day, a freeze, a burst after an
  incident). A mean per week hides a project that ships everything on Thursdays, which is exactly
  the pattern the metric exists to surface.

## Assumptions and limits

- **Directly gameable by splitting.** One change released as five deployments quintuples this
  metric and improves nothing. It is only meaningful against a **stable definition of what a
  deployment is**, held constant over time — a project that redefines it has broken its own series.
- **A deployment is not a release.** Where code ships dark behind a flag, this counts the
  deployment; the change reaching users is a different event, and conflating the two overstates
  delivery.
- **Failed and rolled-back deployments.** Counting attempts measures activity; counting successes
  measures delivery. Either is defensible, but a project that counts attempts here while counting
  only failures in CPT-0157 has two inconsistent denominators.
- **Does not apply when:** the project has no production environment yet — the metric has no
  referent, and reporting zero reads as failure rather than as "not applicable".

## Project-chosen inputs

| Input | Why the project must choose it |
|---|---|
| What counts as a deployment | The definition *is* the metric; a per-service, per-monorepo and per-artefact count differ by an order of magnitude |
| Which environments count as production | Multi-region or multi-tenant rollouts can be one deployment or many |
| The window and the aggregation | A rate needs a period; the distribution matters more than the mean |
| Whether attempts or successes are counted | Must agree with the change-failure-rate denominator |

## Worked example

*Illustrative.* A project records 26 production deployments over 4 weeks → **6.5 per week**.

Split by day, 19 of the 26 fall on two days. The mean says "more than daily"; the distribution says
"twice a week, in batches". The batching is the finding — it usually means an approval step or a
manual gate that the average conceals.

## Governing rules

- **SCM-R9** — deployment instants are ISO 8601, UTC: a frequency computed across mixed local times
  is undefined. No rule fixes a deployment rate; any band over it is a project's own goal.

## Related

- CPT-0156 Lead time for changes — the other half of throughput.
- CPT-0157 Change failure rate · CPT-0158 recovery time — the stability pair that keeps this honest.
- CPT-0159 Little's Law — frequency is the throughput term in the identity.

## References

- Forsgren, Humble & Kim, *Accelerate* (2018) — the four key delivery measures and their derivation.
- DORA / Google Cloud *State of DevOps* reports — the annual survey these measures come from. Cited
  for the **definitions**; its performance bands are survey findings, not requirements.
