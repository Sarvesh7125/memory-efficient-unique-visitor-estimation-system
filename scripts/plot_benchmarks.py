import argparse
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from src.paths import ROOT


def plot_all(results, output):
    output.mkdir(parents=True,exist_ok=True)
    d = pd.read_csv(results/'scalability.csv').sort_values('events')
    s = pd.read_csv(results/'precision_summary.csv')
    t = pd.read_csv(results/'precision_trials.csv')
    x = np.arange(len(d))
    labels = [f'{n:,}\n'+('UCI sessions' if name=='uci_events' else 'Synthetic') for n,name in zip(d.events,d.dataset)]
    plt.style.use('seaborn-v0_8-whitegrid')
    def start(title):
        fig,ax = plt.subplots(figsize=(9,5),layout='constrained')
        ax.set_title(title,loc='left',fontweight='bold',fontsize=15,pad=12)
        return fig,ax
    def save(fig, name):
        fig.savefig(output/f'{name}.png',dpi=220,bbox_inches='tight')
        plt.close(fig)
    def dataset_axis(ax):
        ax.set_xticks(x,labels)
        ax.set_xlabel('Event count and source')
    def paired(ax,a,b,unit):
        ax.bar(x-.19,a,.38,label='Python Set')
        ax.bar(x+.19,b,.38,label='HyperLogLog')
        dataset_axis(ax)
        ax.set_ylabel(unit)
        ax.legend()
    fig,ax=start('01  |  Median execution time')
    paired(ax,d.exact_median_ms,d.hll_median_ms,'Milliseconds (log scale)')
    ax.set_yscale('log')
    save(fig,'01_execution_time')
    fig,ax=start('02  |  Retained and peak allocation memory')
    ax.bar(x-.31,d.exact_retained_bytes/1024,.2,label='Set retained')
    ax.bar(x-.10,d.hll_retained_bytes/1024,.2,label='HLL retained')
    ax.bar(x+.11,d.exact_peak_bytes/1024,.2,label='Set peak traced')
    ax.bar(x+.32,d.hll_peak_bytes/1024,.2,label='HLL peak traced')
    dataset_axis(ax); ax.set_yscale('log'); ax.set_ylabel('KiB (log scale)'); ax.legend(ncol=2)
    save(fig,'02_memory_comparison')
    fig,ax=start('03  |  Exact versus estimated cardinality')
    paired(ax,d.exact_count,d.hll_estimate,'Distinct IDs (log scale)'); ax.set_yscale('log')
    save(fig,'03_cardinality')
    fig,ax=start('04  |  Absolute estimation error')
    ax.bar(x,d.absolute_error_pct,label='Observed error'); ax.axhline(d.theoretical_rse_pct.iloc[0],linestyle='--',label='Theoretical RSE (not a bound)')
    dataset_axis(ax); ax.set_ylabel('Percent'); ax.legend()
    save(fig,'04_estimation_error')
    fig,ax=start('05  |  Effect of sketch precision')
    ax.plot(s.precision,s.rmse_pct,'o-',label='Observed relative RMSE'); ax.plot(s.precision,s.theoretical_rse_pct,'s--',label='Theoretical RSE'); ax.set_xticks(s.precision); ax.set_xlabel('Precision p'); ax.set_ylabel('Percent'); ax.legend()
    save(fig,'05_precision_error')
    fig,ax=start('06  |  Memory–accuracy trade-off')
    ax.plot(s.register_bytes/1024,s.mean_absolute_error_pct,'o-'); ax.set_xscale('log',base=2); ax.set_xlabel('Register storage (KiB)'); ax.set_ylabel('Mean absolute error (%)')
    for r in s.itertuples(): ax.annotate(f'p={r.precision}',(r.register_bytes/1024,r.mean_absolute_error_pct),xytext=(5,5),textcoords='offset points')
    save(fig,'06_memory_accuracy')
    fig,ax=start('07  |  Signed error across independent ID sets')
    ps=sorted(t.precision.unique()); ax.boxplot([t.loc[t.precision==p,'signed_error_pct'] for p in ps]); ax.set_xticks(range(1,len(ps)+1),ps); ax.axhline(0,linestyle='--'); ax.set_xlabel('Precision p'); ax.set_ylabel('Signed relative error (%)')
    save(fig,'07_error_distribution')
    fig,ax=start('08  |  Retained memory reduction')
    bars=ax.bar(x,d.memory_ratio); ax.set_yscale('log'); dataset_axis(ax); ax.set_ylabel('Set / HLL memory (×, log scale)'); ax.bar_label(bars,labels=[f'{v:,.1f}×' for v in d.memory_ratio],padding=3); ax.margins(y=.18)
    save(fig,'08_memory_savings')


def main():
    p=argparse.ArgumentParser(); p.add_argument('--results',type=Path,default=ROOT/'results'/'phase_5_6'); p.add_argument('--output',type=Path,default=ROOT/'visualizations'/'phase_5_6'); a=p.parse_args(); plot_all(a.results,a.output); print(f'Graphs: {a.output}')


if __name__=='__main__':
    main()
