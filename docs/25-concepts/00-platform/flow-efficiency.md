---
id: concept-flow-efficiency
title: "Flow Efficiency (CPT-0160)"
type: concept
owner: orchestrator
status: active
since: 2026-07-27
updated: 2026-07-27
relations:
  - { type: part-of, target: index-concepts-00-platform }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: concept-littles-law }
---
# Flow Efficiency (CPT-0160)

> What share of a change's elapsed time was **actual work** rather than waiting. It splits the
> duration that lead time (CPT-0156) reports as one number, and it usually shows that most of it was
> queue.

## Formula

    flow_efficiency = active_time / elapsed_time

    elapsed_time = active_time + wait_time      (an identity — nothing else is in it)

| Symbol | Meaning | Unit |
|---|---|---|
| active_time | time the item was genuinely being worked on | duration |
| wait_time | time the item was blocked, queued or waiting on someone | duration |
| elapsed_time | the item's full cycle time (CPT-0156) | duration |

The **decomposition is exact**: every moment is active or waiting, so the two must sum to the
elapsed time. If they do not, a state is unaccounted for — and that unaccounted state is nearly
always a queue.

## Inputs and outputs

- **Inputs:** per item, time spent in each workflow state, and each state classified active or waiting.
- **Output:** the ratio plus **where the wait time went**. The ratio identifies a problem; the
  breakdown by state identifies the queue to attack, which is the actionable part.
- **Report a distribution, not one average** — three weeks awaiting a decision and an hour awaiting CI
  are different phenomena.

## Assumptions and limits

- **The active/waiting classification is the whole measurement, and it is a judgement.** "In review"
  is waiting until the reviewer starts, and most tooling cannot tell the two apart. A generous
  classification flatters the ratio, so it must be written down and held stable.
- **Low flow efficiency is the normal finding, not an anomaly** — and it is good news, because wait
  time is usually far cheaper to remove than work time. A project that reads a low ratio as "the team
  is slow" has drawn the opposite conclusion from the one the number supports.
- **A high ratio is not automatically good.** Continuous work on every item implies people idle
  waiting for work — the mirror of the queue problem, and just as expensive.
- **Time in a state is not effort.** An item "in progress" overnight accumulates active time nobody
  spent; either exclude non-working hours or say the measure is calendar-based.
- **Does not apply when:** the workflow has no meaningful states — without state transitions there is
  nothing to classify, and the ratio degenerates to 1 by construction.

## Project-chosen inputs

| Input | Why the project must choose it |
|---|---|
| Which states count as active | The single choice that determines the ratio; write it down and keep it stable |
| Calendar time or working time | Overnight and weekends otherwise inflate active time |
| The unit of work | Must match CPT-0156, or the two cannot be read together |

## Worked example

*Illustrative.* One change: elapsed 12 days = active 1.5 days + waiting 10.5 days.

    flow_efficiency = 1.5 / 12 = 12.5%

The wait: 6 days awaiting review, 3 awaiting a deployment window, 1.5 awaiting a decision.
**Faster coding addresses 12.5% of the duration**; halving the review queue addresses more than twice
what perfect coding could. That reallocation of attention is the only reason to compute the ratio.

## Governing rules

- **SCM-R9** — state-transition instants are ISO 8601, UTC, which is what makes the durations
  additive at all. No rule fixes an acceptable flow efficiency.

## Related

- CPT-0156 Lead time for changes — the elapsed time this decomposes.
- CPT-0159 Little's Law — why the queue, not the work, sets cycle time.

## References

- Reinertsen, D., *The Principles of Product Development Flow* (2009) — queue cost and the dominance
  of wait time in development flow.
- Modig, N. & Åhlström, P., *This is Lean* (2012) — resource efficiency versus flow efficiency, and
  why optimising one damages the other.
