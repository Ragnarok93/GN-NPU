"""JSONL trace ingestion with validation and source-line provenance."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator

from gn_npu.ingest.schema import TraceValidationError, validate_event

NORMALIZED_FIELDS = (
    "schema_version",
    "event_id",
    "session_id",
    "timestamp_ns",
    "event_type",
    "process_build",
    "device_id",
    "driver_id",
    "pipeline_key",
    "cache_result",
    "compile_duration_ns",
    "frame_id",
    "frame_duration_ns",
    "outcome",
)


class TraceParseError(ValueError):
    """Raised when a JSONL capture cannot be parsed without data loss."""


def iter_normalized_events(path: str | Path) -> Iterator[dict[str, Any]]:
    """Yield normalized event rows, rejecting malformed lines and duplicate IDs."""
    source = Path(path)
    seen_ids: set[tuple[str, str]] = set()

    try:
        handle = source.open("r", encoding="utf-8")
    except OSError as exc:
        raise TraceParseError(f"cannot open trace {source}: {exc}") from exc

    with handle:
        for line_number, raw_line in enumerate(handle, start=1):
            if not raw_line.strip():
                continue
            try:
                event = json.loads(raw_line)
                validated = validate_event(event)
            except (json.JSONDecodeError, TraceValidationError) as exc:
                raise TraceParseError(f"{source}:{line_number}: {exc}") from exc

            identity = (validated["session_id"], validated["event_id"])
            if identity in seen_ids:
                raise TraceParseError(
                    f"{source}:{line_number}: duplicate event_id "
                    f"{validated['event_id']!r} in session {validated['session_id']!r}"
                )
            seen_ids.add(identity)

            row = {field: validated.get(field) for field in NORMALIZED_FIELDS}
            row["source_path"] = source.name
            row["source_line"] = line_number
            yield row


def normalize_jsonl_to_parquet(
    input_path: str | Path, output_path: str | Path
) -> int:
    """Normalize a JSONL capture to Parquet and return the number of events."""
    import pandas as pd

    rows = list(iter_normalized_events(input_path))
    if not rows:
        raise TraceParseError(f"{input_path}: no trace events found")

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame.from_records(rows)
    frame.to_parquet(destination, index=False)
    return len(rows)
