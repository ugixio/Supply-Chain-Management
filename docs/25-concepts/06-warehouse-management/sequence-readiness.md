---
id: concept-sequence-readiness
title: "Sequence Readiness — Prepared and Pending (CPT-0164)"
type: concept
owner: orchestrator
status: active
since: 2026-08-01
updated: 2026-08-02
relations:
  - { type: part-of, target: index-concepts-06-warehouse-management }
  - { type: governed-by, target: index-adr }
  - { type: traces-to, target: concept-outbound-shipment-backlog }
---
# Sequence Readiness — Prepared and Pending (CPT-0164)

> Of the sequences a consuming line needs, how many are built and how many are still owed. One
> **flow** and one **level**, deliberately defined together because either alone misleads.

## Formula

    prepared(period) = sequences completed in the period          (a flow — sums over time)
    pending(instant) = sequences required but not yet complete    (a level — never sums)
    readiness        = prepared / required × 100                  (over one defined horizon)

| Symbol | Meaning | Unit |
|---|---|---|
| prepared | sequences finished in the period | count/period |
| pending | sequences outstanding at the reading instant | count |
| required | sequences the horizon calls for | count |
| readiness | share of the horizon that is built | percentage |

## Inputs and outputs

- **Inputs:** the sequence requirement for a stated horizon (a shift, a build window, a call-off
  schedule), and the completion state of each.
- **Outputs:** the prepared count for the period, the pending level at an instant, and the ratio over
  the horizon. **All three carry either their period or their instant** — a prepared count without a
  period and a pending level without an instant are both unreadable.

## Assumptions and limits

- **Vocabulary warning.** *Sequence* is industry vocabulary for just-in-sequence supply, defined in
  the APICS Dictionary. **No standards body fixes what one sequence contains**, so another plant's
  counts are not comparable. Record the definition next to the number.
- **`prepared + pending = required` holds only for a frozen horizon** — requirements arrive during
  the shift.
- **Sequence integrity is binary and it dominates the count.** Right parts in the wrong order is not
  partially prepared — the line cannot use it. Counting it as progress is how this indicator
  flatters an operation.
- **The pending count is a level (MSR-R2)**; the prepared count is a flow. Reporting them the same
  way is the error this pairing exists to prevent.
- **Does not apply where supply is not sequenced.** Bulk or kitted supply has no sequence; use
  CPT-0040 instead.

## Project-chosen inputs

| Input | Why the project must choose it |
|---|---|
| What one sequence contains, and its boundary | The consuming line's takt and layout decide it. This is the definition the whole indicator rests on, and nothing external supplies it. |
| The horizon: shift, build window, call-off | Follows from the agreement with the consuming line. |
| Whether a re-sequenced unit counts as newly prepared | Follows from how rework is accounted; counting it twice inflates the flow. |
| The readiness level that triggers escalation | Follows from the line's own buffer, which is the real protection. |

## Worked example

*Illustrative only.* A shift requires 120 sequences; 96 complete, 24 outstanding at 14:00. Readiness
**80%**, prepared **96 per shift**, pending **24 at 14:00**. If two of the 96 are mis-ordered they
are not prepared: readiness **78.3%**, and the line stops either way.

## Governing rules

- **MSR-R2** — `prepared` is a flow and sums; `pending` is a level and does not.
- **WHS-R5** — what a task reports completed cannot exceed what it was given; a prepared count is
  only auditable under that conservation.
- **SCM-R9** — the instant on the pending level and the boundaries of the period are ISO 8601 UTC.
- **SCM-R10** — component quantities within a sequence carry their GS1 units.

## Related

- CPT-0163 Outbound shipment backlog — the same level arithmetic, and why sums are invalid.
- CPT-0165 Pull-list completion — the call-off that usually feeds sequence preparation.
- CPT-0040 Wave optimization — batching when supply is not sequenced.

## References

- APICS/ASCM Supply Chain Dictionary, 16th Ed. (2024) — *just-in-sequence*, *sequencing*,
  *call-off*. Terminology authority; the content of a sequence is not standardized.
- Little, J. D. C. (1961) — the pending level as work in process (via CPT-0159).
