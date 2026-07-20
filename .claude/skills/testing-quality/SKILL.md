---
description: >
  Testing and quality for this repo — TDD (red-green-refactor), jest (TS) and pytest
  (Python), a test per rule ID (SCM-R13), cross-language golden vectors (U8), contract
  tests for GraphQL/gRPC, coverage and the make verify gates. Use when writing tests,
  verifying a change, or setting up test infrastructure.
---

# Testing & Quality

> The gate is `make verify` (fast: doc gates + typecheck + unit tests) and
> `make verify-full` (merge gate). "Green" means it actually ran — never "should pass"
> (`operating-model.md` §4.2). Report the real output.

## Test-first (the default workflow)

- **Red → green → refactor.** Write the failing test that encodes the spec/rule, make it
  pass with the simplest code, then clean up under a green bar.
- **A test per rule ID.** Every SCM-Rx / department-family / ENG-Rx rule a change touches
  keeps (or gets) a test that would fail if the rule were violated (SCM-R13). This is how a
  rule stays real instead of decorative.
- Name tests by behaviour: `it('rejects a PO sent to supplier without APPROVED (PRC-R2)')`.
  A test name is a sentence about the system.

## What to test at each layer

- **Domain (`packages/domain`)** — pure unit tests, no mocks needed (it's framework-free).
  Cover guards, state machines, formulas against the CPT worked examples.
- **Application** — use-case tests with in-memory port fakes; assert orchestration and
  error mapping, not the adapters.
- **Infrastructure** — integration tests against a real Postgres (testcontainers or a CI
  service); assert soft-delete, idempotency (SCM-R12), NUMERIC exactness.
- **apps/api** — **contract tests**: the generated `schema.gql` shape is asserted; resolver
  tests prove no N+1 and correct mapping.
- **apps/web** — component tests for node states + sidebar; **a11y check (axe)** and a
  keyboard-navigation test (ADR-0026 floor).
- **services/calc** — pytest per public function; Decimal boundary tests (rounding,
  allocation-sums-to-whole, gRPC string round-trip).

## Cross-language golden vectors (U8 — prevents another `a12c114`)

- For any formula implemented in **both** TS and Python (safety stock, EOQ, accuracy
  metrics, z-score…), keep a **shared fixture** of `(inputs → expected)` and assert both
  implementations against it, plus the SQL where money lands. A formula changed in one
  language and not the other must break this test.
- The z-score divergence (CPT-0003) is the standing example: the golden vectors are where
  the U15 canonical choice gets enforced.

## Coverage & discipline

- Coverage is a floor, not a goal — 100% of trivial getters proves nothing. Cover the
  branches that encode rules and the edge/degenerate cases (empty series, zero inventory,
  divide-by-zero sentinels the concept nodes call out).
- No flaky tests: seed randomness, freeze time (`date-fns`/fixed clock), no real network.
- A skipped test is a backlog entry (WORKFLOW.md), not a silent `xit`.

## The two gates (ADR-0012)

- `make verify` after **every layer** — not only at the end.
- `make verify-full` before proposing a merge. pytest joins the gate at U7; eslint flat
  config at U12. Until then, run pytest manually when Python changed and report it.
