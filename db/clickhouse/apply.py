#!/usr/bin/env python3
"""Apply the ClickHouse migrations in order, then assert the schema is what ADR-0036 fixes.

Stdlib only, like `tools/verify.py` — a schema gate that needed its own dependency tree would be
one more thing to keep installed for the gate to mean anything.

Strict by design: if no ClickHouse is reachable this **fails**. It does not skip. A schema check
that quietly does nothing when the server is absent is how a false green happens, and this
repository has already paid for that class of mistake twice (G11's front-matter-only scan, and the
lockfile the local gate never installed).

Usage:
    CLICKHOUSE_URL=http://localhost:8123 python3 db/clickhouse/apply.py [--check-only]

`--check-only` skips applying and asserts the schema of an already-migrated server.
"""

from __future__ import annotations

import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

MIGRATIONS = Path(__file__).resolve().parent / "migrations"
DEFAULT_URL = "http://localhost:8123"

# What ADR-0036 fixes, restated as assertions. Each entry is (table, expected substring, why).
# These are checked against `SHOW CREATE TABLE`, so a silent drift in the sort key, the partition
# key or a codec fails the gate rather than being discovered in a slow dashboard months later.
SCHEMA_ASSERTIONS: list[tuple[str, str, str]] = [
    ("telemetry.samples", "ORDER BY (project_id, metric, ts)",
     "ADR-0036 sort key: supervision queries scope to a project, then a metric, then time"),
    ("telemetry.samples", "PARTITION BY toYYYYMM(ts)",
     "monthly parts; daily partitions fragment at tens of thousands of series"),
    ("telemetry.samples", "CODEC(Delta",
     "timestamps are Delta-encoded before ZSTD"),
    ("telemetry.samples", "CODEC(Gorilla",
     "float values use Gorilla — the codec built for slowly-varying series"),
    ("telemetry.samples", "TTL",
     "raw samples expire; the rollups carry history"),
    ("telemetry.samples_1m", "AggregatingMergeTree",
     "the rollup aggregates at insert time"),
    ("telemetry.samples_1h", "AggregatingMergeTree", "cascade stage 2"),
    ("telemetry.samples_1d", "AggregatingMergeTree", "cascade stage 3"),
]

# Every stage must hold aggregate *states*, not finished numbers: a finished average cannot be
# re-aggregated into a coarser bucket without becoming an average of averages.
STATE_TABLES = ("telemetry.samples_1m", "telemetry.samples_1h", "telemetry.samples_1d")


def query(url: str, sql: str) -> str:
    request = urllib.request.Request(url, data=sql.encode("utf-8"), method="POST")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", "replace").strip()
        raise SystemExit(f"FAIL ClickHouse rejected a statement:\n{detail}\n\nSQL:\n{sql}")
    except OSError as error:
        raise SystemExit(
            f"FAIL cannot reach ClickHouse at {url}: {error}\n"
            "This gate does not skip when the server is absent — an unexecuted schema is "
            "untested code. Start one with:\n"
            "    docker compose -f db/clickhouse/docker-compose.yml up -d"
        )


def apply_migrations(url: str) -> None:
    files = sorted(MIGRATIONS.glob("*.sql"))
    if not files:
        raise SystemExit(f"FAIL no migrations found in {MIGRATIONS}")
    for path in files:
        # ClickHouse's HTTP interface takes one statement per request, so the file is split on `;`.
        # Comments are stripped first: a `;` inside a comment would otherwise split mid-statement.
        body = "\n".join(
            line for line in path.read_text(encoding="utf-8").splitlines()
            if not line.lstrip().startswith("--")
        )
        statements = [s.strip() for s in body.split(";") if s.strip()]
        for statement in statements:
            query(url, statement)
        print(f"  applied {path.name} ({len(statements)} statements)")


def assert_schema(url: str) -> int:
    failures: list[str] = []

    for table, expected, why in SCHEMA_ASSERTIONS:
        ddl = query(url, f"SHOW CREATE TABLE {table}")
        # SHOW CREATE escapes newlines; normalize so a substring match is meaningful.
        flat = ddl.replace("\\n", " ")
        if expected not in flat:
            failures.append(f"{table}: expected {expected!r} — {why}")

    for table in STATE_TABLES:
        ddl = query(url, f"SHOW CREATE TABLE {table}").replace("\\n", " ")
        if "AggregateFunction" not in ddl:
            failures.append(
                f"{table}: holds no AggregateFunction column — a rollup must store mergeable "
                "states, or the next stage averages averages"
            )

    # The cascade must actually be wired: each stage needs its materialized view.
    views = query(url, "SELECT name FROM system.tables WHERE database = 'telemetry' "
                       "AND engine = 'MaterializedView' ORDER BY name")
    present = set(views.split())
    for expected_view in ("samples_1m_mv", "samples_1h_mv", "samples_1d_mv"):
        if expected_view not in present:
            failures.append(f"missing materialized view {expected_view} — the cascade is not wired")

    if failures:
        print("FAIL schema does not match ADR-0036:")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print(f"GREEN schema matches ADR-0036 "
          f"({len(SCHEMA_ASSERTIONS)} assertions, {len(STATE_TABLES)} state tables, 3 views)")
    return 0


def main() -> int:
    url = os.environ.get("CLICKHOUSE_URL", DEFAULT_URL)
    check_only = "--check-only" in sys.argv

    query(url, "SELECT 1")  # fail fast and clearly if unreachable
    if not check_only:
        print(f"Applying migrations to {url}")
        apply_migrations(url)
        # Applying twice must be a no-op: every statement is IF NOT EXISTS, and a migration that
        # is not idempotent cannot be re-run safely on a server that is partly migrated.
        print("Re-applying to prove idempotence")
        apply_migrations(url)

    return assert_schema(url)


if __name__ == "__main__":
    sys.exit(main())
