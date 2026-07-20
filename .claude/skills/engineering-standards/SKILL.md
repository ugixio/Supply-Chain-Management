---
description: >
  Professional code standards for ALL engineering agents (HOW lane) — SOLID, DRY, KISS,
  YAGNI, separation of concerns, clean code, fail-fast, defensive programming, secure by
  default, error handling and immutability. Use before writing or reviewing any code in
  apps/, packages/ or services/. Technology-agnostic; the per-stack skills add specifics.
---

# Engineering Standards — the professional baseline

> These are the practices every HOW-lane agent applies. They are **defaults, not dogma**:
> a principle that would make the code worse for this repo loses to KISS. When two
> principles collide, prefer the one that keeps the change **simple and reversible**
> (`evaluation.md` §1.4).

## Design principles (apply, don't cargo-cult)

- **SOLID** — Single-responsibility (one reason to change per module); Open/closed (extend
  via new code, not by editing stable code); Liskov (subtypes honour the contract);
  Interface-segregation (small, role-specific ports); Dependency-inversion (depend on
  abstractions — this is the Clean-Architecture dependency rule, see `clean-architecture`).
- **DRY** — one authoritative home per fact/behaviour; elsewhere reference it. Mirrors the
  repo's SSOT rule. **But**: duplicated code that is only *coincidentally* similar is not a
  DRY violation — don't couple two things because they look alike today.
- **KISS / YAGNI** — build the simplest thing that satisfies the current spec and rules;
  do **not** add abstraction, config or generality for a future that isn't in the backlog.
  A speculative interface is a maintenance cost with no user.
- **Separation of concerns · high cohesion · low coupling** — a module does one thing;
  related code lives together; cross-module talk goes through published ports (ENG-R3).
- **Composition over inheritance** — prefer wiring small pieces to deep class trees.
- **Convention over configuration** — follow the framework's idiom (Nest, Next) instead of
  bespoke wiring; fewer decisions, less to explain.

## Correctness & safety

- **Fail fast.** Validate inputs at the boundary; throw on invariant violation rather than
  limping on with bad state. The domain already does this (guard throws) — keep it.
- **Defensive programming at trust boundaries only.** Validate external input (HTTP, gRPC,
  DB rows, user); trust already-validated internal calls. Don't re-validate everywhere —
  that's noise that hides the real checks.
- **Secure by default (PoLP).** Least privilege everywhere: narrow tool/permission scopes,
  no secrets in code or logs, parameterized queries (never string-built SQL), deny-by-
  default authorization. Validate and encode at every boundary. Never log money-affecting
  or PII data at info level.
- **Money is exact.** No float ever touches a monetary value (SCM-R8/ENG-R4). See
  `python-precision-grpc` and `postgresql-data` for the Decimal/NUMERIC contract.
- **Errors are typed and meaningful.** No silent `catch {}`; either handle, wrap with
  context, or rethrow. A swallowed error is a future 3 a.m. page.
- **Immutability by default.** Prefer readonly/`const`, pure functions, new-value-returns
  over mutation — the domain ring is already built this way (SCM-R immutable objects).

## Clean code (what a reviewer checks)

- Names say intent; no abbreviations that need a decoder. Functions do one thing at one
  level of abstraction. Comments explain **why**, not **what** (the code says what).
- Match the surrounding code's idiom, density and naming — a diff should read like the
  file it lands in, not like a different author.
- No dead code, no commented-out blocks, no TODO without a backlog entry (WORKFLOW.md).
- Small, reviewable units. A change that can't be reviewed in one sitting is two changes.

## How this fits the repo

- Every non-trivial choice: name ≥2 alternatives + trade-offs, pick the simplest that
  respects the rules (`evaluation.md` §1.4), record it at the right altitude
  (decision ladder §2).
- Definition of Done and the communication contract are in `operating-model.md` §4 —
  reference them; this skill does not restate them.
- Corrections from the owner become one-line **Known-pitfalls** entries in the relevant
  domain SKILL.md (§4.7) — a correction not recorded is repeated.
