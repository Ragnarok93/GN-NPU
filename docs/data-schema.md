# Trace schema: initial contract

The ingestion format will initially be JSON Lines: one JSON object per event.
A later normalization stage may write Parquet for efficient analysis.

Common fields:

- schema_version: integer
- event_id: identifier unique within a capture
- session_id: capture/session identifier
- timestamp_ns: monotonic timestamp in nanoseconds
- event_type: stable event category
- process_build: application/runtime build identifier, if available
- device_id: anonymized device-class identifier
- driver_id: GPU driver/version identifier, if available

Event-specific fields may include pipeline_key, cache_result,
compile_duration_ns, frame_id, frame_duration_ns, and outcome.

Missing fields mean unknown or unavailable; they must not silently become zero.
Document units and semantics for each field. Preserve source timestamps and parser
provenance so normalized records can be traced to their source.
