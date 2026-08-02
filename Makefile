# Single command entry point (ADR-0012). Two speeds, one truth:
#
#   verify       FAST gate: doc gates + typecheck + the Rust tests — run after EVERY layer,
#                not only at the end.
#   verify-full  The merge/CI gate: the fast gate plus the lockfile check and Rust fmt/clippy.
#
# ADR-0037 deleted the invented SCM application, so the Jest and pytest targets went with the
# code they tested. `typecheck` still guards the standards reference module in
# `packages/shared`; `test-rs` guards `crates/scm-money`. Test targets come back when the
# monitoring application has code worth testing — not before, and never as an empty runner.
#
# `verify-full` is the PORTABLE merge gate: it runs anywhere, with no service dependency.
# `verify-schema` is the SERVICE-DEPENDENT gate: it needs a reachable ClickHouse, so it is a
# separate target — and CI runs BOTH. That splits the old "CI runs exactly verify-full" invariant,
# deliberately and visibly rather than by accident, because the alternative was worse in both
# directions: folding it into verify-full makes the merge gate unrunnable without a database, and
# letting it skip when no server is present recreates the false green that `deps-locked` exists to
# prevent. The residual gap is real and bounded: a schema change gets its first execution in CI
# unless the developer starts the compose file locally.
#
# CI runs: make verify-full  &&  make verify-schema

.PHONY: verify verify-full verify-schema doc-gates gate-mutants typecheck deps-locked test-rs lint-rs

verify: doc-gates typecheck test-rs

verify-full: verify gate-mutants deps-locked lint-rs

doc-gates:
	python3 tools/verify.py

# Do the gates still catch what they claim to? Plants one violation per gate in a throwaway
# worktree and asserts each fires — and that no other does. In `verify-full` rather than
# `verify` because it runs the gates fourteen times over and belongs at the merge boundary,
# not in the loop a session runs after every layer.
gate-mutants:
	python3 tools/test_gates.py
	python3 tools/context_eval.py --self-test

typecheck:
	pnpm -s exec tsc --noEmit

# The lockfile must agree with every package.json — the exact invocation CI performs.
# Added after a dependency was removed from a package.json without regenerating the lockfile:
# the local gate passed (node_modules was already installed) and CI failed on the install step,
# which the gate never exercised. A gate that skips what CI does is not a gate.
deps-locked:
	pnpm install --frozen-lockfile --ignore-scripts

# `crates/scm-money` — exact money arithmetic, the one piece of the old estate that carries no
# policy (banker's rounding is IEEE 754; sum-preserving apportionment is a fixed method).
test-rs:
	cargo test --workspace --quiet

# Merge-gate only (slower): formatting plus clippy with warnings as errors.
lint-rs:
	cargo fmt --all -- --check
	cargo clippy --workspace --all-targets -- -D warnings

# The ClickHouse telemetry schema (ADR-0036). Applies the migrations, proves they are idempotent by
# applying them twice, then asserts the sort key, partitioning, codecs, TTLs, aggregate states and
# the materialized-view cascade. FAILS if no server is reachable — it never skips.
#   docker compose -f db/clickhouse/docker-compose.yml up -d
verify-schema:
	python3 db/clickhouse/apply.py
