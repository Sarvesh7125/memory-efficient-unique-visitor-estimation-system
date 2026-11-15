# Memory-Efficient Unique Visitor Estimation System

## Problem and objectives
Estimate distinct visitor identifiers from large event streams without retaining every identifier. Compare exact Python Set against custom HyperLogLog under identical workloads. Quantify runtime, memory, estimation error and scalability, and deliver a Streamlit prototype.

## Design
CSV → validation/normalization → chunked ID stream → set or HLL → metrics → plots/dashboard. Planned HLL: stable 64-bit BLAKE2b hash, p-bit index, bytearray registers, leading-zero ranks, harmonic estimator and small-range correction. Default p=12; test p=8,10,12,14,16. Approximate relative standard error 1.04/sqrt(2**p). Optional merge via register-wise maximum.

## Nine phases
1. Setup, requirements, problem statement — delivered.
2. Dataset scripts, synthetic datasets, source documentation — delivered; real acquisition pending user network/export.
3. HLL and exact baseline — pending.
4. Algorithm correctness tests — pending (data pipeline tests delivered).
5. Benchmarks — pending; sizes 1K, 10K, 100K, 1M; repeat timing and report median; measure retained state separately from input and process overhead; multiple seeds for error.
6. Plots — pending; runtime, memory, actual vs estimate, precision error, memory-accuracy.
7. Streamlit — pending; upload, ID column, precision, metrics, export.
8. Final report — pending; source, methods, results, limitations.
9. Demo/viva — pending.

## Assessment mapping
Problem/design (2): this document and rationale. Implementation (3): phases 3–4 and 7. Performance (2): phase 5. Results (1): phases 6 and 8. Demonstration (2): phases 7 and 9.

## Complexity targets
Exact set: expected O(1) insertion, O(U) retained storage. HLL: fixed O(2^p) state, O(1) update for fixed hash width, O(2^p) estimation. Do not claim HLL faster: hashing in Python may cost more than a built-in set. Accuracy uses absolute percentage error, undefined at zero actual count (report separately).
