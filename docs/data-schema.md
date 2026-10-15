# Trace schema v1

The ingestion format is JSON Lines (JSONL): one JSON object per event. The
validator currently accepts only `schema_version: 1`; a future incompatible
contract must use a new version rather than silently changing these meanings.

## Common fields

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `schema_version` | integer | yes | Contract version; currently `1` |
| `event_id` | non-empty string | yes | Event identifier, unique within a session |
| `session_id` | non-empty string | yes | Capture/session identifier; avoid personal identifiers |
| `timestamp_ns` | non-negative integer | yes | Monotonic event timestamp in nanoseconds |
| `event_type` | string enum | yes | One of the categories below |
| `process_build` | string | no | Application/runtime build identifier |
| `device_id` | string | no | Anonymized device-class label, not a hardware serial |
| `driver_id` | string | no | GPU driver/version identifier |

## Event types and required fields

| `event_type` | Additional required fields | Meaning |
|---|---|---|
| `pipeline_create` | `pipeline_key`, `outcome` | Pipeline creation result |
| `shader_compile` | `pipeline_key`, `compile_duration_ns`, `outcome` | Shader/pipeline compile measurement |
| `cache_lookup` | `pipeline_key`, `cache_result` | Observable cache lookup |
| `frame_timing` | `frame_id`, `frame_duration_ns` | Frame duration measurement |
| `stutter` | `frame_id`, `frame_duration_ns` | Frame classified as a stutter by the collector |

Allowed `outcome` values are `success`, `failure`, `cancelled`, and `unknown`.
Allowed `cache_result` values are `hit`, `miss`, and `unknown`. Durations
are integer nanoseconds and cannot be negative. A duration of zero is valid
only when the source actually measured zero; do not use it as a missing-value
sentinel.

## Validation and normalization

- Unknown fields are rejected in schema v1 to catch producer/consumer drift.
- Missing event-specific required fields and invalid types are errors.
- Malformed JSON and duplicate `(session_id, event_id)` pairs stop ingestion
  with the source path and line number. The parser does not silently skip rows.
- Blank lines are ignored.
- Normalized rows preserve event fields and add `source_path` (basename only)
  and `source_line` provenance. Unavailable optional values remain null.
- Source timestamps are preserved; the parser does not reorder events or infer
  clock synchronization across sessions.

## Local usage

After installing the project with `python -m pip install -e '.[dev]'`:

```bash
python scripts/normalize_traces.py tests/fixtures/sample_trace.jsonl data/processed/sample.parquet
```

Only synthetic fixtures belong in the public repository. Real captures should
be reviewed for secrets and identifying metadata and kept outside Git by default.
