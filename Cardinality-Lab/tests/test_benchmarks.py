import math
from scripts.run_benchmarks import measure, precision_trials, summarize, merge_demo, signed_error, benchmark
from scripts.plot_benchmarks import plot_all
from src.exact import ExactCounter
import pandas as pd


def test_measure():
    result=measure(ExactCounter,['a','b','a'],2)
    assert result['estimate']==2 and len(result['times_ms'])==2
    assert result['peak_bytes']>0 and result['retained_bytes']>0


def test_precision_reproducibility():
    a=precision_trials(3,200,[8,12])
    b=precision_trials(3,200,[8,12])
    assert [r['estimate'] for r in a]==[r['estimate'] for r in b]
    assert len(a)==6


def test_statistics():
    rows=precision_trials(3,200,[8])
    s=summarize(rows)[0]
    assert math.isclose(s['rmse_pct'],math.sqrt(sum(r['signed_error_pct']**2 for r in rows)/3))
    assert s['trials']==3 and signed_error(90,100)==-10


def test_merge():
    assert merge_demo()['identical_registers']


def test_pipeline(tmp_path):
    path=tmp_path/'events.csv'
    pd.DataFrame({'visitor_id':['a','b','a','c']}).to_csv(path,index=False)
    row=benchmark(path,2,expected=3)
    assert row['events']==4 and row['exact_count']==3
    trials=precision_trials(2,200,[8,12])
    pd.DataFrame([row]).to_csv(tmp_path/'scalability.csv',index=False)
    pd.DataFrame(trials).to_csv(tmp_path/'precision_trials.csv',index=False)
    pd.DataFrame(summarize(trials)).to_csv(tmp_path/'precision_summary.csv',index=False)
    plot_all(tmp_path,tmp_path/'plots')
    assert len(list((tmp_path/'plots').glob('*.png')))==8
