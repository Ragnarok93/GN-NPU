import json
from pathlib import Path

import pandas as pd
import pytest

from gn_npu.ingest.jsonl import (
    TraceParseError,
    iter_normalized_events,
    normalize_jsonl_to_parquet,
)
from gn_npu.ingest.schema import TraceValidationError, validate_event

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "sample_trace.jsonl"


def test_synthetic_fixture_normalizes_with_provenance() -> None:
    rows = list(iter_normalized_events(FIXTURE))

    assert len(rows) == 5
    assert rows[0]["event_type"] == "pipeline_create"
    assert rows[0]["source_path"] == "sample_trace.jsonl"
    assert rows[0]["source_line"] == 1
    assert rows[2]["compile_duration_ns"] == 250_000
    assert rows[3]["frame_duration_ns"] == 16_666_667


def test_missing_measurement_stays_missing() -> None:
    rows = list(iter_normalized_events(FIXTURE))

    assert rows[1]["compile_duration_ns"] is None
    assert rows[1]["frame_duration_ns"] is None
    assert rows[1]["device_id"] is None


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"timestamp_ns": True}, "timestamp_ns"),
        ({"timestamp_ns": -1}, "timestamp_ns"),
        ({"pipeline_key": ""}, "pipeline_key"),
        ({"unexpected": "value"}, "unknown field"),
        ({"schema_version": 2}, "schema_version"),
    ],
)
def test_invalid_events_are_rejected(change: dict, message: str) -> None:
    event = {
        "schema_version": 1,
        "event_id": "evt",
        "session_id": "session",
        "timestamp_ns": 1,
        "event_type": "pipeline_create",
        "pipeline_key": "pipeline",
        "outcome": "success",
    }
    event.update(change)

    with pytest.raises(TraceValidationError, match=message):
        validate_event(event)


def test_event_type_specific_fields_are_required() -> None:
    with pytest.raises(TraceValidationError, match="compile_duration_ns"):
        validate_event(
            {
                "schema_version": 1,
                "event_id": "evt",
                "session_id": "session",
                "timestamp_ns": 1,
                "event_type": "shader_compile",
                "pipeline_key": "pipeline",
                "outcome": "success",
            }
        )


def test_malformed_json_reports_source_line(tmp_path: Path) -> None:
    trace = tmp_path / "bad.jsonl"
    trace.write_text('{"schema_version": 1}\n{broken\n', encoding="utf-8")

    with pytest.raises(TraceParseError, match=r"bad\.jsonl:2"):
        list(iter_normalized_events(trace))


def test_duplicate_event_id_in_session_is_rejected(tmp_path: Path) -> None:
    event = {
        "schema_version": 1,
        "event_id": "same",
        "session_id": "session",
        "timestamp_ns": 1,
        "event_type": "pipeline_create",
        "pipeline_key": "pipeline",
        "outcome": "success",
    }
    trace = tmp_path / "duplicates.jsonl"
    trace.write_text(
        json.dumps(event) + "\n" + json.dumps({**event, "timestamp_ns": 2}) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(TraceParseError, match="duplicate event_id"):
        list(iter_normalized_events(trace))


def test_normalizer_writes_parquet_round_trip(tmp_path: Path) -> None:
    output = tmp_path / "processed" / "trace.parquet"

    count = normalize_jsonl_to_parquet(FIXTURE, output)
    frame = pd.read_parquet(output)

    assert count == 5
    assert len(frame) == 5
    assert frame.loc[2, "compile_duration_ns"] == 250_000
    assert pd.isna(frame.loc[1, "compile_duration_ns"])
    assert frame.loc[4, "source_line"] == 5


def test_empty_capture_is_rejected(tmp_path: Path) -> None:
    trace = tmp_path / "empty.jsonl"
    trace.write_text("\n  \n", encoding="utf-8")

    with pytest.raises(TraceParseError, match="no trace events"):
        normalize_jsonl_to_parquet(trace, tmp_path / "empty.parquet")
