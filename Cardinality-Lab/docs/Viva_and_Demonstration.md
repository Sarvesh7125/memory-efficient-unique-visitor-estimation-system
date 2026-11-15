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
