import argparse
import gc
import json
import math
import platform
import random
import statistics as st
import time
import tracemalloc
from pathlib import Path

import pandas as pd
from src.exact import ExactCounter
from src.hyperloglog import HyperLogLog
from src.paths import ROOT
from src.preprocessing import iter_visitor_ids


def measure(factory, ids, repeats):
    times = []
    for _ in range(repeats):
        gc.collect()
        start = time.perf_counter()
        counter = factory().update(ids)
        estimate = counter.estimate()
        times.append(time.perf_counter() - start)
        del counter
    gc.collect()
    tracemalloc.start()
    try:
        counter = factory().update(ids)
        counter.estimate()
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return dict(estimate=estimate, median_ms=1000 * st.median(times), times_ms=[1000 * t for t in times], peak_bytes=peak, retained_bytes=counter.memory_bytes())


def signed_error(estimate, actual):
    return 100 * (estimate - actual) / actual if actual else 0.0


def benchmark(path, repeats, p=12, expected=None):
    ids = list(iter_visitor_ids(path))
    exact = measure(ExactCounter, ids, repeats)
    hll = measure(lambda: HyperLogLog(p), ids, repeats)
    actual = exact['estimate']
    if expected is not None and actual != expected:
        raise ValueError(f'{path}: expected {expected}, got {actual}')
    return dict(dataset=path.stem, identifier_kind='session ID (not person)' if path.name == 'uci_events.csv' else 'distinct supplied IDs', events=len(ids), precision=p, exact_count=actual, hll_estimate=hll['estimate'], signed_error_pct=signed_error(hll['estimate'], actual), absolute_error_pct=abs(signed_error(hll['estimate'], actual)), theoretical_rse_pct=100 * HyperLogLog(p).theoretical_rse, exact_median_ms=exact['median_ms'], hll_median_ms=hll['median_ms'], exact_times_ms=exact['times_ms'], hll_times_ms=hll['times_ms'], exact_peak_bytes=exact['peak_bytes'], hll_peak_bytes=hll['peak_bytes'], exact_retained_bytes=exact['retained_bytes'], hll_retained_bytes=hll['retained_bytes'], hll_register_bytes=1 << p, memory_ratio=exact['retained_bytes']/hll['retained_bytes'], memory_savings_pct=100*(1-hll['retained_bytes']/exact['retained_bytes']))


def precision_trials(trials, cardinality, precisions, seed=42):
    rng = random.Random(seed)
    rows = []
    for trial in range(trials):
        salt = f'{rng.getrandbits(64):016x}'
        ids = [f'{salt}:{i}' for i in range(cardinality)]
        for p in precisions:
            sketch = HyperLogLog(p).update(ids)
            estimate = sketch.estimate()
            error = signed_error(estimate, cardinality)
            rows.append(dict(trial=trial+1, precision=p, actual=cardinality, estimate=estimate, signed_error_pct=error, absolute_error_pct=abs(error), register_bytes=sketch.payload_bytes(), retained_bytes=sketch.memory_bytes(), theoretical_rse_pct=100*sketch.theoretical_rse))
    return rows


def summarize(rows):
    output = []
    for p in sorted({r['precision'] for r in rows}):
        group = [r for r in rows if r['precision']==p]
        errors = [r['signed_error_pct'] for r in group]
        output.append(dict(precision=p, trials=len(group), actual=group[0]['actual'], mean_signed_error_pct=st.mean(errors), mean_absolute_error_pct=st.mean(map(abs, errors)), std_signed_error_pct=st.stdev(errors) if len(errors)>1 else 0.0, rmse_pct=math.sqrt(st.mean(e*e for e in errors)), max_absolute_error_pct=max(map(abs,errors)), register_bytes=group[0]['register_bytes'], theoretical_rse_pct=group[0]['theoretical_rse_pct']))
    return output


def merge_demo(p=12):
    a = [f'user_{i}' for i in range(10000)]
    b = [f'user_{i}' for i in range(5000,15000)]
    left, right = HyperLogLog(p).update(a), HyperLogLog(p).update(b)
    merged = left.merge(right)
    direct = HyperLogLog(p).update(a+b)
    assert merged.registers == direct.registers
    return dict(actual_union=len(set(a+b)), merged_estimate=merged.estimate(), direct_estimate=direct.estimate(), identical_registers=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repeats', type=int, default=5)
    parser.add_argument('--trials', type=int, default=20)
    parser.add_argument('--cardinality', type=int, default=25000)
    parser.add_argument('--sizes', nargs='+', type=int, default=[1000,10000,100000,1000000])
    parser.add_argument('--output', type=Path, default=ROOT/'results'/'phase_5_6')
    args = parser.parse_args()
    if min(args.repeats,args.trials,args.cardinality,*args.sizes)<1:
        parser.error('All numeric arguments must be positive')
    args.output.mkdir(parents=True,exist_ok=True)
    rows = []
    for size in sorted(set(args.sizes)):
        path = ROOT/'data'/'benchmark'/f'events_{size}.csv'
        print(f'Benchmarking {path.name}',flush=True)
        rows.append(benchmark(path,args.repeats,expected=size//4 if size in (1000,10000,100000,1000000) else None))
    uci = ROOT/'data'/'processed'/'uci_events.csv'
    if uci.exists():
        print('Benchmarking UCI',flush=True)
        rows.append(benchmark(uci,args.repeats,expected=24026))
    else:
        print('UCI absent: skipping real-world experiment',flush=True)
    print('Running independent precision trials',flush=True)
    trials = precision_trials(args.trials,args.cardinality,[8,10,12,14,16])
    summary = summarize(trials)
    metadata = dict(python=platform.python_version(),platform=platform.platform(),repeats=args.repeats,precision_trials=args.trials,seed=42,uci_included=uci.exists(),timing_scope='algorithm construction, insertion and final estimate; excludes CSV loading and memory instrumentation',peak_scope='tracemalloc Python allocations during algorithm run; input strings preloaded and excluded; not process RSS',retained_scope='estimated retained object size including references to visitor strings for set')
    for name,data in [('scalability',rows),('precision_trials',trials),('precision_summary',summary)]:
        pd.DataFrame(data).to_csv(args.output/f'{name}.csv',index=False)
        (args.output/f'{name}.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
    (args.output/'metadata.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
    (args.output/'merge.json').write_text(json.dumps(merge_demo(),indent=2),encoding='utf-8')
    print(f'Results: {args.output}',flush=True)


if __name__ == '__main__':
    main()
