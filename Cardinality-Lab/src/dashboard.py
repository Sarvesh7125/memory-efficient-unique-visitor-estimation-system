from pathlib import Path
from time import perf_counter
import pandas as pd
from src.exact import ExactCounter
from src.hyperloglog import HyperLogLog

ROOT = Path(__file__).resolve().parents[1]


def datasets():
    return sorted((ROOT / 'data' / 'benchmark').glob('*.csv')) + sorted((ROOT / 'data' / 'processed').glob('*.csv'))


def reset(source):
    if hasattr(source, 'seek'):
        source.seek(0)
    return source


def columns(source):
    return list(pd.read_csv(reset(source), nrows=0).columns)


def chunks(source, column, size=50000):
    for frame in pd.read_csv(reset(source), usecols=[column], dtype='string', keep_default_na=False, chunksize=size):
        ids = frame[column].str.strip()
        yield ids[ids.notna() & ~ids.str.lower().isin(['', 'null', 'nan', '<other>'])]


def analyze(source, column, p=12, compare=True):
    hll = HyperLogLog(p)
    exact = ExactCounter() if compare else None
    events = 0
    hll_time = exact_time = 0.0
    for ids in chunks(source, column):
        events += len(ids)
        start = perf_counter()
        hll.update(ids)
        hll_time += perf_counter() - start
        if exact is not None:
            start = perf_counter()
            exact.update(ids)
            exact_time += perf_counter() - start
    start = perf_counter()
    estimate = hll.estimate()
    hll_time += perf_counter() - start
    actual = exact.estimate() if exact is not None else None
    em = exact.memory_bytes() if exact is not None else None
    hm = hll.memory_bytes()
    return dict(events=events, precision=p, exact_count=actual, hll_estimate=estimate,
                absolute_error_pct=abs(estimate-actual)/actual*100 if actual else None,
                theoretical_rse_pct=hll.theoretical_rse*100, exact_retained_bytes=em,
                hll_retained_bytes=hm, hll_register_bytes=hll.payload_bytes(),
                memory_ratio=em/hm if em is not None else None,
                memory_savings_pct=(1-hm/em)*100 if em else None,
                exact_ms=exact_time*1000 if compare else None, hll_ms=hll_time*1000)


def merge_demo(a, b, overlap, p=12):
    if not 0 <= overlap <= min(a,b):
        raise ValueError('Invalid overlap')
    left = HyperLogLog(p).update(str(i) for i in range(a))
    right = HyperLogLog(p).update(str(i) for i in range(a-overlap,a-overlap+b))
    x,y = left.estimate(),right.estimate()
    left.merge(right)
    direct = HyperLogLog(p).update(str(i) for i in range(a+b-overlap))
    return dict(left_estimate=x, right_estimate=y, merged_estimate=left.estimate(),
                exact_union=a+b-overlap, direct_estimate=direct.estimate(),
                identical_registers=left.registers == direct.registers)


def benchmark_dir():
    local = ROOT / 'results' / 'phase_5_6'
    reference = ROOT / 'results' / 'phase_5_6_reference'
    for folder in (local,reference):
        if all((folder / f).exists() for f in ('scalability.csv','precision_summary.csv','precision_trials.csv')):
            return folder
    return None
