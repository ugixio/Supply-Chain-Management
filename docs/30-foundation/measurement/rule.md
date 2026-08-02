---
id: rule-measurement
title: "Rules — Measurement Identities (MSR-R*)"
type: rule
owner: orchestrator
status: active
since: 2026-08-02
updated: 2026-08-02
relations:
  - { type: part-of, target: index-foundation }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: rule-scm-core }
---
# Rules — Measurement Identities

> **What belongs here.** Arithmetic that constrains *how a measure may be computed and aggregated*,
> independent of what it measures. These are identities, not conventions: they hold for every
> department, so a node states them once by citation instead of re-deriving them.
>
> **What does not.** Any level, target or tolerance — that is policy (ADR-0037). And the *meaning* of
> a measure, which belongs to its concept node.
>
> **Why a separate axis** (ADR-0039). These identities were being restated per department —
> **QMS-R7** fixes the opportunity base for defect rates, **RSK-R5** keeps an ordinal score ordinal,
> **PRC-R4 · SPL-R5 · WHS-R5 · ORD-R5** each state a conservation for their own process. Each is
> correct and each is a special case of something general. A cross-cutting home lets the next one be
> cited rather than re-written, which is the whole point.

## Invariants (arithmetic — NEVER violated)

- **MSR-R1:** A ratio is aggregated **from its components, never by averaging ratios**. Over any
  group, `ratio = Σnumerator ÷ Σdenominator`; the mean of the per-part ratios is a different
  quantity and equals it only when every denominator is identical. Three periods of 2/100, 3/10 and
  1/90 give **6/200 = 3.0 %**, while their mean is 11.0 %. Two corollaries follow and are part of the
  rule: **(a)** numerator and denominator must cover the **same population and the same period**, or
  the ratio compares two different things; **(b)** an unweighted mean of per-item ratios weights a
  one-line item equally with a fifty-line one, so where it is used it is **declared** as an
  unweighted mean. *Source:* arithmetic — `Σaᵢ/Σbᵢ ≠ (1/n)Σ(aᵢ/bᵢ)` unless all `bᵢ` are equal.
  *Design consequence:* a system that stores only the computed ratio **cannot** satisfy this rule
  afterwards; the components must be captured.

- **MSR-R2:** A measure is a **flow** or a **level**, and the distinction fixes which aggregations
  are valid. A **flow** counts events over an interval and **sums** across adjacent intervals. A
  **level** is read at an instant; over an interval its valid aggregations are **last, maximum,
  minimum or time-weighted average — never the sum**, and never the count of readings. Summing a
  level fabricates a quantity that never existed: a backlog of 40 read six times in an hour is 40,
  not 240. A simple mean of readings equals the time-weighted average **only when the reading
  intervals are equal**. *Source:* arithmetic — a level has no time dimension to accumulate over.
  *Design consequence:* the flow/level classification is **data**, declared per measure, not a
  convention the author of each report is trusted to remember.

## How these are cited

A concept node names the rule and stops — it does not restate the arithmetic:

```
## Governing rules
- **MSR-R2** — a level; valid aggregations are last, max, min or time-weighted average.
```

The catalogue index for a department that publishes levels or ratios points at this file once, rather
than every node carrying a paragraph. Before this axis existed the flow/level argument was written out
in three warehouse nodes, which is what a missing citation target looks like.

## Related rules elsewhere (special cases, kept where they are)

These stay in their department families — they carry domain detail this axis deliberately does not:

| Rule | What it fixes |
|---|---|
| **QMS-R7** | A defect rate is stated with its opportunity base — the denominator discipline of MSR-R1, for defects |
| **RSK-R5** | A score built from ordinal scales stays ordinal |
| **PRC-R4** | Inspection conserves what arrived |
| **SPL-R5** | Netting conserves |
| **WHS-R5** | A task cannot report more completed than it was given |
| **ORD-R5** | Allocation conserves |
| **SCM-R14** | Apportionment of money sums exactly to the total; ties to even |

## References

- Arithmetic identities; no external body is required to fix them, and none could change them.
- ADR-0039 — why this axis exists and what it may hold.
