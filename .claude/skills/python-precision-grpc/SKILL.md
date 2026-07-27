---
description: >
  Python as the tools layer (ADR-0033/0035) — exact Decimal money, numerical
  correctness for the SCM algorithms, ROUND_HALF_EVEN, gRPC/protobuf service contract
  (ADR-0020) with string-encoded money, type hints, docstrings and pytest. Use for any
  work in the Python tools layer or the shared `.proto` contract.
---

# Python as the tools layer — precision & gRPC

> Python owns models, statistics, optimization and ML — and nothing else (ENG-R8). It is reached
> as a gRPC service (`scm.calc.v1`, ADR-0020) called **by the Rust core**, never by the frontend.
> It decides no business rule and holds no policy value. Two things must never slip: **financial
> exactness** and **the string-money boundary**.
>
> There is no Python in the repository today — ADR-0037 deleted the invented calculation service.
> This lane activates with Phase M, over the monitoring platform's telemetry.

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
- **Exact money belongs to the core, not here** (ENG-R4/R10): `crates/scm-money` is the one
  implementation. Python parses a decimal string, keeps it exact through any arithmetic it must
  do, and returns a decimal string. Re-implementing an apportionment in Python creates the
  divergence risk the single core exists to remove (risk register #2).

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

- Every public function has a test, and every live rule ID it enforces has an assertion naming
  that ID. Check the rule is live first — a retired ID fails gate G11.
- **Golden vectors:** where the same arithmetic is exercised from more than one place, both read
  one shared fixture (`tests/golden/*.json`) and the vectors pass **unchanged**. Editing a
  fixture to make a suite green is a rule violation, not a fix.
- Test the Decimal boundaries explicitly: rounding direction, allocation-sums-to-whole,
  and the string round-trip across the gRPC codec.
