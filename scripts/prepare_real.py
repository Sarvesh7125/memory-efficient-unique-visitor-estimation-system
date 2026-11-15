import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import urlretrieve
from zipfile import ZipFile
import pandas as pd
from src.paths import DATA
from src.preprocessing import normalize

URL = 'https://archive.ics.uci.edu/static/public/553/clickstream+data+for+online+shopping.zip'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', choices=['uci','ga4','standard'], default='uci')
    parser.add_argument('--input', type=Path)
    args = parser.parse_args()
    raw = DATA / 'raw'
    raw.mkdir(parents=True,exist_ok=True)
    path = args.input
    if path is None:
        if args.source != 'uci':
            parser.error('--input is required for this source')
        path = raw / 'uci_clickstream.zip'
        if not path.exists():
            urlretrieve(URL, path)
    if args.source == 'uci' and path.suffix.lower() == '.zip':
        with ZipFile(path) as archive:
            matches = [n for n in archive.namelist() if n.lower().endswith('e-shop clothing 2008.csv')]
            if len(matches) != 1:
                raise ValueError('Expected exactly one UCI clickstream CSV')
            with archive.open(matches[0]) as f:
                frame = pd.read_csv(f, sep=';', dtype={'session ID':'string'})
    else:
        frame = pd.read_csv(path, sep=';' if args.source=='uci' else ',', dtype='string' if args.source!='uci' else {'session ID':'string'})
    cleaned = normalize(frame,args.source)
    folder = DATA / 'processed'
    folder.mkdir(parents=True,exist_ok=True)
    output = folder / f'{args.source}_events.csv'
    cleaned.to_csv(output,index=False)
    meta = {'source':args.source,'input_file':path.name,'input_sha256':hashlib.file_digest(path.open('rb'),'sha256').hexdigest(),'raw_rows':len(frame),'valid_rows':len(cleaned),'removed_rows':len(frame)-len(cleaned),'distinct_ids':int(cleaned.visitor_id.nunique()),'identifier_kind':'session ID (not person)' if args.source=='uci' else ('pseudonymous user ID' if args.source=='ga4' else 'user-supplied identifier'),'output':output.name}
    (folder/f'{args.source}_manifest.json').write_text(json.dumps(meta,indent=2),encoding='utf8')
    print(json.dumps(meta,indent=2))

if __name__=='__main__':
    main()
