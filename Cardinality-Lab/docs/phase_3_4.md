# Phase 3 & 4 — Algorithms and verification

## Installation
Extract the patch directly into the existing project root (the folder containing `src`, `data`, and `.venv`). No new dependencies or dataset downloads are needed. All files in the patch are additions.

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m scripts.verify_algorithms
.\.venv\Scripts\python.exe -m scripts.verify_algorithms --input data/processed/uci_events.csv --expected 24026 --output results/phase_3_4_uci.json
```

The default command writes results/phase_3_4_local.json. The real-data command verifies the exact count against the locally reported 24,026 sessions; this file was not available in the build environment. Session IDs are not individual people.

## Implementation
`ExactCounter` stores distinct strings in a Python set. `HyperLogLog` uses deterministic BLAKE2b 64-bit hashes, p high bits for register selection, and leading-zero rank in the remaining bits. Each byte register retains its maximum rank. The estimate uses the harmonic mean with conventional alpha constants and linear counting for small cardinalities. Default p=12 gives 4096 bytes of register payload and theoretical relative standard error 1.625%; this is not an absolute error bound. No extreme-cardinality correction is implemented: the intended datasets are far below the 64-bit hash saturation range. Neither class requires a third-party algorithm library.

Both classes expose add, update, estimate, payload_bytes and memory_bytes. HLL merge mutates the receiving sketch and leaves the other unchanged; equal precision and identical hash conventions are required. Register-wise maxima reproduce the sketch built over the union, even for overlapping input streams.

## Complexity
For n events and u distinct IDs, exact counting consumes O(u) retained entries, with expected O(1) set insertion and O(1) count retrieval. HLL uses O(2^p) registers, O(1) update with respect to n (hashing cost depends on ID length), O(2^p) estimation and merging. CSV input is streamed using the original chunk reader.

## Memory methodology
memory_bytes sums shallow object, instance dictionary and backing container sizes, plus set-held strings or HLL precision metadata. It is an approximate retained-object footprint, not peak process memory or allocator RSS. Shared objects may be counted; Python implementation and dictionary allocation can change measurements. HLL register payload alone is exactly 4096 bytes at p=12. Exact payload includes Python string object sizes, not just encoded text. CSV buffers and temporary hash objects are excluded. The verification command runs both counters on the same stream; independent timing and peak allocation experiments belong to Phase 5.

## Validation
28 pytest cases passed in the build environment, including the original four pipeline tests. Synthetic files totaling 1,111,000 events were processed successfully. See results/phase_3_4_synthetic.json for measured counts and retained footprint estimates. Accuracy tests use an empirical tolerance rather than a guaranteed HLL error bound. No UCI measurement is claimed until the local command is run.
