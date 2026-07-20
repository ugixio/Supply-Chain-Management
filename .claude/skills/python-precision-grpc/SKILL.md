---
description: >
  Python calculation core (services/calc) — exact Decimal money (ADR-0019), numerical
  correctness for the SCM algorithms, ROUND_HALF_EVEN, gRPC/protobuf service contract
  (ADR-0020) with string-encoded money, type hints, docstrings and pytest. Use for any
  work in services/calc or the proto/ contracts.
---

# Python calculation core — precision & gRPC

> `services/calc` owns all mathematical models and ML (ADR-0001). It is exposed to the API
> as a gRPC service (`scm.calc.v1`, ADR-0020). Two things must never slip: **financial
> exactness** and **the string-money boundary**.

## Money is Decimal, not float (ADR-0019 / ENG-R4)

- Money and rates use **`decimal.Decimal`** with an explicit `Context` — set precision and
  **`ROUND_HALF_EVEN`** (banker's rounding). Configure it once per process; do not rely on
  the global default.
- **Never** let a monetary value pass through `float`/`numpy.float64`. Analytics on
  *quantities* (demand series, forecasts) may stay float — but the moment a result becomes
  money (cost, price, allocation), it is `Decimal`.
- **Round only at defined boundaries** (the return value, an allocation remainder) — never
  mid-calculation. Allocation/pro-rata: distribute with Decimal and assign the rounding
  remainder deterministically so the parts sum **exactly** to the whole (the "penny
  problem" — the largest-remainder method, documented in the function).
- This is the fix for the live `Math.round(amount*factor)` bug (CPT-0003/U15 kin): the same
  discipline must hold in TS and Python — a money formula in both languages is changed in
  both or neither (risk register #2).

## Numerical correctness

- Type hints are mandatory (`def f(x: Decimal) -> Decimal:`) and docstrings state units,
  assumptions and the reference (matches the existing modules and the CPT concept nodes).
- Guard domains: raise on `holding_cost <= 0` (EOQ), `service_level ∉ (0,1)`, empty series —
  fail fast, don't return NaN silently.
- Prefer `scipy.stats.norm.ppf` for the exact z-score where a concept node specifies it
  (CPT-0003 records that the tables diverge — do not add a third variant; follow the U15
  decision).
- Determinism: seed any stochastic model; document non-determinism; a forecast the tests
  can't reproduce is not shippable.

## gRPC / protobuf contract (ADR-0020)

- Service `scm.calc.v1` in `proto/`. Each RPC is **stateless and idempotent**; no session
  state between calls.
- **Money and rate fields are `string`**, never `double` (ENG-R5) — the client sends a
  decimal string, the server parses to `Decimal`, computes, returns a decimal string.
  Quantities may be `int`/`double` as appropriate, but never money.
- Version the contract; additive changes only within `v1`; a breaking change is `v2`.
- Errors use gRPC status codes with actionable messages; never leak internals.

## Testing (see `testing-quality`)

- `pytest` mirrors the TS coverage bar (SCM-R13). Every public calc function has a test;
  every rule ID it enforces has an assertion.
- **Golden vectors** (U8): a shared fixture set proves TS == Python == SQL for the same
  inputs — the mechanism that prevents another `a12c114` divergence.
- Test the Decimal boundaries explicitly: rounding direction, allocation-sums-to-whole,
  and the string round-trip across the gRPC codec.
