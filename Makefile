# Single command entry point (ADR-0012). Two speeds, one truth:
#
#   verify       FAST gate: doc gates + typecheck + unit tests — the AI runs this after
#                EVERY layer, not only at the end.
#   verify-full  The merge/CI gate: fast gate + the full jest suite + the Python money
#                tests (U7 first enforced slice: services/calc/tests, stdlib-only — the
#                heavy ML suite stays out of CI, risk register #6). eslint flat config
#                still pending (U12).
#
# Toolchain: pnpm workspaces + Turborepo (ADR-0022). Never fork a second entry point:
# CI runs exactly `make verify-full`.

.PHONY: verify verify-full doc-gates typecheck test-unit test test-py

verify: doc-gates typecheck test-unit

verify-full: verify test test-py

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
