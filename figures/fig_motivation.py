#!/usr/bin/env python3
"""
Fig 1: Open-Page vs Close-Page IPC comparison.

LNCS style. Single-level x-axis with Suite/Program labels, 90° rotation.
"""

from common import *

# ── load data ─────────────────────────────────────────────────────────────
open_ipc  = {b: v[0] for b, v in read_comparison('GS_1c/compare_vs_open.tsv').items()}
close_ipc = {b: v[1] for b, v in read_comparison('compare_GS_vs_smart_close_1c.tsv').items()}

# ── benchmark selection ───────────────────────────────────────────────────
BENCHMARKS = [
    'hpcc/RandAcc',
    'hpcc/RandAcc_LCG',
    'hashjoin/hj-8-NPO_st',
    'crono/PageRank/soc-pokec',
    'spec17/xz/cld',
    'graph500/s16-e10',
    'ligra/CF/higgs',
    'spec06/sphinx3/ref',
    'spec06/wrf/ref',
    'ligra/PageRank/roadNet-CA',
    'npb/CG',
    'npb/IS',
]

BENCHMARKS.sort(key=lambda b: close_ipc[b] / open_ipc[b], reverse=True)

# Suite/Program labels
LABEL_MAP = {
    'hpcc/RandAcc':              'HPCC/RandAcc',
    'hpcc/RandAcc_LCG':          'HPCC/LCG',
    'hashjoin/hj-8-NPO_st':      'HashJoin/hj-8',
    'crono/PageRank/soc-pokec':   'Crono/Pokec',
    'spec17/xz/cld':              'SPEC17/xz',
    'graph500/s16-e10':           'Graph500/s16-e10',
    'ligra/CF/higgs':             'Ligra/CF',
    'spec06/sphinx3/ref':         'SPEC06/sphinx3',
    'spec06/wrf/ref':             'SPEC06/wrf',
    'ligra/PageRank/roadNet-CA':  'Ligra/road',
    'npb/CG':                     'NPB/CG',
    'npb/IS':                     'NPB/IS',
}
labels = [LABEL_MAP[b] for b in BENCHMARKS]

# ── normalize ─────────────────────────────────────────────────────────────
open_norm  = [open_ipc[b]  / max(open_ipc[b], close_ipc[b]) for b in BENCHMARKS]
close_norm = [close_ipc[b] / max(open_ipc[b], close_ipc[b]) for b in BENCHMARKS]

transition_idx = next(
    (i for i, b in enumerate(BENCHMARKS) if close_ipc[b] / open_ipc[b] < 1.0),
    None)

# ── plot ──────────────────────────────────────────────────────────────────
setup_style()
plt.rcParams.update({'font.size': 8})
fig, ax = plt.subplots(figsize=(4.803, 3.0))

n = len(labels)
x = np.arange(n)
bar_w = 0.33

c_open  = COLORS['open_page']
c_close = COLORS['closed_page']

ax.bar(x - bar_w/2, open_norm, bar_w,
       label='Open-Page', color=c_open, edgecolor='white', linewidth=0.5, zorder=3)
ax.bar(x + bar_w/2, close_norm, bar_w,
       label='Close-Page', color=c_close, edgecolor='white', linewidth=0.5, zorder=3)

ax.axhline(y=1.0, color='#333333', linestyle='-', linewidth=0.6, alpha=0.5, zorder=2)

# Loss annotations
for i in range(n):
    o, c = open_norm[i], close_norm[i]
    if c > o and (1 - o) * 100 >= 2:
        ax.text(x[i] - bar_w/2, o - 0.01, f'-{(1-o)*100:.0f}%',
                ha='center', va='top', fontsize=5.5,
                color=COLORS_DARK['open_page'], fontweight='bold')
    elif o > c and (1 - c) * 100 >= 3:
        ax.text(x[i] + bar_w/2, c - 0.01, f'-{(1-c)*100:.0f}%',
                ha='center', va='top', fontsize=5.5,
                color=COLORS_DARK['closed_page'], fontweight='bold')

# Region divider
if transition_idx is not None:
    ax.axvline(x=transition_idx - 0.5, color='#666666', linestyle='--',
               linewidth=0.8, alpha=0.5, zorder=1)
    ax.text((transition_idx - 1) / 2, 1.055,
            'Close-Page Preferred', ha='center', va='top', fontsize=6,
            color=c_close, fontweight='bold', fontstyle='italic', alpha=0.7)
    ax.text((transition_idx + n - 1) / 2, 1.055,
            'Open-Page Preferred', ha='center', va='top', fontsize=6,
            color=c_open, fontweight='bold', fontstyle='italic', alpha=0.7)

# ── x-axis ───────────────────────────────────────────────────────────────
ax.set_xticks(x)
ax.set_xticklabels(labels, rotation=90, ha='center', fontsize=6)

# ── y-axis & styling ─────────────────────────────────────────────────────
ax.set_ylim(0.65, 1.06)
ax.yaxis.set_major_locator(mticker.MultipleLocator(0.1))
ax.yaxis.set_minor_locator(mticker.MultipleLocator(0.05))
ax.set_ylabel('Normalized IPC', fontsize=8)
ax.set_xlim(-0.6, n - 0.4)
ax.tick_params(axis='y', labelsize=7)
ax.grid(axis='y', linestyle=':', alpha=0.3, zorder=0)

plt.tight_layout()
fig.subplots_adjust(top=0.88)
handles, leg_labels = ax.get_legend_handles_labels()
fig.legend(handles, leg_labels, loc='upper center', ncol=2,
           fontsize=7, frameon=False)

savefig(fig, 'motivation_open_vs_close')
