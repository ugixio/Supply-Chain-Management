---
id: concept-algorithm-selection
title: "Forecast Algorithm Selection (CPT-0011)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-20
relations:
  - { type: part-of, target: index-concepts-demand-planning }
  - { type: governed-by, target: index-adr }
  - { type: traces-to, target: concept-forecast-accuracy-metrics }
---
# Forecast Algorithm Selection (CPT-0011)

> Choosing among SMA, SES, Holt and Holt-Winters. The repo does this **two different
> ways**, and the two are not interchangeable.

## The two strategies

### (a) Rule-based dispatch

Selection from declared series characteristics; returns only the **name** of an algorithm. Cheap,
transparent, and reproducible.

| Condition (evaluated in order) | Result |
|---|---|
| `hasSeasonality` **and** `seasonalPeriod` **and** `data.length ≥ 2m` | `HOLT_WINTERS` |
| `hasTrend` | `HOLTS` |
| `data.length ≥ 3` | `SES` |
| otherwise | `SMA` |

Trend and seasonality are **caller-supplied booleans** — nothing is inferred from the
series. Garbage flags in, wrong algorithm out.

### (b) Empirical backtest

Selection by measured holdout accuracy; returns a **fitted forecast**, not just a name.

1. Split the series into train and holdout — the split fraction is project-chosen.
2. Fit each candidate on train. Holt-Winters is only a candidate where the train segment covers at
   least two full seasons.
3. Score each on the holdout; pick the best by the chosen error measure.
4. Re-fit the winner on the **full** series and forecast from that.
5. Define what happens if every candidate fails — a fallback, or a refusal.

## Assumptions and limits

- **The two strategies have different contracts and are not substitutes.** (a) takes declared
  flags and returns a name; (b) takes the series and returns a fitted forecast. A caller written
  for one cannot consume the other, and calling the choice "algorithm selection" in both cases
  hides that.
- **Smoothing parameters left at fixed defaults make the comparison unfair.** Each candidate is
  then judged at whatever α/β/γ it happened to be given, so (b) selects the algorithm best suited
  to those defaults rather than the algorithm best suited to the series. Either optimise the
  parameters per candidate or state that the ranking is conditional on the defaults used.
- Selecting on **MAPE** inherits every MAPE weakness (CPT-0008): it is asymmetric and
  drops zero actuals, so on intermittent demand this selector is biased toward whichever
  candidate happens to over-forecast least on non-zero periods. Croston (CPT-0006) is not
  a candidate at all.
- **A candidate that fails must not fail silently.** Swallowing an error per candidate turns a
  broken implementation into a candidate that simply never wins, and the selector still returns a
  confident answer.
- **A percentage holdout on a short series can be a single period** — a selection made on one
  observation, which is indistinguishable from chance. Set a minimum holdout length in periods,
  not only a fraction.

## Worked example

24 monthly observations, `season_length = 12`, holdout 20%:

- holdout = max(1, ⌊24 × 0.2⌋) = **4**; train = 20 periods.
- Under **(b)** Holt-Winters is not a candidate: the *train* segment holds 20 periods and
  `20 < 2 × 12`. Candidates are SMA, SES and Holt.
- Under **(a)** the same series passes the seasonality test, because the check runs against the
  **full** 24 observations and `24 ≥ 2 × 12`.

**The two strategies disagree on this exact input**, and neither is wrong: (a) asks whether the
series has two seasons, (b) asks whether the *training* segment does. The lesson is that a
two-season requirement must state which segment it applies to — the answer changes the model
chosen.

## Governing rules

- **DMD-R9** — a forecast is stated with its horizon and bucket, so a selection made on one horizon
  does not transfer to another. No rule mandates a selection method; several are legitimate, so the choice, the
  holdout policy and the error measure are the project's (see CPT-0008 on what each measure
  penalizes).

## Related

- CPT-0001, CPT-0002, CPT-0004, CPT-0005 — the candidate algorithms.
- CPT-0021 Demand sensing ensemble — the ML-side equivalent (`select_best_model`).

## References

- Hyndman & Athanasopoulos (2021), Ch. 5 — training/test splits and model selection.
