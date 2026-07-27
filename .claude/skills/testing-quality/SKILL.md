---
description: >
  Testing and quality for this repository — what the gates actually run today (doc gates
  G1-G11, tsc, cargo test, fmt/clippy), test-first discipline, a test per live rule ID,
  the golden-vector fixture pattern, and what each lane will need when the monitoring
  application arrives. Use when writing tests, verifying a change, or adding a gate.
---

# Testing & Quality

> The gate is `make verify` (fast) and `make verify-full` (the merge gate — exactly what CI
> runs). "Green" means it actually ran — never "should pass" (`operating-model.md` §4.2).
> Report the real output, including the failure.

## What the gates run today

`make verify` → `doc-gates` (`tools/verify.py`, G1–G11) · `typecheck` (`tsc --noEmit` over
`packages/shared`) · `test-rs` (`cargo test --workspace`).
`make verify-full` adds `deps-locked` (`pnpm install --frozen-lockfile`) and `lint-rs`
(`cargo fmt --check`, `clippy -D warnings`).

ADR-0037 deleted the invented application, and its Jest and pytest suites went with the code
they tested. So the honest picture is: **the documentation gates and `crates/scm-money` are the
whole test estate.** Do not add an empty runner to make the list look fuller — a target that
passes because it found nothing to run is worse than no target, because it reads as coverage.

Two properties every gate here must keep:

- **It covers the whole estate.** G11 (retired rules stay retired) first shipped scanning only
  front-matter documents and reported green while `.claude/` cited three retired IDs. A gate
  over part of the estate produces a false green.
- **It exercises what CI exercises.** `deps-locked` exists because a stale lockfile passed
  locally (`node_modules` was already installed) and failed in CI on a step the gate never ran.

## Test-first (the default workflow)

- **Red → green → refactor.** Write the failing test that encodes the rule or concept, make it
  pass with the simplest code, then clean up under a green bar.
- **A test per live rule ID.** A change touching an `SCM-R*`, `ENG-R*` or department-family
  invariant keeps (or gets) a test that fails if the rule is violated. Cite the ID in the test
  name: `#[test] fn allocation_sums_to_the_whole_scm_r14()`. Check the rule is **live** first —
  a retired ID in a test name is a G11 failure, and the rule files list retirements with the
  ID that replaced them.
- **Only live rules get tests.** Retired rules were retired because they encoded policy
  (ADR-0037); a test asserting a retired threshold re-introduces the policy through the back
  door.
- Name tests by behaviour, not by function: a test name is a sentence about the system.

## The golden-vector pattern

`tests/golden/money.golden.json` is the model. A fixture of `(inputs → expected)` lives in its
own file, each vector carries a `why` naming the case it protects, and the suite reads it rather
than inlining values.

- **The vectors must pass unchanged.** Editing a fixture to make a suite green is a rule
  violation, not a fix.
- Use the pattern when the same arithmetic will be exercised from more than one place — that is
  what stops two implementations drifting apart silently.
- Vectors encode *identities and standards* (IEEE 754 tie behaviour, sum preservation), never a
  project's chosen parameter. A fixture asserting a 5% tolerance is policy in a JSON file.

## What to test per lane, when each lane exists

- **Rust core (`crates/*`)** — pure unit tests, no mocks: it takes identity and time as inputs
  and holds no I/O (ENG-R10). Cover guards, state machines, and exact arithmetic at its edges
  (ties, overflow, empty and degenerate inputs).
- **The standards module (`packages/shared`)** — the check-digit and code-validity functions are
  the testable surface: valid keys, keys with a wrong check digit, wrong-length input, and the
  sea-only Incoterms set.
- **`apps/api` (NestJS, Phase M)** — contract tests: the generated `schema.gql` shape is
  asserted, never hand-edited (ENG-R6). Resolver tests prove mapping and no N+1. The gateway
  computes no business result, so there is no business assertion to make here.
- **`apps/web` (Next.js, Phase M)** — component tests plus an accessibility check (axe) and a
  keyboard-navigation test (ADR-0026 floor).
- **PostgreSQL** — integration tests against a real server: `NUMERIC` exactness, and that a
  correction appends rather than destroys (SCM-R3).
- **ClickHouse (ADR-0036)** — assert the rollup cascade agrees with the raw tier for the same
  window; a rollup that disagrees with its source is the failure mode worth a test.
- **Python tools (Phase M)** — pytest per public function; `Decimal` boundary tests and the
  gRPC string round-trip for money (ENG-R5).

## Coverage & discipline

- Coverage is a floor, not a goal — 100% of trivial getters proves nothing. Cover the branches
  that encode rules and the degenerate cases the concept nodes call out (empty series, zero
  denominator, divide-by-zero sentinels).
- No flaky tests: seed randomness, freeze time behind a fixed clock, no real network.
- A skipped test is a backlog entry (`docs/program/WORKFLOW.md`), not a silent skip marker.
- **Verify a new gate check by planting the failure it is meant to catch**, then removing it.
  A check that has never gone red has not been tested.

## Documentation is under test too

The doc gates are the main suite in this repository, so treat a doc change like code: run
`make verify` after it. G9 (context budget) fails on a file that grew past its word budget —
the fix is to reference the normative statement, not to restate it. G10 requires a cited source
and no `## Implementations` on a concept node. **Read a scripted prose edit back in the diff
before committing**: bulk substitutions across `.md` have twice produced sentences that parse as
the opposite of what they mean, and no gate catches that.
