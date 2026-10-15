# GN-NPU

Research and tooling for predictive graphics optimization in GameNative/DXVK,
starting with trace-driven pipeline preparation and shader-compilation reduction.

## Principle

The first goal is to predict useful preparation work from observed runtime
behavior, not to move Vulkan command submission or synchronization onto an NPU.

Predictions are advisory. The graphics runtime remains responsible for execution,
synchronization, resource lifetimes, and safe fallback behavior.

## Milestones

1. **Initial contract implemented:** versioned trace schema v1 and synthetic fixture.
2. **Initial ingestion implemented:** strict JSONL validation, normalized rows,
   source-line provenance, and Parquet output.
3. Next: validate against representative real traces and establish a heuristic
   baseline before training learned models.
4. Evaluate on held-out sessions and workloads.
5. Integrate a bounded, optional prewarming experiment into GameNative/DXVK.
6. Evaluate CPU inference before investigating vendor-specific NPU APIs.

## Setup

Requires Python 3.11 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
pytest
ruff check .
```

## Normalize a trace

The checked-in example is synthetic and safe for public CI:

```bash
python scripts/normalize_traces.py tests/fixtures/sample_trace.jsonl data/processed/sample.parquet
```

The parser rejects malformed records, unsupported schema versions, unknown
fields, invalid values, and duplicate event IDs within a session. It preserves
missing values and records the source filename and line number for each event.
See [docs/data-schema.md](docs/data-schema.md) for the v1 contract.

## Data policy

Do not commit raw gameplay logs, shader/pipeline caches, private captures,
credentials, or trained model binaries. Keep small synthetic fixtures in tests.
Document provenance, build identity, device/driver details, and collection
conditions for every dataset used in evaluation.

## Current status

Trace schema v1, JSONL validation, and a Parquet normalization path are
implemented, but still require CI execution and validation against representative
GameNative/DXVK captures. No trained model, validated predictor, runtime
integration, or on-device performance improvement is claimed.
