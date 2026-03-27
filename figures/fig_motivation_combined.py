#!/usr/bin/env python3
"""
Fig 1: Motivation — combined subfigures.

(a) Open-Page vs Close-Page IPC comparison across 12 workloads.
(b) Row buffer hit rate across execution epochs for four representative workloads.
"""

import json
from collections import defaultdict
from common import *
import matplotlib.gridspec as gridspec

setup_style()

# ══════════════════════════════════════════════════════════════════════════
# Data for (a): Open-Page vs Close-Page
# ══════════════════════════════════════════════════════════════════════════
open_ipc  = {b: v[0] for b, v in read_comparison('GS_1c/compare_vs_open.tsv').items()}
close_ipc = {b: v[1] for b, v in read_comparison('compare_GS_vs_smart_close_1c.tsv').items()}

BENCHMARKS_A = [
    'hpcc/RandAcc', 'hpcc/RandAcc_LCG', 'hashjoin/hj-8-NPO_st',
    'crono/PageRank/soc-pokec', 'spec17/xz/cld', 'graph500/s16-e10',
    'ligra/CF/higgs', 'spec06/sphinx3/ref', 'spec06/wrf/ref',
    'ligra/PageRank/roadNet-CA', 'npb/CG', 'npb/IS',
]
BENCHMARKS_A.sort(key=lambda b: close_ipc[b] / open_ipc[b], reverse=True)

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
labels_a = [LABEL_MAP[b] for b in BENCHMARKS_A]

open_norm  = [open_ipc[b]  / max(open_ipc[b], close_ipc[b]) for b in BENCHMARKS_A]
close_norm = [close_ipc[b] / max(open_ipc[b], close_ipc[b]) for b in BENCHMARKS_A]

transition_idx = next(
    (i for i, b in enumerate(BENCHMARKS_A) if close_ipc[b] / open_ipc[b] < 1.0),
    None)

# ══════════════════════════════════════════════════════════════════════════
# Data for (b): Phase RBH
# ══════════════════════════════════════════════════════════════════════════
BENCHMARKS_B = [
    {
        'path': 'open_page_1c/spec17/mcf/ref/5',
        'title': 'SPEC17/mcf',
        'arrows': [
            {'text': 'High', 'xy': (50, 98),  'xytext': (50, 60)},
            {'text': 'Low',  'xy': (148, 13), 'xytext': (148, 50)},
        ],
    },
    {
        'path': 'open_page_1c/crono/PageRank/soc-pokec/0',
        'title': 'Crono/PageRank',
        'arrows': [
            {'text': 'Low',  'xy': (50, 15),  'xytext': (50, 55)},
            {'text': 'High', 'xy': (100, 93), 'xytext': (100, 55)},
        ],
    },
    {
        'path': 'open_page_1c/spec06/GemsFDTD/ref/17',
        'title': 'SPEC06/GemsFDTD',
        'arrows': [
            {'text': 'Low',  'xy': (13, 20),  'xytext': (13, 60)},
            {'text': 'High', 'xy': (32, 87),  'xytext': (32, 55)},
        ],
    },
    {
        'path': 'open_page_1c/spec06/zeusmp/ref/23',
        'title': 'SPEC06/zeusmp',
        'arrows': [
            {'text': 'Low',  'xy': (8, 17),   'xytext': (8, 55)},
            {'text': 'High', 'xy': (20, 97),  'xytext': (20, 65)},
            {'text': 'Mid',  'xy': (31, 49),  'xytext': (31, 80)},
        ],
    },
]


def load_rbh(rel_path):
    """Load ddrepoch.json -> (epochs, rbh%) aggregated across channels."""
    path = f'{RESULTS_DIR}/{rel_path}/ddrepoch.json'
    with open(path) as f:
        raw = json.load(f)
    agg = defaultdict(lambda: [0, 0])
    for rec in raw:
        e = rec['epoch_num']
        agg[e][0] += rec.get('num_read_row_hits', 0) + rec.get('num_write_row_hits', 0)
        agg[e][1] += rec.get('num_read_cmds', 0) + rec.get('num_write_cmds', 0)
    epochs, rbh = [], []
    for e in sorted(agg.keys()):
        hits, total = agg[e]
        if total == 0:
            continue
        epochs.append(e)
        rbh.append(hits / total * 100)
    return epochs, rbh


# ══════════════════════════════════════════════════════════════════════════
# Figure layout: (a) on top, (b) 2×2 on bottom — compact
# ══════════════════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(LNCS_TEXT_WIDTH, 4.0))
gs = gridspec.GridSpec(2, 1, height_ratios=[1.6, 2.8], hspace=0.55)

# ── (a) Bar chart ────────────────────────────────────────────────────────
ax_a = fig.add_subplot(gs[0])

n = len(labels_a)
x = np.arange(n)
bar_w = 0.33

c_open  = COLORS['open_page']
c_close = COLORS['closed_page']

ax_a.bar(x - bar_w/2, open_norm, bar_w,
         label='Open-Page', color=c_open, hatch=HATCHES['open_page'],
         edgecolor='black', linewidth=0.8, zorder=3)
ax_a.bar(x + bar_w/2, close_norm, bar_w,
         label='Close-Page', color=c_close, hatch=HATCHES['closed_page'],
         edgecolor='black', linewidth=0.8, zorder=3)

# Region divider
if transition_idx is not None:
    ax_a.axvline(x=transition_idx - 0.5, color='#666666', linestyle='--',
                 linewidth=0.8, alpha=0.5, zorder=1)

ax_a.set_xticks(x)
ax_a.set_xticklabels(labels_a, rotation=35, ha='right')
ax_a.set_ylim(0.65, 1.06)
ax_a.yaxis.set_major_locator(mticker.MultipleLocator(0.1))
ax_a.yaxis.set_minor_locator(mticker.MultipleLocator(0.05))
ax_a.set_ylabel('Normalized IPC')
ax_a.set_xlim(-0.6, n - 0.4)
ax_a.grid(axis='y', linestyle=':', alpha=0.3, zorder=0)

handles, leg_labels = ax_a.get_legend_handles_labels()
ax_a.legend(handles, leg_labels, loc='upper center', ncol=2,
            fontsize=FONT_ANNOT, frameon=False, bbox_to_anchor=(0.5, 1.18))

ax_a.text(-0.08, 1.18, '(a)', transform=ax_a.transAxes,
          fontsize=FONT_TITLE, fontweight='bold', va='top')

# ── (b) 2×2 phase RBH ───────────────────────────────────────────────────
gs_b = gridspec.GridSpecFromSubplotSpec(2, 2, subplot_spec=gs[1],
                                        hspace=0.5, wspace=0.3)
axes_b = np.array([[fig.add_subplot(gs_b[i, j]) for j in range(2)]
                    for i in range(2)])

phase_colors = [COLORS['open_page'], COLORS['closed_page'],
                COLORS['craft'], COLORS['dympl']]
phase_styles = ['-', '--', '-.', ':']

for ax, cfg, pcol, pls in zip(axes_b.flat, BENCHMARKS_B, phase_colors, phase_styles):
    epochs, rbh = load_rbh(cfg['path'])

    ax.plot(epochs, rbh, color=pcol, linewidth=1.0, linestyle=pls)
    ax.fill_between(epochs, rbh, alpha=0.18, color=pcol)

    ax.set_ylim(-2, 105)
    ax.yaxis.set_major_locator(mticker.MultipleLocator(25))
    ax.grid(axis='y', linestyle=':', alpha=0.3)
    ax.set_title(cfg['title'], fontsize=FONT_TICK, pad=3)

    for arr in cfg['arrows']:
        ax.annotate(arr['text'], xy=arr['xy'], xytext=arr['xytext'],
                    fontsize=FONT_DETAIL, ha='center', va='center',
                    color='#333333', fontweight='bold',
                    arrowprops=dict(arrowstyle='->', color='#666666',
                                   lw=0.6),
                    annotation_clip=False)

# Shared axis labels
for ax in axes_b[1]:
    ax.set_xlabel('Epoch')
# Single shared y-label centered vertically between the two rows
bbox_top = axes_b[0, 0].get_position()
bbox_bot = axes_b[1, 0].get_position()
fig.text(bbox_bot.x0 - 0.08, (bbox_top.y1 + bbox_bot.y0) / 2,
         'Row Buffer Hit Rate (%)', fontsize=FONT_AXIS_LABEL, va='center',
         rotation=90)

axes_b[0, 0].text(-0.2, 1.2, '(b)', transform=axes_b[0, 0].transAxes,
                   fontsize=FONT_TITLE, fontweight='bold', va='top')

savefig(fig, 'motivation_combined')
plt.close(fig)
