"""
Row buffer hit rate over execution epochs (open-page policy).
2×2 panel showing four representative phase-change patterns.
"""

import json
from collections import defaultdict
from common import *

setup_style()
plt.rcParams.update({'font.size': 8})

# ── benchmark configs ────────────────────────────────────────────────────
BENCHMARKS = [
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
    """Load ddrepoch.json → (epochs, rbh%) aggregated across channels."""
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


# ── plot 2×2 ─────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(4.8, 3.5))

for ax, cfg in zip(axes.flat, BENCHMARKS):
    epochs, rbh = load_rbh(cfg['path'])

    ax.plot(epochs, rbh, color=COLORS['open_page'], linewidth=1.0)
    ax.fill_between(epochs, rbh, alpha=0.12, color=COLORS['open_page'])

    ax.set_ylim(-2, 105)
    ax.tick_params(labelsize=7)
    ax.yaxis.set_major_locator(mticker.MultipleLocator(25))
    ax.grid(axis='y', linestyle=':', alpha=0.3)
    ax.set_title(cfg['title'], fontsize=8, pad=4)

    for arr in cfg['arrows']:
        ax.annotate(arr['text'], xy=arr['xy'], xytext=arr['xytext'],
                    fontsize=6, ha='center', va='center',
                    color=COLORS_DARK['open_page'], fontweight='bold',
                    arrowprops=dict(arrowstyle='->', color='#888888',
                                   lw=0.8),
                    annotation_clip=False)

# shared axis labels
for ax in axes[1]:
    ax.set_xlabel('Epoch', fontsize=8)
for ax in axes[:, 0]:
    ax.set_ylabel('Row Buffer Hit Rate (%)', fontsize=8)

fig.tight_layout(h_pad=1.2, w_pad=1.0)
savefig(fig, 'phase_rbh_4bench')
plt.close(fig)
