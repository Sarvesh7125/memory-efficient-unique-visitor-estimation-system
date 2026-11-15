# Cardinality Lab — Complete Project Master Context

**Academic title:** Memory-Efficient Unique Visitor Estimation System  
**Subject:** SDS mini project  
**Status:** All nine development phases completed; dashboard launch confirmed by the student.  
**Purpose of this file:** A self-contained technical handover for future development, report writing, viva preparation, portfolio publishing and AI coding assistants. The actual implementation files remain the source of truth. This document records the completed project, not a proposal.

## 1. Problem, scope and goals
Website event logs contain repeated identifiers. Counting events does not count unique visitors. The conventional exact solution retains every distinct ID in a Python set. HyperLogLog (HLL) estimates cardinality using a fixed number of registers, trading exactness for smaller retained state. The system compares both under identical workloads and provides an interactive dashboard. No external HLL library is used. IDs are supplied identifiers, not verified individuals. The real UCI dataset specifically measures sessions.

## 2. Assessment and completion history
| Phase | Completed work |
|---|---|
| 1 | Modular structure, requirements, initial problem statement |
| 2 | Synthetic generation, CSV normalization, UCI download and local processing |
| 3 | ExactCounter and HyperLogLog from scratch; merge and memory methods |
| 4 | Correctness tests, synthetic verification, local UCI verification |
| 5 | Repeated timing, peak and retained memory, precision trials, local benchmark |
| 6 | Eight Matplotlib figures generated locally |
| 7 | Six-section Streamlit dashboard; student confirmed local completion |
| 8 | 15-page DOCX report, 12-slide PPTX, architecture/flow diagrams |
| 9 | 45 viva answers, demonstration script, rubric checklist |

Rubric (10 marks): problem/design 2; implementation 3; performance/scalability 2; results/documentation 1; demonstration/viva 2. All requirements have supporting deliverables; marks are not guaranteed.

## 3. Technology and architecture
Python 3.11+; pandas; NumPy; Matplotlib; Streamlit; Plotly; pytest; standard library hashlib, math, sys, tracemalloc, time, pathlib and argparse. No database, remote service, training model or deep learning component is required. The app runs locally. Architecture: CSV → normalized ID stream → exact set and/or HLL → metrics → CSV/JSON and plots/dashboard. The live HLL-only mode avoids storing the complete set of IDs. The benchmark deliberately preloads IDs to isolate algorithm work.

## 4. Source structure and contracts

- `.streamlit/config.toml`
- `README.md`
- `app.py`
- `benchmarks/README.md`
- `data/processed/README.md`
- `data/raw/README.md`
- `docs/dataset.md`
- `docs/ga4_export.sql`
- `docs/phase_3_4.md`
- `docs/phase_5_6.md`
- `docs/phase_7.md`
- `docs/project_plan.md`
- `requirements-dashboard.txt`
- `requirements.txt`
- `scripts/__init__.py`
- `scripts/generate_benchmarks.py`
- `scripts/plot_benchmarks.py`
- `scripts/prepare_real.py`
- `scripts/run_benchmarks.py`
- `scripts/verify_algorithms.py`
- `src/__init__.py`
- `src/dashboard.py`
- `src/exact.py`
- `src/hyperloglog.py`
- `src/paths.py`
- `src/preprocessing.py`
- `tests/test_algorithms.py`
- `tests/test_benchmarks.py`
- `tests/test_dashboard.py`
- `tests/test_data.py`

`ExactCounter` and `HyperLogLog` expose `add(str)`, `update(iterable)`, `estimate()`, `payload_bytes()`, `memory_bytes()`. `update` returns self. HLL additionally exposes `p`, `m`, `registers`, `theoretical_rse` (fraction), `merge(other)` (in-place, returns self). Allowed integer precision is 4–18, default 12; mismatched precision raises ValueError; non-string IDs raise TypeError. UI helpers reside in `src/dashboard.py`. The canonical benchmark artifact names are `scalability`, `precision_trials`, `precision_summary` (CSV and JSON), `metadata.json`, `merge.json`; local results preferred over reference outputs. Paths are relative to project root.

## 5. Algorithm implementation and complexity
BLAKE2b with digest_size=8 produces a deterministic unsigned big-endian 64-bit integer h. With q=64-p, index=h>>q; remainder=h & ((1<<q)-1); rank=q-remainder.bit_length()+1. For every event, update register[index] to max(old,rank). Identical IDs produce identical updates. The raw estimate is alpha*m²/sum(2^(-register)). Alpha is 0.673, 0.697, 0.709 for m=16,32,64; otherwise 0.7213/(1+1.079/m). If raw <=2.5*m and V empty registers remain, use m*ln(m/V). Empty input yields zero. No extreme-cardinality correction is implemented. Merge takes elementwise max of compatible registers and does not mutate the donor. Theoretical relative standard error is 1.04/sqrt(m), not a guaranteed bound. For p=12, m=4096, register payload 4096 bytes and RSE 1.625%. Exact set expected O(N) time, O(U) retained entries; HLL O(N+m) time and O(m) storage for bounded length IDs; estimate and merge O(m). Hash costs depend on identifier length.

## 6. Dataset documentation and acquisition

# Dataset documentation

## Real source A: UCI Clickstream Data for Online Shopping
Source: https://archive.ics.uci.edu/dataset/553/clickstream+data+for+online+shopping
DOI: https://doi.org/10.24432/C5QK7X
Citation: Clickstream Data for Online Shopping [Dataset]. (2019). UCI Machine Learning Repository.
License: CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/).
Published size: 165,474 records, 14 features; April–August 2008. Actual local counts are not verified until the acquisition script runs. The download was blocked by DNS in the build environment; no actual real records are bundled.
Each row is a click. The identifier is a session ID, not a stable person ID. The project labels results from this source as distinct sessions. Transformations: date assembled from year/month/day (no clock time supplied), product code converted to a constructed path, event type set to click. Duplicate visits are preserved.

## Realistic user-level alternative: Google GA4 obfuscated ecommerce sample
Source: https://developers.google.com/analytics/bigquery/web-ecommerce-demo-dataset
Public BigQuery dataset, Nov 2020–Jan 2021. Export query in ga4_export.sql selects one week; actual row count is recorded after export. Requires Google Cloud/BigQuery access; no export is bundled. Pseudonymous user IDs approximate visitors, not people. Google notes obfuscation and placeholder values. Use subject to source terms; do not assume a redistribution license.

## Synthetic benchmark source
Generated locally with NumPy seed 42; exactly 25% distinct IDs per file. Every intended ID occurs at least once, remaining events sample uniformly from those IDs and are shuffled. Independent sizes (not nested); timestamps are sequential synthetic values, and pages/events sampled independently (no realistic funnel implied). Source and exact counts in data/benchmark/manifest.json. These are not real logs.

## Canonical schema
visitor_id (string), timestamp (source date or timestamp), page_url (observed or constructed), event_type (string). Blank and placeholder IDs are rejected; repeats preserved. ID strings are trimmed but not converted to integers. Missing timestamps rejected by normalization; non-UCI timestamp strings are retained as supplied, not comprehensively validated.


**Local update:** The UCI acquisition completed successfully on the student's laptop. 165,474 raw and valid rows, zero removed, 24,026 distinct session IDs. Source ZIP `uci_clickstream.zip`; processed `uci_events.csv`. The real file is not present in the build environment; the local benchmark files and screenshots establish the counts. GA4 is an optional alternative and was not used in the measured experiments. Synthetic generated 1,111,000 total events across independent sizes, not a count of unique people. Source manifest:
```json
[
  {
    "file": "events_1000.csv",
    "events": 1000,
    "distinct_ids": 250,
    "seed": 42,
    "target_ratio": 0.25,
    "bytes": 46003,
    "source": "synthetic"
  },
  {
    "file": "events_10000.csv",
    "events": 10000,
    "distinct_ids": 2500,
    "seed": 42,
    "target_ratio": 0.25,
    "bytes": 468751,
    "source": "synthetic"
  },
  {
    "file": "events_100000.csv",
    "events": 100000,
    "distinct_ids": 25000,
    "seed": 42,
    "target_ratio": 0.25,
    "bytes": 4789266,
    "source": "synthetic"
  },
  {
    "file": "events_1000000.csv",
    "events": 1000000,
    "distinct_ids": 250000,
    "seed": 42,
    "target_ratio": 0.25,
    "bytes": 48896646,
    "source": "synthetic"
  }
]
```

## 7. Experimental methodology and actual results
Five repeated timed runs per algorithm per dataset; median reported. Timing includes construction, insertions and estimate, excludes CSV loading, garbage collection and tracing. Exact runs first, which may introduce order effects. Separate peak traced allocation via tracemalloc excludes preloaded input strings; not process RSS or native allocation. Retained size is approximate sum of Python object sizes including referenced set strings. These two memory measures are not interchangeable. Signed percentage error = 100*(estimate-actual)/actual, absolute error = absolute value; undefined when actual is zero. Memory ratio = exact retained / HLL retained, savings = 100*(1-HLL/exact). 20 independently salted deterministic ID sets of 25,000 distinct IDs each, tested at five precisions (100 observations); repeated timing on the same IDs is not an independent error trial. RMSE is square root of mean squared signed percentage errors. Local results below are from uploaded `results.zip`, not reference timings.

### Environment metadata
```json
{
  "python": "3.11.0",
  "platform": "Windows-10-10.0.26300-SP0",
  "repeats": 5,
  "precision_trials": 20,
  "seed": 42,
  "uci_included": true,
  "timing_scope": "algorithm construction, insertion and final estimate; excludes CSV loading and memory instrumentation",
  "peak_scope": "tracemalloc Python allocations during algorithm run; input strings preloaded and excluded; not process RSS",
  "retained_scope": "estimated retained object size including references to visitor strings for set"
}
```

### Local scalability and accuracy
| Dataset | Events | Exact | HLL (raw estimate) | Absolute error % | Set median ms | HLL median ms |
|---|---:|---:|---:|---:|---:|---:|
| events_1000 | 1000 | 250 | 251.569741 | 0.627896 | 0.0854 | 0.9195 |
| events_10000 | 10000 | 2500 | 2444.742307 | 2.210308 | 0.6802 | 8.0903 |
| events_100000 | 100000 | 25000 | 25063.220765 | 0.252883 | 10.4138 | 76.6716 |
| events_1000000 | 1000000 | 250000 | 245262.781699 | 1.894887 | 229.8959 | 816.4805 |
| uci_events | 165474 | 24026 | 24034.177659 | 0.034037 | 11.2224 | 108.3936 |

### Local memory (bytes)
| Dataset | Set retained | HLL retained | Set peak traced | HLL peak traced | Ratio | Savings % |
|---|---:|---:|---:|---:|---:|---:|
| events_1000 | 22860 | 4521 | 10784 | 5354 | 5.0564 | 80.223097 |
| events_10000 | 275442 | 4465 | 164328 | 5291 | 61.6891 | 98.378969 |
| events_100000 | 3561474 | 4409 | 2621872 | 5228 | 807.7736 | 99.876203 |
| events_1000000 | 23277882 | 4361 | 12583288 | 5173 | 5337.7395 | 99.981265 |
| uci_events | 3383802 | 4361 | 2621784 | 5170 | 775.9234 | 99.871121 |

### Precision experiment (full summary CSV)
```csv
precision,trials,actual,mean_signed_error_pct,mean_absolute_error_pct,std_signed_error_pct,rmse_pct,max_absolute_error_pct,register_bytes,theoretical_rse_pct
8,20,25000,3.59889706242362,4.827935918017202,5.087017441624576,6.126656444974239,14.712278199528125,256,6.5
10,20,25000,1.9528920112161423,2.5501229103181196,2.462218202263667,3.094055552063089,6.398632667904021,1024,3.25
12,20,25000,0.40807858207534153,1.344447523311639,1.680662010777205,1.6881711062255556,3.6434709551705455,4096,1.625
14,20,25000,0.107697491936772,0.5982826193101639,0.762137936216587,0.7506066026214568,1.7217453194169212,16384,0.8125
16,20,25000,-0.010027588721654317,0.19100185126428695,0.24089990045155116,0.23501420482868593,0.5084771151211462,65536,0.40625
```

### Distributed merge result
```json
{
  "actual_union": 15000,
  "merged_estimate": 15008.868498974643,
  "direct_estimate": 15008.868498974643,
  "identical_registers": true
}
```

### Earlier independent UCI verification (different object overhead)
```json
[
  {
    "dataset": "uci_events.csv",
    "identifier_kind": "session ID (not person)",
    "events": 165474,
    "precision": 12,
    "exact_count": 24026,
    "hll_estimate": 24034.177659333956,
    "absolute_error_pct": 0.034036707458405056,
    "theoretical_rse_pct": 1.625,
    "exact_retained_bytes": 3384018,
    "hll_retained_bytes": 4561,
    "hll_register_bytes": 4096,
    "memory_ratio": 741.9465029598772
  }
]
```

The headline result is 5,337.74× retained-memory ratio at 1M events, with 1.895% error and 99.9813% savings. UCI error is 0.03404%; the final benchmark ratio is 775.92×, whereas the earlier verification reported 741.95× due to measured object-size differences across runs. Set was faster in all measured local cases: do not claim a speedup. Precision 12 balances fixed state and empirical accuracy. The single favorable UCI error is not a guarantee. Hardware specifications were not supplied.

## 8. Graphs and output artifacts

- `01_execution_time.png` — locally generated Matplotlib figure
- `02_memory_comparison.png` — locally generated Matplotlib figure
- `03_cardinality.png` — locally generated Matplotlib figure
- `04_estimation_error.png` — locally generated Matplotlib figure
- `05_precision_error.png` — locally generated Matplotlib figure
- `06_memory_accuracy.png` — locally generated Matplotlib figure
- `07_error_distribution.png` — locally generated Matplotlib figure
- `08_memory_savings.png` — locally generated Matplotlib figure

Raw per-trial observations and timing samples remain in the CSV/JSON evidence; do not replace them with rounded report numbers. Diagrams: architecture, data_flow, hll_flow in PNG/SVG. Final report and slides are in the submission package. Dashboard screenshots were not supplied; no actual screenshots were fabricated.

## 9. Dashboard design and behavior
# Phase 7 — Cardinality Lab dashboard

Extract the patch into the existing project root, preserving the `.streamlit` folder. It adds files only; previous algorithms, datasets, benchmark outputs and virtual environment are unchanged.

## Windows PowerShell

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dashboard.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open the local URL printed by Streamlit (normally http://localhost:8501).

## Demonstration

- Overview: inspect the largest benchmark and retained memory.
- Live Visitor Estimation: select `data/processed/uci_events.csv`, use `visitor_id`, p=12 and enable exact comparison. Expect exact 24,026 and estimated approximately 24,034 based on prior local verification. Select session IDs as identifier meaning. Try HLL-only mode and a custom CSV. Results exports refer to the last completed run.
- Performance Benchmarking: filter datasets and compare timing, memory and error. Local benchmark CSVs are preferred; reference results from another machine are labeled if local results are missing.
- Precision Analysis: inspect 100 observations and theoretical error.
- Distributed Sketch Merging: use 10,000 IDs per source and 5,000 shared IDs. The actual union is 15,000; merged registers must equal direct union registers.
- Dataset Explorer: inspect first 1,000 rows and preview-only distributions.

The live page processes IDs in chunks, but Streamlit uploads may be held in memory. Exact comparison retains IDs and is optional. Live timings exclude parsing and are single-run measurements. Benchmark peak memory measures traced allocations, not system RAM. Real UCI IDs refer to sessions, not people. The dashboard does not transmit uploaded CSVs to external services; keep it on localhost for private data.

## Validation

38 automated tests passed in the build environment; app.py and src/dashboard.py compiled successfully. Streamlit was not installed in that environment and installation was unavailable, so browser-level UI behavior and local UCI integration remain to be checked on the user's machine. Plotly is the only new dependency relative to the initial requirements.


## 10. Reproduce from a fresh clone (Windows PowerShell)
```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dashboard.txt
.\.venv\Scripts\python.exe -m scripts.generate_benchmarks
.\.venv\Scripts\python.exe -m scripts.prepare_real
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m scripts.verify_algorithms
.\.venv\Scripts\python.exe -m scripts.verify_algorithms --input data/processed/uci_events.csv --expected 24026 --output results/phase_3_4_uci.json
.\.venv\Scripts\python.exe -m scripts.run_benchmarks
.\.venv\Scripts\python.exe -m scripts.plot_benchmarks
.\.venv\Scripts\python.exe -m streamlit run app.py
```
For Linux/macOS use `python3 -m venv .venv` and `.venv/bin/python` instead of the Windows executable. UCI acquisition requires internet; if it fails, place original ZIP at `data/raw/uci_clickstream.zip`. GA4: export SQL in `docs/ga4_export.sql`, use `--source ga4 --input data/raw/ga4.csv`. A fast smoke run: `-m scripts.run_benchmarks --sizes 1000 10000 --repeats 2 --trials 3 --cardinality 1000 --output results/smoke` then `-m scripts.plot_benchmarks --results results/smoke --output visualizations/smoke`. The dashboard normally opens at http://localhost:8501. Build-stage pytest counts: 4 → 28 → 33 → 38; local dashboard confirmed by student; no local pytest screenshot supplied.

## 11. Dependencies (as implemented)
```
pandas>=2.2,<3
numpy>=1.26,<3
matplotlib>=3.8,<4
streamlit>=1.40,<2
pytest>=8,<10
-r requirements.txt
plotly>=5.24,<7
```

## 12. Viva and demo guide (all original questions)
# SDS mini project — viva and demonstration

## 45 questions and answers

1. **What is the problem?** Estimate distinct IDs in large repeated-event logs without retaining all IDs.
2. **What is cardinality?** Number of distinct elements in a collection.
3. **Event count versus cardinality?** Events include repeats; cardinality counts each ID once.
4. **Why use a set as baseline?** It provides exact distinct counts and a conventional comparison.
5. **What is HLL?** A probabilistic cardinality sketch using hashed values and maximum ranks.
6. **Why hash IDs?** To distribute values approximately uniformly over registers and ranks.
7. **Which hash?** BLAKE2b with an eight-byte digest, interpreted as a 64-bit integer.
8. **Why not Python hash?** Its string hash can vary across processes; reproducible compatible sketches need stable hashing.
9. **What is p?** Number of index bits; it controls register count.
10. **What is m?** 2^p; 4096 at p=12.
11. **How is a register selected?** The high p bits of the hash.
12. **What is rank?** Leading zero count of remaining bits plus one, including the all-zero case.
13. **Why use maximum?** Rare large ranks provide evidence of more diverse hash values.
14. **Why do duplicates not inflate the sketch?** Identical IDs produce identical index and rank; max is idempotent.
15. **What is stored?** One byte per register, plus Python object overhead.
16. **How is cardinality estimated?** Alpha times m squared divided by the sum of 2 raised to negative register values.
17. **Why small-range correction?** Raw HLL has small-cardinality bias; zero registers permit linear counting.
18. **What is linear counting?** m times ln(m/V), where V is number of empty registers.
19. **What happens with empty input?** Linear counting returns zero.
20. **Theoretical RSE?** Approximately 1.04/sqrt(m); 1.625% at p=12.
21. **Is that a maximum error?** No; it is an approximate relative standard deviation.
22. **How does precision affect memory?** Increasing p by one doubles register storage.
23. **How does precision affect expected error?** Increasing p by two approximately halves theoretical RSE.
24. **Set complexity?** Expected O(N) total time and O(U) retained storage for bounded-length IDs.
25. **HLL complexity?** O(N+m) time and O(m) storage; hash cost depends on string length.
26. **Merge complexity?** O(m) time, using register-wise maxima.
27. **Merge requirements?** Same precision and same hash interpretation and algorithm.
28. **Why not add two estimates?** Overlapping IDs would be counted twice.
29. **Local merge evidence?** Exact union 15,000; estimated 15,008.87; identical merged and direct registers.
30. **Real dataset?** UCI online-shopping clickstream, 165,474 events.
31. **Does UCI measure people?** No, it supplies session IDs; 24,026 distinct sessions.
32. **Synthetic dataset?** NumPy seed 42; 1K, 10K, 100K, 1M events, 25% distinct IDs.
33. **Why preserve repeats?** They represent repeated events and test idempotent counting.
34. **Why five runs?** Median reduces sensitivity to occasional timing variations.
35. **What is timed?** Construction, inserts and final estimation; not CSV loading or memory instrumentation.
36. **What is peak memory?** Incremental traced Python allocations from tracemalloc, not process RSS.
37. **What is retained memory?** Approximate size of the surviving counter object graph; set includes referenced strings.
38. **Why can retained memory exceed peak traced allocation?** Input strings existed before tracing but are included in retained-set size.
39. **Which is faster here?** Set: 229.896 ms vs HLL 816.481 ms at 1M events.
40. **Largest memory reduction?** 5,337.74× retained-memory ratio at 1M events; 23,277,882 vs 4,361 bytes.
41. **Largest synthetic error?** 2.2103% at 10K events.
42. **UCI error?** 0.03404%; 24,034.18 estimated vs 24,026 actual.
43. **What does RMSE mean?** Root mean square of signed relative percentage errors over independent ID sets; p=12 gives 1.688%.
44. **Why use HLL-only mode?** Exact comparison retains IDs and defeats the bounded sketch-memory advantage.
45. **Limitations and next steps?** Session IDs are not people, timing is machine-dependent, no total RSS measurement or extreme-cardinality correction. Test diverse workloads and optimized implementations.

## Live demonstration (approximately 5–7 minutes)

- Open the project root; show source, datasets and results directories. Explain problem and baseline.
- Launch: ` .\.venv\Scripts\python.exe -m streamlit run app.py` (PowerShell; omit leading space if desired).
- Overview: describe largest tested dataset and memory benefit, not a speed benefit.
- Live estimation: select UCI CSV, visitor_id, session IDs, p=12, exact comparison. Expect 24,026 exact and about 24,034 estimated. Export results. Toggle HLL-only to explain production mode.
- Upload a tiny CSV with IDs A, B, A, C, B; exact distinct count should be 3. HLL is approximate.
- Benchmarking: demonstrate four synthetic sizes and UCI, using local results. Explain median timing and traced peak.
- Precision: compare p=8 and p=16; explain register growth and error distribution.
- Merging: 10,000 per source and 5,000 overlap; exact union 15,000; merged/direct register equality.
- Dataset Explorer: preview records; clarify session/person distinction. Conclude with limitations.

## Submission checklist (10 marks)

- [ ] Problem definition/design (2): objectives, dataset schema, HLL selection, architecture.
- [ ] Implementation/functionality (3): custom code, exact baseline, pytest output, working dashboard.
- [ ] Performance/scalability (2): local CSVs, five repeats, four synthetic sizes + real data, memory and error metrics.
- [ ] Results/documentation (1): report, graphs and interpretation.
- [ ] Demo/viva (2): rehearse commands, HLL update and merge, Explain why set is faster.
- [ ] Replace student name, guide, institution, year placeholders; insert real dashboard screenshots if required.
- [ ] Verify all files on the submission machine; do not submit .venv or private CSVs.


## 13. Limitations and future work
Session IDs do not measure unique people. Synthetic event structure is simplified. HLL errors vary and may exceed RSE. No extreme range correction, deletion support, sliding window or production-scale distributed service is implemented. Timing is hardware/runtime-dependent, fixed execution order can bias results, and traced allocation is not RSS. Uploads may be held in Streamlit memory. Suggested extensions (not implemented): native/vectorized hashing, independent workload distributions, end-to-end streaming RSS tests, time-partitioned sketches, persistent sketch serialization, and pseudonymous GA4 data analysis.

## 14. GitHub publication workflow
Suggested repository: `memory-efficient-unique-visitor-estimation-system`. Description: From-scratch HyperLogLog cardinality estimation with exact-count baseline, reproducible benchmarks and an interactive Streamlit dashboard. Publish source, tests, scripts, requirements, configuration, documentation, diagrams, and aggregated benchmark evidence. Keep local `.venv`, caches, `.env`, credentials, private uploads and raw/processed data out of Git; synthetic datasets can be regenerated from the seed and included manifest. Do not commit private personal information or unreviewed academic cover details. UCI source attribution is in docs/dataset.md; GA4 redistribution not assumed. No code license was selected; choose one only if authorized. A GitHub-ready archive is a clean reconstruction from available phase artifacts and uploaded evidence, not a copy of unknown local edits.

Create an empty repository at https://github.com/new (no autogenerated README if using these commands). In the extracted repository folder:
```powershell
git init
git add .
git status --short
git commit -m "Initial release: Cardinality Lab"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```
If a repository already exists and is not empty, clone it and integrate files on a new branch rather than force-push. Authenticate using Git Credential Manager or GitHub CLI; never share a password/token in chat. Verify README, source and evidence after push. No remote upload has occurred at the time of writing.

## 15. Source and evidence provenance
This context was consolidated from the Phase 1–7 project source, its phase documentation, the original user-reported UCI preparation and verification, the uploaded Windows local results and visualizations, and the final submission package. Project-specific source code and raw experiments remain authoritative. Prior phase READMEs may describe historical pending tasks; the completed status in this file supersedes those old status descriptions. Final report and presentation cover placeholders must be completed locally.

References: UCI dataset DOI https://doi.org/10.24432/C5QK7X; Google GA4 public sample https://developers.google.com/analytics/bigquery/web-ecommerce-demo-dataset; Flajolet et al., *HyperLogLog: the analysis of a near-optimal cardinality estimation algorithm* (2007), https://algo.inria.fr/flajolet/Publications/FlFuGaMe07.pdf.
