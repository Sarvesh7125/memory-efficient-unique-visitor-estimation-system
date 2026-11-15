from pathlib import Path
import pandas as pd

COLUMNS = ['visitor_id', 'timestamp', 'page_url', 'event_type']

def normalize(frame, source):
    if source == 'uci':
        dates = pd.to_datetime(frame[['year', 'month', 'day']], errors='coerce')
        out = pd.DataFrame({'visitor_id': frame['session ID'], 'timestamp': dates.dt.strftime('%Y-%m-%d'), 'page_url': '/product/' + frame['page 2 (clothing model)'].astype('string'), 'event_type': 'click'})
    elif source == 'ga4':
        out = frame.rename(columns={'user_pseudo_id':'visitor_id'})[COLUMNS].copy()
    else:
        out = frame[COLUMNS].copy()
    ids = out['visitor_id'].astype('string').str.strip()
    valid = ids.notna() & ~ids.str.lower().isin(['', 'null', 'nan', '<other>']) & out['timestamp'].notna()
    out = out.loc[valid].copy()
    out['visitor_id'] = ids.loc[valid]
    return out.reset_index(drop=True)

def iter_visitor_ids(path, chunksize=50000):
    for chunk in pd.read_csv(path, usecols=['visitor_id'], dtype='string', keep_default_na=False, chunksize=chunksize):
        ids = chunk['visitor_id'].str.strip()
        yield from ids[~ids.str.lower().isin(['', 'null', 'nan', '<other>'])]
