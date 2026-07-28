-- 0005 — two identities, never one (ADR-0034 least privilege, ADR-0036 read path).
--
-- The ingester may only insert; the gateway may only select. Neither may create, drop or alter:
-- schema change is a migration, not something a running service can do.
--
-- The quota numbers are this application's configuration, not a standard. They exist so that one
-- careless dashboard query cannot exhaust the cluster, and they are deliberately generous enough
-- that a legitimate rollup query never hits them.

CREATE ROLE IF NOT EXISTS telemetry_writer;
GRANT INSERT ON telemetry.samples TO telemetry_writer;

CREATE ROLE IF NOT EXISTS telemetry_reader;
-- Raw is readable because incident investigation needs it inside the 14-day window; dashboards are
-- expected to read the coarsest table that answers the question (ADR-0036).
GRANT SELECT ON telemetry.samples    TO telemetry_reader;
GRANT SELECT ON telemetry.samples_1m TO telemetry_reader;
GRANT SELECT ON telemetry.samples_1h TO telemetry_reader;
GRANT SELECT ON telemetry.samples_1d TO telemetry_reader;

CREATE SETTINGS PROFILE IF NOT EXISTS telemetry_reader_profile
SETTINGS max_memory_usage = 4000000000 READONLY,
         max_execution_time = 30 READONLY,
         readonly = 1;

CREATE QUOTA IF NOT EXISTS telemetry_reader_quota
KEYED BY user_name
FOR INTERVAL 1 MINUTE MAX read_rows = 2000000000, result_rows = 5000000, execution_time = 60
TO telemetry_reader;
