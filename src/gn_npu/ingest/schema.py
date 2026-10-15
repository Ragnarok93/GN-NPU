"""Validation for the versioned GN-NPU JSONL trace contract."""

from __future__ import annotations

from typing import Any

SCHEMA_VERSION = 1

COMMON_REQUIRED = {
    "schema_version",
    "event_id",
    "session_id",
    "timestamp_ns",
    "event_type",
}
OPTIONAL_COMMON = {"process_build", "device_id", "driver_id"}
EVENT_FIELDS = {
    "pipeline_key",
    "cache_result",
    "compile_duration_ns",
    "frame_id",
    "frame_duration_ns",
    "outcome",
}
ALLOWED_FIELDS = COMMON_REQUIRED | OPTIONAL_COMMON | EVENT_FIELDS

EVENT_REQUIRED = {
    "pipeline_create": {"pipeline_key", "outcome"},
    "shader_compile": {"pipeline_key", "compile_duration_ns", "outcome"},
    "cache_lookup": {"pipeline_key", "cache_result"},
    "frame_timing": {"frame_id", "frame_duration_ns"},
    "stutter": {"frame_id", "frame_duration_ns"},
}
OUTCOMES = {"success", "failure", "cancelled", "unknown"}
CACHE_RESULTS = {"hit", "miss", "unknown"}


class TraceValidationError(ValueError):
    """Raised when a trace event violates the schema contract."""


def _require_nonempty_string(event: dict[str, Any], field: str) -> None:
    value = event.get(field)
    if not isinstance(value, str) or not value.strip():
        raise TraceValidationError(f"{field!r} must be a non-empty string")


def _require_nonnegative_int(event: dict[str, Any], field: str) -> None:
    value = event.get(field)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise TraceValidationError(f"{field!r} must be a non-negative integer")


def _optional_string(event: dict[str, Any], field: str) -> None:
    value = event.get(field)
    if value is not None and (not isinstance(value, str) or not value.strip()):
        raise TraceValidationError(f"{field!r} must be a non-empty string when provided")


def validate_event(event: Any) -> dict[str, Any]:
    """Validate one event and return it unchanged as a plain dictionary."""
    if not isinstance(event, dict):
        raise TraceValidationError("event must be a JSON object")

    unknown = set(event) - ALLOWED_FIELDS
    if unknown:
        raise TraceValidationError(f"unknown field(s): {', '.join(sorted(unknown))}")

    missing = COMMON_REQUIRED - set(event)
    if missing:
        raise TraceValidationError(f"missing required field(s): {', '.join(sorted(missing))}")

    version = event["schema_version"]
    if isinstance(version, bool) or not isinstance(version, int) or version != SCHEMA_VERSION:
        raise TraceValidationError(
            f"'schema_version' must equal supported version {SCHEMA_VERSION}"
        )

    _require_nonempty_string(event, "event_id")
    _require_nonempty_string(event, "session_id")
    _require_nonnegative_int(event, "timestamp_ns")

    event_type = event["event_type"]
    if not isinstance(event_type, str) or event_type not in EVENT_REQUIRED:
        raise TraceValidationError(
            f"'event_type' must be one of: {', '.join(EVENT_REQUIRED)}"
        )

    missing_event_fields = EVENT_REQUIRED[event_type] - set(event)
    if missing_event_fields:
        raise TraceValidationError(
            f"{event_type!r} missing required field(s): "
            f"{', '.join(sorted(missing_event_fields))}"
        )

    for field in OPTIONAL_COMMON:
        _optional_string(event, field)

    for field in ("pipeline_key", "frame_id"):
        if field in event:
            _require_nonempty_string(event, field)

    for field in ("compile_duration_ns", "frame_duration_ns"):
        if field in event:
            _require_nonnegative_int(event, field)

    if "outcome" in event:
        outcome = event["outcome"]
        if not isinstance(outcome, str) or outcome not in OUTCOMES:
            raise TraceValidationError(
                f"'outcome' must be one of: {', '.join(sorted(OUTCOMES))}"
            )
    if "cache_result" in event:
        cache_result = event["cache_result"]
        if not isinstance(cache_result, str) or cache_result not in CACHE_RESULTS:
            raise TraceValidationError(
                f"'cache_result' must be one of: {', '.join(sorted(CACHE_RESULTS))}"
            )

    return dict(event)
