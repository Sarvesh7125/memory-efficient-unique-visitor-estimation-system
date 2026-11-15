import argparse
import json
import numpy as np
import pandas as pd
from src.paths import DATA

def generate(size, seed=42, ratio=0.25):
    if size < 1 or not 0 < ratio <= 1:
        raise ValueError('size must be positive and ratio in (0,1]')
    rng = np.random.default_rng(seed)
    unique = max(1, int(size * ratio))
    ids = np.concatenate([np.arange(unique), rng.integers(0, unique, size=size-unique)])
    rng.shuffle(ids)
    events = rng.choice(['page_view','click','add_to_cart','purchase'], size, p=[.70,.20,.08,.02])
    pages = rng.choice(['/home','/products','/search','/cart','/checkout'], size)
    return pd.DataFrame({'visitor_id': np.char.add('user_', ids.astype(str)), 'timestamp': pd.date_range('2026-01-01', periods=size, freq='s'), 'page_url':pages, 'event_type':events})

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sizes', nargs='+', type=int, default=[1000,10000,100000,1000000])
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--ratio', type=float, default=.25)
    args = parser.parse_args()
    folder = DATA / 'benchmark'
    folder.mkdir(parents=True, exist_ok=True)
    records = []
    for size in args.sizes:
        frame = generate(size, args.seed, args.ratio)
        path = folder / f'events_{size}.csv'
        frame.to_csv(path, index=False)
        records.append({'file':path.name,'events':len(frame),'distinct_ids':int(frame.visitor_id.nunique()),'seed':args.seed,'target_ratio':args.ratio,'bytes':path.stat().st_size,'source':'synthetic'})
        print(records[-1])
    (folder / 'manifest.json').write_text(json.dumps(records,indent=2), encoding='utf8')

if __name__ == '__main__':
    main()
