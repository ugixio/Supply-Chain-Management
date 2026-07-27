---
id: concept-bcp-objectives-validation
title: "BCP Objectives Validation — RTO/RPO/MTPD (CPT-0079)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-10-risk-management }
  - { type: governed-by, target: index-adr }
---
# BCP Objectives Validation — RTO/RPO/MTPD (CPT-0079)

> The consistency check on a Business Continuity Plan's three clocks: you must recover
> (RTO) before tolerance runs out (MTPD), and your data-loss window (RPO) must be
> achievable within the recovery itself.

## Formula

    valid ⇔ RTO ≤ MTPD ∧ RPO ≤ RTO ∧ all > 0

| Symbol | Meaning | Unit |
|---|---|---|
| RTO | Recovery Time Objective — time to restore the activity | hours |
| RPO | Recovery Point Objective — max tolerable data/state loss | hours |
| MTPD | Maximum Tolerable Period of Disruption | hours |

## Inputs and outputs

- **Input:** `BCPObjectives(rto_hours, rpo_hours, mtpd_hours)`.
- **Output:** list of human-readable violation messages; empty = valid. Each violation
  explains its consequence ("recovery will not complete before maximum tolerable
  disruption").

## Assumptions and limits

- `RPO ≤ RTO` is a practical supply-chain reading (state recovery must fit inside the
  recovery window); ISO 22301 defines both against the disruption, and organizations
  with continuous replication can legitimately run RPO ≪ RTO — the rule flags the
  incoherent opposite.
- Hours-granularity: sub-hour objectives (payment systems) need finer units upstream.
- Validation is static: whether the *drills* actually meet RTO/RPO is CPT-0080's
  evidence question.
- **Does not apply when:** an activity has no data/state dimension — RPO is then
  vacuous (enter RPO = RTO).

## Worked example

RTO 24h, RPO 4h, MTPD 72h → valid (24 ≤ 72, 4 ≤ 24).
RTO 96h, MTPD 72h → violation: recovery exceeds tolerance — re-engineer the recovery
strategy or renegotiate the MTPD with the business.

## Project-chosen inputs

| Input | Why the project must choose it |
|---|---|
| The recovery objectives themselves | RTO, RPO and MTPD are business decisions about tolerable loss |
| What counts as validation | A tabletop walkthrough and a full failover are not the same evidence |
| The validation cadence | An objective validated once is an objective validated for one configuration |

## Governing rules

- **RSK-R2** — residual risk cannot exceed inherent risk: a recovery objective claimed but never
  validated does not reduce anything. Whether a plan may activate unvalidated is the project's.

## Related

- CPT-0080 BCP readiness score — drill evidence against these objectives.

## References

- ISO 22301:2019 §8.3 — business continuity strategies and solutions; BIA (§8.2).
