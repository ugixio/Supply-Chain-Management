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
# Never fork a second entry point: CI runs exactly `make verify-full`.

.PHONY: verify verify-full doc-gates typecheck deps-locked test-rs lint-rs

verify: doc-gates typecheck test-rs

verify-full: verify deps-locked lint-rs

doc-gates:
	python3 tools/verify.py

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
