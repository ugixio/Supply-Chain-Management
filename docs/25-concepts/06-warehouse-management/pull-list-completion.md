---
id: concept-pull-list-completion
title: "Pull-List Completion (CPT-0165)"
type: concept
owner: orchestrator
status: active
since: 2026-08-01
updated: 2026-08-02
relations:
  - { type: part-of, target: index-concepts-06-warehouse-management }
  - { type: governed-by, target: index-adr }
---
# Pull-List Completion (CPT-0165)

> How many material call-offs the warehouse fulfilled, and how completely. A **flow** on the count
> and a **ratio** on the fill — and the count alone is the one that flatters an operation.

## Formula

    lists_processed(period) = call-off lists closed in the period      (a flow)
    line_fill              = lines fulfilled / lines requested × 100   (per list, or pooled)

| Symbol | Meaning | Unit |
|---|---|---|
| lists_processed | call-off lists closed in the period | count/period |
| lines requested | lines the list asked for | count |
| lines fulfilled | lines delivered complete to the point of use | count |
| line_fill | output | percentage |

## Inputs and outputs

- **Inputs:** the lists closed in the period, and per list its requested and fulfilled lines.
- **Outputs:** the list count and the fill percentage. **Report both.** A list closed short is still
  a closed list, so the count rises while the consuming process starves — the failure this pairing
  exists to expose.

## Assumptions and limits

- **Vocabulary warning, stated plainly.** A *pull list* is the operational name for a material
  call-off in a pull system — demand signalled by consumption, as the APICS Dictionary defines
  *pull system*. **No standards body fixes what one list contains**, so list counts are not
  comparable between operations, or across a change in how lists are cut. Publish the definition
  with the number.
- **The list count is a work-batching artefact, not a workload.** Splitting the same demand into
  twice as many lists doubles this indicator without moving one extra part. Compare line counts
  across periods; use the list count only for queue reasoning.
- **"Fulfilled" means complete to the point of use.** Staged at the dock is not fulfilled if the line
  cannot consume it. Where the boundary sits decides the number.
- **Pool the lines rather than averaging per-list percentages (MSR-R1).**
- **Does not apply as an outbound customer service level** — that is fill rate on a different
  population, and mixing them hides which side is short.

## Project-chosen inputs

| Input | Why the project must choose it |
|---|---|
| What one list contains, and how lists are cut | Follows from the consuming process's cadence and the material handling equipment. This definition carries the whole indicator, and nothing external supplies it. |
| Where "fulfilled" is recorded | Follows from where responsibility transfers to the consuming process. |
| Pooled lines or per-list mean | Follows from the question: pooled measures material, per-list measures list discipline. |
| The fill level that triggers escalation | Follows from the buffer the consuming process holds, which is the real protection. |

## Worked example

*Illustrative only.* A shift closes 48 lists covering 402 lines, of which 388 were fulfilled.
Pooled fill **96.5%**; lists processed **48 per shift**. If the same demand had been cut into 96
smaller lists, the count would read 96 — twice as busy, identical material moved.

## Governing rules

- **MSR-R1** — the fill ratio aggregates from pooled lines, not from a mean of per-list percentages.
- **WHS-R5** — a list cannot report more fulfilled than it requested; the conservation is what makes
  fill auditable rather than self-reported.
- **SCM-R10** — requested and fulfilled quantities carry their GS1 units, or the ratio compares
  unlike things.
- **SCM-R4** — the material movement the list triggers has its accounting consequence.

## Related

- CPT-0164 Sequence readiness — sequences are commonly built from these call-offs.
- CPT-0163 Outbound shipment backlog — the level arithmetic, if pending lists are also tracked.
- CPT-0045 Labour productivity — the rate view of the same work.

## References

- APICS/ASCM Supply Chain Dictionary, 16th Ed. (2024) — *pull system*, *call-off*, *kanban*.
  Terminology authority; the content of a pull list is not standardized.
- Ohno, T., *Toyota Production System* (1988) — consumption-signalled replenishment.
