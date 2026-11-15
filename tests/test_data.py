import pandas as pd
from scripts.generate_benchmarks import generate
from src.preprocessing import normalize, iter_visitor_ids

def test_generator():
    a=generate(1000)
    assert len(a)==1000 and a.visitor_id.nunique()==250
    pd.testing.assert_frame_equal(a,generate(1000))

def test_normalize_uci():
    frame=pd.DataFrame({'year':[2008,2008,2008],'month':[4,4,4],'day':[1,1,1],'session ID':['001','001',None],'page 2 (clothing model)':['A','B','C']})
    out=normalize(frame,'uci')
    assert list(out.visitor_id)==['001','001']
    assert list(out.timestamp)==['2008-04-01','2008-04-01']

def test_stream(tmp_path):
    path=tmp_path/'events.csv'
    pd.DataFrame({'visitor_id':['001','001','','002','NULL']}).to_csv(path,index=False)
    assert list(iter_visitor_ids(path,2))==['001','001','002']

def test_ga4():
    frame=pd.DataFrame({'user_pseudo_id':['a','<Other>','a'],'timestamp':['2020-11-01']*3,'page_url':['/']*3,'event_type':['view']*3})
    assert list(normalize(frame,'ga4').visitor_id)==['a','a']
