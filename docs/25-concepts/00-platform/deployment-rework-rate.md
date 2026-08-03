---
id: concept-deployment-rework-rate
title: "Deployment Rework Rate (CPT-0167)"
type: concept
owner: orchestrator
status: active
since: 2026-08-03
updated: 2026-08-03
relations:
  - { type: part-of, target: index-concepts-00-platform }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: concept-change-failure-rate }
---
# Deployment Rework Rate (CPT-0167)

> The share of deployments that were **unplanned, and happened to repair production**. The second
> instability measure alongside CPT-0157, and the one that catches what the other four miss: a team
> can post good numbers on all of them while spending its time cleaning up after itself.

## Formula

    rework_rate = unplanned_remediation_deployments(window) / deployments(window)

Same denominator and same window as CPT-0155 and CPT-0157, or the three cannot be read together.

| Symbol | Meaning | Unit |
|---|---|---|
| unplanned_remediation_deployments | deployments not on the plan, made to repair production | count |
| deployments | all deployments in the window | count |
| rework_rate | fraction, reported with both counts | fraction or % |

## Inputs and outputs

- **Inputs:** the deployment population, and per deployment two facts — was it planned, and was it
  made to repair production.
- **Output:** the fraction **with both counts** (see CPT-0157 for why the bare fraction misleads).
- **Not the same question as CPT-0157.** That asks *how many changes broke something*; this asks
  *how much of the release stream went back*. One failure repaired over six deployments gives a low
  CFR and a high rework rate.

## Assumptions and limits

- **"Unplanned" is the whole measurement and nothing external fixes it.** A deployment off the plan
  but foreseen as routine follow-up is a judgement call. Whatever rule a project adopts decides the
  numerator, so applying it inconsistently makes the trend an artefact of classification drift.
- **Gameable by planning the repair.** Add the hotfix to the plan and the numerator falls with
  nothing else changing. That is the mirror of CPT-0157's first trap, and it is why the two are read
  together rather than either alone.
- **Rising rework with rising throughput is the signal this measure exists for** — see the group
  index for why that combination matters to a monitoring product in particular.
- **Not effort.** A deployment count is not hours; for time spent read CPT-0160.

## Project-chosen inputs

| Input | Why the project must choose it |
|---|---|
| What makes a deployment "unplanned" | Follows from how the project plans releases. Nothing external fixes it, and it *is* the numerator. |
| What counts as repairing production | Follows from the same incident definition CPT-0157 uses — and it must be the same one, or the two rates describe different populations. |
| The window, and the deployment population | Must match CPT-0155 and CPT-0157 exactly. |
| The level that warrants action | The project's own, from its capacity to absorb rework. **Published bands are a survey population's distribution, not a target.** |

## Worked example

*Illustrative only.* A window records 40 deployments; 6 were unplanned repairs. Rework rate
**15% (6/40)**. If those six repaired **one** underlying failure, CFR is 2.5% (1/40) and rework rate
is 15% — the same week, and only the second number says where the time went.

## Governing rules

- **MSR-R1** — a ratio aggregates from pooled counts over one population and one window; the mean of
  four weekly rates is a different quantity.
- **SCM-R9** — deployment instants are ISO 8601 UTC, which is what makes a window well defined.

## Related

- CPT-0157 Change failure rate — the other instability measure; how many changes broke, not how much
  of the stream went backwards.
- CPT-0155 Deployment frequency — the shared denominator.
- CPT-0160 Flow efficiency — where the *time* went, which a deployment count cannot say.

## References

- DORA (Google Cloud) software delivery performance metrics — *deployment rework rate*, the fifth
  metric; grouping is three throughput and two instability. **Definitional authority only:** DORA is
  a research programme, not a standards body, and its performance bands are a surveyed population's
  distribution, so no band appears here.
- *State of DevOps* on AI-assisted development raising throughput while stability worsens — cited for
  the mechanism, not for a figure.
