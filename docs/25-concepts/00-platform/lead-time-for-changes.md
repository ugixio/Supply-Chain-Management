---
id: concept-lead-time-for-changes
title: "Lead Time for Changes (CPT-0156)"
type: concept
owner: orchestrator
status: active
since: 2026-07-27
updated: 2026-07-27
relations:
  - { type: part-of, target: index-concepts-00-platform }
  - { type: governed-by, target: index-adr }
---
# Lead Time for Changes (CPT-0156)

> How long a change takes to reach production, measured per change. The **latency** half of
> throughput: deployment frequency (CPT-0155) says how often the pipe fires, this says how long the
> pipe is.

## Formula

    lead_time(change) = production_instant − start_instant

    reported as a distribution:  p50, p85, p95   (not a mean)

| Symbol | Meaning | Unit |
|---|---|---|
| start_instant | when the clock starts — **the project's definition**, see below | ISO 8601 instant |
| production_instant | when the change is live in production | ISO 8601 instant |
| p50 / p85 / p95 | percentiles of the distribution over the window | duration |

## Inputs and outputs

- **Inputs:** per change, the two instants (UTC — SCM-R9), and the deployment it rode in.
- **Output:** percentiles plus the sample size. **A mean is the wrong summary here**: lead-time
  distributions are strongly right-skewed, so one change blocked for three weeks moves the mean and
  tells you nothing about the typical change. The median and an upper percentile do.
- Never report a percentile without `n`. A p95 over eleven changes is the second-slowest one.

## Assumptions and limits

- **Where the clock starts decides what the metric means**, and there is no single right answer:
  - **first commit** — measures engineering flow, and shortens if work is branched later;
  - **work started** (ticket moved to in-progress) — includes analysis, and depends on board hygiene;
  - **request raised** — the only one a stakeholder recognizes, and the one nobody's tooling emits.
  The narrower the definition, the better the number looks. State it.
- **Gameable by definition drift.** Moving the start later, or excluding "hotfixes", improves the
  metric without changing delivery. This is why the definition must be fixed and versioned before a
  series is trusted.
- **Queue time dominates in practice.** Most of a long lead time is waiting, not working, which is
  what flow efficiency (CPT-0160) separates out — optimizing the working part of a mostly-queued
  change is effort in the wrong place.
- **Abandoned changes have no lead time**, and dropping them silently biases the metric downward:
  the changes that were hardest to finish are exactly the ones most likely to be abandoned.
- **Does not apply when:** comparing across projects with different start definitions — the numbers
  are not the same measurement.

## Project-chosen inputs

| Input | Why the project must choose it |
|---|---|
| The start event | Commit, work-started or request-raised — each is a different question |
| Which percentiles are reported | p50 for the typical change, an upper percentile for the promise a team can keep |
| How hotfixes and reverts are treated | Included, excluded, or reported separately — excluding them flatters the number |
| Working time or calendar time | Calendar time is what a stakeholder experiences; working time is what a team controls |

## Worked example

*Illustrative.* Over 30 changes: p50 = 4 h, p85 = 3 d, p95 = 11 d; mean = 1.6 d.

The mean sits between p50 and p85 and describes no actual change. The shape is the finding: half of
the work flows through in an afternoon, while a tail waits days — and a tail that long is a queue,
not slow coding (CPT-0160).

## Governing rules

- **SCM-R9** — both instants are ISO 8601, UTC. **DMD-R9**-style discipline applies by analogy: a
  duration is stated with the window and definition it was measured under, or it is not comparable.
  No rule fixes an acceptable lead time.

## Related

- CPT-0155 Deployment frequency — the other throughput half.
- CPT-0159 Little's Law — lead time is the `W` term.
- CPT-0160 Flow efficiency — splits this duration into work and wait.

## References

- Forsgren, Humble & Kim, *Accelerate* (2018) — definition of lead time for changes.
- Reinertsen, D., *The Principles of Product Development Flow* (2009) — why queues dominate
  end-to-end duration.
