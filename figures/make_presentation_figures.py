"""Presentation-sized, vector comparisons using the existing deck's data.

Rebuild: python3 figures/make_presentation_figures.py
Embed:   python3 tools/prepare_slides.py
"""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'out'
DATA = json.loads((ROOT / 'data/presentation-comparisons.json').read_text())
INK, MUTED, TEAL, GRID = '#243c32', '#63796d', '#0b6b63', '#e7eeea'
plt.rcParams.update({
    'font.family': 'Lato', 'font.size': 10, 'svg.fonttype': 'path',
    'axes.unicode_minus': False, 'figure.facecolor': 'white',
    'savefig.facecolor': 'white', 'text.color': INK,
})


def save(fig, name):
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / f'{name}.svg')
    fig.savefig(OUT / f'{name}.png', dpi=200)
    plt.close(fig)


def context():
    rows = DATA['context']
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 2.3), sharey=True)
    fig.subplots_adjust(left=.15, right=.975, top=.77, bottom=.22, wspace=.13)
    colors = [TEAL, '#81a9b5', '#d2b17b']
    for ax, key, label in zip(axes, ['static', 'dynamic'], ['Static shapes', 'Dynamic shapes']):
        values = np.array([r[key] for r in rows]); y = np.arange(len(rows))
        ax.axhspan(-.42, .42, color='#eff6f2', zorder=0)
        left = np.zeros(len(rows))
        for j, color in enumerate(colors):
            ax.barh(y, values[:, j], left=left, height=.53, color=color, zorder=3)
            left += values[:, j]
        for i, value in enumerate(left):
            ax.text(value+130, i, f'{value:,.0f}', va='center', fontsize=10,
                    color=TEAL if i == 0 else MUTED, weight='bold' if i == 0 else 'normal')
        ax.axvline(8000, color='#9bb1a5', ls=(0,(3,3)), lw=.8)
        ax.set_xlim(0, 8500); ax.set_ylim(len(rows)-.5, -.65)
        ax.set_xticks([0,4000,8000], ['0','4K','8K'])
        ax.set_yticks(y, [r['name'] for r in rows], fontsize=10)
        ax.tick_params(axis='both', length=0, colors=MUTED, labelsize=10, pad=4)
        ax.grid(axis='x', color=GRID, lw=.7, zorder=0)
        for spine in ax.spines.values(): spine.set_visible(False)
        ax.set_title(label, loc='left', fontsize=11, fontweight='bold', color=INK, pad=8)
    axes[0].get_yticklabels()[0].set_color(TEAL)
    axes[0].get_yticklabels()[0].set_fontweight('bold')
    fig.text(.025, .955, 'Context footprint per attempt', size=13, weight='bold', va='top')
    fig.text(.975, .952, '8K comparison working set', ha='right', va='top', size=9, color=MUTED)
    fig.legend([Patch(color=c) for c in colors], ['Kernel source','Profile + feedback','Skill prompt'],
               loc='lower center', bbox_to_anchor=(.54,.005), ncol=3, frameon=False,
               fontsize=9, handlelength=1, columnspacing=1.8)
    save(fig, 'context-budget')


def loc():
    rows = DATA['loc']
    fig, ax = plt.subplots(figsize=(8.4, 2.3))
    fig.subplots_adjust(left=.255, right=.95, top=.75, bottom=.16)
    y=np.arange(len(rows)); values=[r[1] for r in rows]
    ax.axhspan(.62, 1.38, color='#eff6f2', zorder=0)
    ax.barh(y, values, height=.52, color=['#79ae99', TEAL]+['#a8bbb2']*4, zorder=3)
    for i,value in enumerate(values):
        ax.text(value+5, i, str(value), va='center', fontsize=10,
                color=TEAL if i<2 else MUTED, weight='bold' if i==1 else 'normal')
    ax.set_yticks(y,[r[0] for r in rows],fontsize=10)
    ax.set_ylim(len(rows)-.5,-.7); ax.set_xlim(0,315)
    ax.set_xticks([0,100,200,300]); ax.grid(axis='x', color=GRID, lw=.7, zorder=0)
    ax.tick_params(axis='both',length=0,colors=MUTED,labelsize=10,pad=5)
    for spine in ax.spines.values(): spine.set_visible(False)
    ax.get_yticklabels()[1].set_color(TEAL);ax.get_yticklabels()[1].set_fontweight('bold')
    fig.text(.025,.95,'Persistent, warp-specialized GEMM',size=13,weight='bold',va='top')
    fig.text(.975,.946,'Lines of code · lower is shorter',size=9,color=MUTED,ha='right',va='top')
    save(fig,'loc-comparison')


def pass_rates():
    data = DATA['pass']
    fig, axes = plt.subplots(1, 2, figsize=(8.0, 4.4), sharey=True)
    fig.subplots_adjust(left=.15, right=.98, top=.84, bottom=.19, wspace=.13)
    y=np.arange(6)
    for ax, key, label in zip(axes, ['static', 'dynamic'], ['Static shapes', 'Dynamic shapes']):
        p1, p5=data[key+'_p1'], data[key+'_p5']
        colors=[TEAL]+['#a7bcb1']*5
        ax.axhspan(-.44,.44,color='#edf5ef',zorder=0)
        ax.barh(y-.14,p1,height=.25,color=colors,zorder=3)
        ax.barh(y+.15,p5,height=.22,facecolor='white',edgecolor=colors,hatch='////',linewidth=.6,zorder=3)
        for i,v in enumerate(p1):
            ax.text(v-2,i-.14,f'{v:.1f}',color='white' if i==0 else '#274538',
                    fontsize=9,ha='right',va='center',weight='bold')
        ax.set_xlim(0,103);ax.set_ylim(5.55,-.6)
        ax.set_xticks([0,50,100],['0','50','100%'])
        ax.set_yticks(y,data['names'],fontsize=11)
        ax.tick_params(axis='both',length=0,colors=MUTED,pad=6)
        ax.grid(axis='x',color=GRID,linewidth=.7)
        for spine in ax.spines.values():spine.set_visible(False)
        ax.set_title(label,loc='left',fontsize=14,weight='bold',color=INK,pad=14)
    axes[0].get_yticklabels()[0].set_color(TEAL)
    axes[0].get_yticklabels()[0].set_fontweight('bold')
    fig.text(.03,.96,'Compile success (%)',size=13,weight='bold',va='top')
    fig.legend([Patch(color=TEAL),Patch(facecolor='white',edgecolor=TEAL,hatch='////')],
               ['pass@1','pass@5'],loc='lower center',bbox_to_anchor=(.56,.03),
               ncol=2,frameon=False,fontsize=11,handlelength=1.6,columnspacing=2.5)
    save(fig,'compile-pass')


if __name__ == '__main__':
    context()
    loc()
    pass_rates()
    print('Rebuilt context-budget, loc-comparison and compile-pass SVG/PNG figures')
