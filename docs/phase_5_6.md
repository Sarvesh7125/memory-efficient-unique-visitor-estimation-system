# Phase 5–6: Performance Evaluation and Visualization

## Installation and execution

Extract this patch directly into the existing project root. No new dependencies or datasets are required. From PowerShell in the project root:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m scripts.run_benchmarks
.\.venv\Scripts\python.exe -m scripts.plot_benchmarks
```

Local results go to `results/phase_5_6/` and local graphs to `visualizations/phase_5_6/`. The bundled reference directories have measurements from the execution environment, not your PC. UCI is automatically included if `data/processed/uci_events.csv` exists; it is checked against 24,026 distinct session IDs. The reference run lacks UCI because the locally acquired file was not supplied. Sessions are not people.

For a quicker smoke test use `-m scripts.run_benchmarks --sizes 1000 10000 --repeats 2 --trials 3 --cardinality 1000 --output results/smoke` and plot with `-m scripts.plot_benchmarks --results results/smoke --output visualizations/smoke`.

## Methodology

The existing ExactCounter and HyperLogLog implementations are unchanged. For each dataset, both receive the same preloaded valid ID sequence, preserving repetition. Five timed runs per algorithm include construction, updates and final estimate; CSV parsing, memory measurement, and garbage collection are excluded. Median runtime is reported, along with raw samples. Set always runs first; this fixed order may influence timings. Timings are machine-dependent.

Peak traced allocation is measured in a separate run using tracemalloc, excluding preloaded input strings and not measuring process RSS or native allocations. Retained size uses the existing memory_bytes methods, which estimate the object graph including referenced distinct strings for the set. Therefore retained size can exceed incremental peak allocation; these are different measures. The input list is deliberately shared for benchmarking fairness, not a bounded-memory end-to-end pipeline. The HLL data structure itself is fixed-size at a fixed precision and can consume the existing chunked iterator directly in production. Python object overhead varies by runtime.

Precision experiment: 20 independently salted deterministic ID sets of 25,000 distinct IDs, each tested at p=8,10,12,14,16. This yields 100 observations. Timing repetitions are not independent accuracy trials because HLL is deterministic. Statistics include signed bias, mean absolute relative error, sample standard deviation, relative RMSE and maximum absolute error. The theoretical RSE is a standard deviation approximation, not an error bound. Precision experiment results are conditional on the test cardinality. The merge demo checks register equality against direct union processing.

## Outputs

- scalability.csv/json: timing samples, median times, cardinalities, errors, retained and peak memory, reduction ratio.
- precision_trials.csv/json: per-trial estimates and errors.
- precision_summary.csv/json: grouped descriptive statistics.
- metadata.json: runtime environment and measurement scope.
- merge.json: union verification.
- Eight PNG figures: timing, memory, cardinality, error, precision, memory/accuracy, error distribution, memory reduction.

## Reference findings

At one million synthetic events, 250,000 exact distinct IDs were estimated as 245,262.78 (1.895% absolute error). The retained set size was about 20.29 MiB versus 4.25 KiB for HLL, a roughly 4,888-fold reduction. HLL was slower than exact counting in all four cases in this pure Python implementation, reflecting hashing and rank-update overhead. Its advantage is retained memory rather than latency. Higher precision reduced observed mean absolute error across the independent trials, at the cost of more registers. Do not use reference timing as a measurement of the local machine; rerun before submitting.
