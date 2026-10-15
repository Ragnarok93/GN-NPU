# GN-NPU

Research and tooling for predictive graphics optimization in GameNative/DXVK,
starting with trace-driven pipeline preparation and shader-compilation reduction.

## Principle

The first goal is to predict useful preparation work from observed runtime
behavior, not to move Vulkan command submission or synchronization onto an NPU.

Predictions are advisory. The graphics runtime remains responsible for execution,
synchronization, resource lifetimes, and safe fallback behavior.

## Milestones

1. Define a versioned trace schema and collect representative runtime events.
2. Parse and normalize logs into reproducible datasets.
3. Establish heuristic baselines before training learned models.
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

## Data policy

Do not commit raw gameplay logs, shader/pipeline caches, private captures,
credentials, or trained model binaries. Keep small synthetic fixtures in tests.
Document provenance, build identity, device/driver details, and collection
conditions for every dataset used in evaluation.

## Current status

Scaffold stage. No trained model, validated predictor, runtime integration, or
on-device performance improvement is claimed.
