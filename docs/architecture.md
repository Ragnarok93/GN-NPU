# GN-NPU architecture

## Data flow

GameNative/DXVK instrumentation
-> versioned events
-> parsers and validation
-> normalized Parquet datasets
-> feature extraction
-> heuristic baseline and learned predictor
-> offline evaluation
-> optional bounded runtime prewarming experiment

## Initial event categories

- Pipeline or shader creation requested/completed
- Compilation duration and outcome
- Pipeline/cache hit or miss where observable
- Frame timing and stutter windows
- Stable pipeline identity and workload context
- Session, application build, driver, device, and schema version

Instrumentation must distinguish unavailable measurements from zero values.
Avoid secrets and unnecessary identifying information.

## Safety boundaries

- Prediction is advisory; the graphics runtime owns execution and synchronization.
- Never block the frame-critical path on model inference.
- Bound queues, memory, prewarming work, and per-frame overhead.
- Preserve a deterministic fallback when prediction is disabled or fails.
- Do not infer causal benefit from correlation alone.
- Compare against no-prediction and simple heuristic baselines.

## Evaluation

Split by gameplay session and preferably by game/workload, not just by event.
This reduces leakage from repeated pipelines and adjacent frames. Measure prediction
quality, frame-time impact, CPU cost, memory use, false positives, and regressions.
