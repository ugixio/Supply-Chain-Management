# Single command entry point (ADR-0012). Two speeds, one truth:
#
#   verify       FAST gate: doc gates + typecheck + the Rust tests — run after EVERY layer,
#                not only at the end.
#   verify-full  The merge/CI gate: the fast gate plus Rust fmt and clippy.
#
# ADR-0037 deleted the invented SCM application, so the Jest and pytest targets went with the
# code they tested. `typecheck` still guards the standards reference module in
# `packages/shared`; `test-rs` guards `crates/scm-money`. Test targets come back when the
# monitoring application has code worth testing — not before, and never as an empty runner.
#
# Never fork a second entry point: CI runs exactly `make verify-full`.

.PHONY: verify verify-full doc-gates typecheck test-rs lint-rs

verify: doc-gates typecheck test-rs

verify-full: verify lint-rs

doc-gates:
	python3 tools/verify.py

typecheck:
	pnpm -s exec tsc --noEmit

# `crates/scm-money` — exact money arithmetic, the one piece of the old estate that carries no
# policy (banker's rounding is IEEE 754; sum-preserving apportionment is a fixed method).
test-rs:
	cargo test --workspace --quiet

# Merge-gate only (slower): formatting plus clippy with warnings as errors.
lint-rs:
	cargo fmt --all -- --check
	cargo clippy --workspace --all-targets -- -D warnings
