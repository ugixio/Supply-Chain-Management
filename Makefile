# Single command entry point (ADR-0012). Two speeds, one truth:
#
#   verify       FAST gate: doc gates + typecheck + unit tests + the Rust core tests — the
#                AI runs this after EVERY layer, not only at the end.
#   verify-full  The merge/CI gate: fast gate + the full jest suite + the Python money
#                tests (U7 first enforced slice: services/calc/tests, stdlib-only — the
#                heavy ML suite stays out of CI, risk register #6) + Rust fmt/clippy.
#                eslint flat config still pending (U12).
#
# Toolchain: pnpm workspaces + Turborepo (ADR-0022) and a Cargo workspace for the Rust core
# (ADR-0035). Never fork a second entry point: CI runs exactly `make verify-full`.

.PHONY: verify verify-full doc-gates typecheck test-unit test test-py test-rs lint-rs

verify: doc-gates typecheck test-unit test-rs

verify-full: verify test test-py lint-rs

doc-gates:
	python3 tools/verify.py

typecheck:
	pnpm -s exec tsc --noEmit

test-unit:
	pnpm -s exec jest tests/unit --silent

test:
	pnpm -s exec jest --runInBand --silent

test-py:
	python3 -m pytest services/calc/tests -q

# The Rust core (ADR-0035). Part of the FAST gate: its golden-vector suite reads the same
# tests/golden fixture the Jest and pytest suites read, so a cross-language divergence in
# money arithmetic fails here first (ENG-R10.6).
test-rs:
	cargo test --workspace --quiet

# Merge-gate only (slower): formatting plus clippy with warnings as errors.
lint-rs:
	cargo fmt --all -- --check
	cargo clippy --workspace --all-targets -- -D warnings
