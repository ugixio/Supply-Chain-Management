# Single command entry point (ADR-0012). Two speeds, one truth:
#
#   verify       FAST gate: doc gates + typecheck + unit tests — the AI runs this after
#                EVERY layer, not only at the end.
#   verify-full  The merge/CI gate: fast gate + the full jest suite. eslint (flat config
#                pending, U12) and pytest (U7) join here when they land.
#
# Toolchain: pnpm workspaces + Turborepo (ADR-0022). Never fork a second entry point:
# CI runs exactly `make verify-full`.

.PHONY: verify verify-full doc-gates typecheck test-unit test

verify: doc-gates typecheck test-unit

verify-full: verify test

doc-gates:
	python3 tools/verify.py

typecheck:
	pnpm -s exec tsc --noEmit

test-unit:
	pnpm -s exec jest tests/unit --silent

test:
	pnpm -s exec jest --runInBand --silent
