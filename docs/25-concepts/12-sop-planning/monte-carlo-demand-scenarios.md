---
id: concept-monte-carlo-demand-scenarios
title: "Monte Carlo Demand Scenarios (CPT-0152)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-12-sop-planning }
  - { type: governed-by, target: index-adr }
---
# Monte Carlo Demand Scenarios (CPT-0152)

> Fan-chart demand scenarios for S&OP: simulate noisy futures around the base
> forecast and hand the meeting P10/P50/P90 vectors as pessimistic / base /
> optimistic plans.

## Formula

    demand_t ~ Normal(base_t, base_t × cv)     clipped at 0
    P10/P50/P90 = per-period percentiles over n_scenarios draws (default 1000,
    seed 42)

| Symbol | Meaning | Unit |
|---|---|---|
| base_t | base forecast per period | units |
| cv | demand coefficient of variation (0.20 = 20%) | fraction |

## Inputs and outputs

- **Inputs:** base vector, cv ≥ 0, scenario count ≥ 1 (validated); fixed seed for
  reproducible planning cycles.
- **Output:** `{P10, P50, P90}` vectors across the horizon.

## Assumptions and limits

- **Independent periods:** no autocorrelation — real demand runs hot/cold in
  streaks, so *cumulative* quantities (e.g. quarter totals) are more variable
  than these bands suggest; the per-period fan is honest, the cumulative read is
  optimistic.
- σ proportional to level (constant CV) — reasonable mid-volume; small-volume
  periods with clipping at zero skew P50 slightly above base × 1 when cv is
  large.
- Normal noise; use the XYZ class (CPT-0018/0115) to set cv per segment rather
  than one global number.
- P10/P90 are *demand* percentiles — running supply plans against P90 demand is
  a capacity-options conversation (upside flexibility, CPT-0092), not a stocking
  rule; safety stock math stays with CPT-0012.
- **Does not apply when:** scenario drivers are discrete events (win/lose a
  tender) — model those as explicit scenarios, not noise.

## Worked example

Base [1000, 1100, 1200], cv 0.2 → P10 ≈ [744, 818, 892], P90 ≈ [1256, 1382,
1508] — the supply review pre-books overtime options against P90's Q3.

## Governing rules

- **SOP-R4** — scenarios inform the one plan; they do not become a second one. Only the committed
  scenario is the plan (SOP-R5), and the rest are evidence for how it was chosen.

## Related

- CPT-0092 SCOR agility — the supply response to the P90 branch.
- CPT-0077 Monte Carlo VaR — the same machinery on losses.

## References

- Wallace (2004) — scenario S&OP; Hyndman & Athanasopoulos, *FPP3* — prediction
  intervals as fan charts.
