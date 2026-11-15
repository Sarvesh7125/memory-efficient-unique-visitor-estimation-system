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
