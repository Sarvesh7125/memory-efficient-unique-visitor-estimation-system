import json
import pandas as pd
import plotly.express as px
import streamlit as st
from src.dashboard import ROOT, datasets, columns, analyze, merge_demo, benchmark_dir, reset

st.set_page_config(page_title='Cardinality Lab | Visitor Analytics', page_icon='◈', layout='wide')
st.markdown('''<style>
.block-container {max-width: 1280px; padding-top: 2.3rem; padding-bottom: 3rem;}
[data-testid="stMetric"] {background: #131F31; border: 1px solid #293850; border-radius: 14px; padding: 19px;}
[data-testid="stMetricLabel"] {color: #9EADC3;}
[data-testid="stSidebar"] {border-right: 1px solid #293850;}
</style>''', unsafe_allow_html=True)
NAV = ['Overview','Live Visitor Estimation','Performance Benchmarking','Precision Analysis','Distributed Sketch Merging','Dataset Explorer']
COLORS = ['#35D9B2','#719CFF','#F4B86B','#D78BFA']
folder = benchmark_dir()
with st.sidebar:
    st.title('◈ Cardinality Lab')
    st.caption('SDS MINI PROJECT  /  VISITOR ANALYTICS')
    page = st.radio('Workspace', NAV, label_visibility='collapsed')
    st.divider()
    st.caption('HyperLogLog • Python Set • Streaming CSV')
    st.caption('Real-world UCI identifiers represent sessions, not people.')
    if folder:
        st.caption('Benchmark source: ' + ('Local results' if folder.name == 'phase_5_6' else 'Reference results (other machine)'))


def pretty(value, digits=0):
    return '—' if value is None else f'{value:,.{digits}f}'


def metric_row(items):
    for col, (label,value) in zip(st.columns(len(items)),items):
        col.metric(label,value)


def chart(fig):
    fig.update_layout(template='plotly_dark', paper_bgcolor='#0B1220', plot_bgcolor='#131F31', margin=dict(l=15,r=15,t=45,b=15), legend_title_text='', font=dict(color='#E6EDF7'))
    st.plotly_chart(fig, use_container_width=True)


def downloads(data, name):
    a,b = st.columns(2)
    frame = data if isinstance(data,pd.DataFrame) else pd.DataFrame([data])
    a.download_button('Download CSV',frame.to_csv(index=False),name+'.csv','text/csv',key=name+'csv')
    payload = frame.to_json(orient='records',indent=2) if isinstance(data,pd.DataFrame) else json.dumps(data,indent=2,allow_nan=False)
    b.download_button('Download JSON',payload,name+'.json','application/json',key=name+'json')


def select_source(key):
    files = datasets()
    mode = st.radio('Data source',['Project dataset','Upload CSV'],horizontal=True,key=key+'mode')
    if mode == 'Upload CSV':
        return st.file_uploader('Select CSV',type=['csv'],key=key+'upload')
    if not files:
        st.warning('No project CSVs found. Upload a CSV instead.')
        return None
    return st.selectbox('Dataset',files,format_func=lambda p: str(p.relative_to(ROOT)),key=key+'file')


def load_bench(name):
    if folder is None:
        st.warning('No benchmark results found. Run python -m scripts.run_benchmarks.')
        st.stop()
    return pd.read_csv(folder / name)


st.caption('WORKSPACE  /  '+page.upper())
st.title(page)
if page == 'Overview':
    st.write('Estimate distinct website identifiers without retaining every ID. Explore the accuracy, speed and memory trade-offs of a probabilistic sketch.')
    if folder:
        df = load_bench('scalability.csv')
        row = df.loc[df['events'].idxmax()]
        metric_row([('Largest workload',pretty(row.events)),('Exact IDs',pretty(row.exact_count)),('HLL estimate',pretty(row.hll_estimate)),('Memory reduction',pretty(row.memory_ratio,1)+'×')])
        st.caption('Largest dataset in '+folder.name+'; retained algorithm memory, not total RAM.')
        chart(px.bar(df,x='dataset',y=['exact_retained_bytes','hll_retained_bytes'],barmode='group',log_y=True,title='Retained memory by dataset (log scale)',labels={'value':'Bytes','variable':'Algorithm'},color_discrete_sequence=COLORS))
    else:
        st.info('Run benchmarks to populate the overview. Live estimation is available now.')
    st.subheader('How the system works')
    for col, title, body in zip(st.columns(3),['01 / Ingest','02 / Estimate','03 / Evaluate'],['Read visitor IDs in CSV chunks.','Hash each ID and update fixed-size registers.','Compare with exact counting when enabled.']):
        col.markdown('**'+title+'**'); col.write(body)
elif page == 'Live Visitor Estimation':
    st.write('Choose a dataset and precision. Turn off exact comparison to avoid retaining all unique IDs.')
    source = select_source('live')
    p = st.slider('Precision (p)',8,16,12,key='livep')
    compare = st.checkbox('Compare with Python Set',True)
    metric_row([('Registers',pretty(2**p)),('Register payload',f'{2**p/1024:g} KiB'),('Theoretical RSE',f'{104/(2**p)**0.5:.3f}%')])
    if source is not None:
        try:
            cols = columns(source)
            column = st.selectbox('Identifier column',cols,index=cols.index('visitor_id') if 'visitor_id' in cols else 0)
            kind = st.selectbox('Identifier meaning',['Distinct supplied IDs','Session IDs','Pseudonymous visitor IDs'],index=1 if getattr(source,'name','')=='uci_events.csv' else 0)
            if st.button('Run estimation',type='primary'):
                with st.spinner('Processing CSV in chunks…'):
                    result = analyze(source,column,p,compare)
                    result.update(dataset=source.name,identifier_kind=kind,identifier_column=column)
                    st.session_state['live_result'] = result
        except (ValueError,OSError,pd.errors.ParserError,pd.errors.EmptyDataError) as exc:
            st.error(str(exc))
    result = st.session_state.get('live_result')
    if result:
        st.subheader('Last completed run')
        st.caption(f"{result['dataset']} · {result['identifier_kind']} · p={result['precision']}")
        metric_row([('Valid events',pretty(result['events'])),('Exact count',pretty(result['exact_count'])),('HLL estimate',pretty(result['hll_estimate'])),('Absolute error',pretty(result['absolute_error_pct'],3)+'%' if result['absolute_error_pct'] is not None else '—')])
        metric_row([('HLL retained bytes',pretty(result['hll_retained_bytes'])),('Set retained bytes',pretty(result['exact_retained_bytes'])),('HLL processing ms',pretty(result['hll_ms'],2)),('Set processing ms',pretty(result['exact_ms'],2))])
        if result['exact_retained_bytes'] is not None:
            chart(px.bar(x=['Python Set','HyperLogLog'],y=[result['exact_retained_bytes'],result['hll_retained_bytes']],log_y=True,labels={'x':'Algorithm','y':'Retained bytes'},title='Memory comparison',color_discrete_sequence=COLORS))
        st.caption('Times exclude CSV parsing; live measurements are single-run, not repeated benchmarks. Uploaded data and CSV chunks also use memory.')
        downloads(result,'live_estimation')
elif page == 'Performance Benchmarking':
    df = load_bench('scalability.csv')
    picks = st.multiselect('Datasets',df.dataset.tolist(),default=df.dataset.tolist())
    df = df[df.dataset.isin(picks)].sort_values('events')
    if df.empty:
        st.info('Select at least one dataset.'); st.stop()
    chart(px.line(df,x='events',y=['exact_median_ms','hll_median_ms'],markers=True,log_x=True,log_y=True,title='Median execution time',labels={'value':'Milliseconds','events':'Events'},color_discrete_sequence=COLORS))
    a,b = st.columns(2)
    with a:
        chart(px.bar(df,x='dataset',y=['exact_retained_bytes','hll_retained_bytes'],barmode='group',log_y=True,title='Retained memory',labels={'value':'Bytes'},color_discrete_sequence=COLORS))
    with b:
        chart(px.bar(df,x='dataset',y=['exact_peak_bytes','hll_peak_bytes'],barmode='group',log_y=True,title='Peak traced allocations',labels={'value':'Bytes'},color_discrete_sequence=COLORS))
    chart(px.bar(df,x='dataset',y='absolute_error_pct',title='Absolute estimation error (%)',color_discrete_sequence=COLORS))
    chart(px.bar(df,x='dataset',y=['exact_count','hll_estimate'],barmode='group',title='Exact versus estimated cardinality',color_discrete_sequence=COLORS))
    st.caption('Peak memory uses tracemalloc, not process RSS. Input buffers are excluded in the benchmark.')
    st.dataframe(df,use_container_width=True,hide_index=True); downloads(df,'scalability')
elif page == 'Precision Analysis':
    df = load_bench('precision_summary.csv')
    trials = load_bench('precision_trials.csv')
    chart(px.line(df,x='precision',y=['rmse_pct','theoretical_rse_pct','mean_absolute_error_pct'],markers=True,title='Observed and theoretical errors',labels={'value':'Percent'},color_discrete_sequence=COLORS))
    chart(px.scatter(df,x='register_bytes',y='rmse_pct',text='precision',log_x=True,title='Memory–accuracy trade-off',color_discrete_sequence=COLORS))
    chart(px.box(trials,x='precision',y='signed_error_pct',points='all',title='Error distribution by precision',color_discrete_sequence=COLORS))
    st.dataframe(df,use_container_width=True,hide_index=True); downloads(df,'precision_summary'); downloads(trials,'precision_trials')
elif page == 'Distributed Sketch Merging':
    st.write('Simulate two sources with overlapping identifiers. The merged sketch takes the maximum of each corresponding register.')
    a,b = st.columns(2)
    left = a.number_input('Source A distinct IDs',1,100000,10000)
    right = b.number_input('Source B distinct IDs',1,100000,10000)
    overlap = st.slider('Shared IDs',0,min(left,right),min(5000,left,right))
    p = st.slider('Sketch precision',8,16,12)
    if st.button('Merge sketches',type='primary'):
        result = merge_demo(left,right,overlap,p)
        metric_row([('Actual union',pretty(result['exact_union'])),('Merged estimate',pretty(result['merged_estimate'])),('Direct estimate',pretty(result['direct_estimate']))])
        if result['identical_registers']:
            st.success('Merged registers are identical to the sketch built directly over the union.')
        chart(px.bar(x=['A estimate','B estimate','Union estimate'],y=[result['left_estimate'],result['right_estimate'],result['merged_estimate']],title='Independent estimates and merged union',color_discrete_sequence=COLORS))
        downloads(result,'merge_demo')
elif page == 'Dataset Explorer':
    source = select_source('explorer')
    if source is not None:
        try:
            frame = pd.read_csv(reset(source),nrows=1000,dtype='string',keep_default_na=False)
            metric_row([('Preview rows',pretty(len(frame))),('Columns',pretty(len(frame.columns)))])
            st.caption('Preview only: first 1,000 rows. Counts and distributions below describe the preview, not the full dataset.')
            st.dataframe(frame,hide_index=True,use_container_width=True)
            column = st.selectbox('Explore column',frame.columns)
            frequency = frame[column].value_counts().head(15).rename_axis('value').reset_index(name='count')
            chart(px.bar(frequency,x='value',y='count',title='Top 15 values in preview',color_discrete_sequence=COLORS))
            downloads(frame,'dataset_preview')
        except (ValueError,OSError,pd.errors.ParserError,pd.errors.EmptyDataError) as exc:
            st.error(str(exc))
