# Single command entry point (ADR-0012). Two speeds, one truth:
#
#   verify       FAST gate: doc gates + typecheck + unit tests — the AI runs this after
#                EVERY layer, not only at the end.
#   verify-full  The merge/CI gate: fast gate + the full jest suite. eslint (flat config
#                pending) and pytest (U7: zero Python tests yet) join here when they land.
#
# Never fork a second entry point: CI runs exactly `make verify-full`.

.PHONY: verify verify-full doc-gates typecheck test-unit test

verify: doc-gates typecheck test-unit

verify-full: verify test

doc-gates:
	python3 tools/verify.py

typecheck:
	npm run --silent typecheck

test-unit:
	npx --no-install jest tests/unit --silent

test:
	npm test --silent
