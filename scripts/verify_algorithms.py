import argparse
import json
from pathlib import Path
from src.exact import ExactCounter
from src.hyperloglog import HyperLogLog
from src.paths import ROOT
from src.preprocessing import iter_visitor_ids


def compare(path, p=12):
    exact = ExactCounter()
    hll = HyperLogLog(p)
    events = 0
    for visitor_id in iter_visitor_ids(path):
        exact.add(visitor_id)
        hll.add(visitor_id)
        events += 1
    actual = exact.estimate()
    estimate = hll.estimate()
    exact_memory = exact.memory_bytes()
    hll_memory = hll.memory_bytes()
    return {'dataset': Path(path).name, 'identifier_kind': 'session ID (not person)' if Path(path).name == 'uci_events.csv' else 'distinct supplied IDs', 'events': events, 'precision': p, 'exact_count': actual, 'hll_estimate': estimate, 'absolute_error_pct': abs(estimate - actual) / actual * 100 if actual else None, 'theoretical_rse_pct': hll.theoretical_rse * 100, 'exact_retained_bytes': exact_memory, 'hll_retained_bytes': hll_memory, 'hll_register_bytes': hll.payload_bytes(), 'memory_ratio': exact_memory / hll_memory}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, action='append')
    parser.add_argument('--precision', type=int, default=12)
    parser.add_argument('--expected', type=int)
    parser.add_argument('--output', type=Path, default=ROOT / 'results' / 'phase_3_4_local.json')
    args = parser.parse_args()
    paths = args.input or sorted((ROOT / 'data' / 'benchmark').glob('events_*.csv'))
    if args.expected is not None and len(paths) != 1:
        parser.error('--expected requires exactly one input')
    results = [compare(path, args.precision) for path in paths]
    if args.expected is not None and results[0]['exact_count'] != args.expected:
        raise SystemExit(f"Expected {args.expected}, got {results[0]['exact_count']}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2), encoding='utf-8')
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
