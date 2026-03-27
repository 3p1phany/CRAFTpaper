#!/usr/bin/env python3
"""Figure: Timeout Precharge Accuracy vs IPC Improvement.

Sorted by accuracy (ascending) to highlight the paradox: low-accuracy
benchmarks (roadNet-CA) achieve the largest IPC gains because wrong
precharges drive escalation toward an open-page policy.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

setup_style()

# ── data (from craft_timeout_accuracy.md, sorted by accuracy ascending) ──
benchmarks = [
    'ligra/PageRank/roadNet-CA',        # 32.8%
    'ligra/Triangle/roadNet-CA',        # 35.3%
    'ligra/CF/roadNet-CA',              # 47.4%
    'crono/Triangle-Counting/roadNet-CA',  # 52.2%
    'spec06/wrf/ref',                   # 53.7%
    'spec06/sphinx3/ref',               # 55.8%
    'ligra/BFSCC/soc-pokec-short',      # 63.9%
    'ligra/Radii/higgs',                # 71.5%
    'ligra/Components-Shortcut/soc-pokec',  # 83.6%
    'ligra/CF/higgs',                   # 87.6%
    'ligra/CF/soc-pokec',               # 89.6%
    'ligra/PageRank/higgs',             # 90.1%
]

accuracy = [32.8, 35.3, 47.4, 52.2, 53.7, 55.8, 63.9, 71.5, 83.6, 87.6, 89.6, 90.1]
ipc_impr = [1.89, 2.00, 5.79, 1.74, 1.65, 2.60, 2.85, 1.61, 1.63, 3.10, 2.02, 2.87]

labels = [short_name(b) for b in benchmarks]
n = len(labels)
x = np.arange(n)

# ── color: highlight roadNet-CA benchmarks (accuracy < 50%) ──────────────
bar_colors = []
for acc in accuracy:
    if acc < 50.0:
        bar_colors.append(COLORS['closed_page'])  # brick red for low accuracy
    else:
        bar_colors.append(COLORS['craft'])         # forest green for normal

# ── plot ─────────────────────────────────────────────────────────────────
fig, ax1 = plt.subplots(figsize=(LNCS_TEXT_WIDTH, 3.5))

# Accuracy bars
bars = ax1.bar(x, accuracy, 0.55,
               color=bar_colors, edgecolor='white', linewidth=0.5)

# 50% reference line
ax1.axhline(y=50, color='gray', linestyle='--', linewidth=0.8, alpha=0.6)
ax1.text(n - 0.4, 51.5, '50%', fontsize=6, color='gray',
         ha='right', va='bottom')

# Left axis styling
ax1.set_ylabel('Timeout Precharge Accuracy (%)')
ax1.set_ylim(0, 105)
ax1.set_yticks(np.arange(0, 101, 20))

ax1.set_xticks(x)
ax1.set_xticklabels(labels, rotation=35, ha='right')
ax1.grid(axis='y', linestyle=':', alpha=0.3)
ax1.set_xlim(-0.6, n - 0.4)

# IPC improvement on secondary axis
ax2 = ax1.twinx()
ax2.plot(x, ipc_impr, 's-', color=COLORS_DARK['open_page'],
         markersize=4, linewidth=1.0, markerfacecolor=COLORS['open_page'],
         markeredgecolor=COLORS_DARK['open_page'], markeredgewidth=0.6,
         zorder=5)

# Annotate IPC values — alternate above/below to avoid overlap
for i, (xi, yi) in enumerate(zip(x, ipc_impr)):
    y_off = 7 if i % 2 == 0 else -12
    va = 'bottom' if i % 2 == 0 else 'top'
    ax2.annotate(f'+{yi:.1f}%', (xi, yi),
                 textcoords='offset points', xytext=(0, y_off),
                 fontsize=FONT_DETAIL, fontweight='bold',
                 color=COLORS_DARK['open_page'], ha='center', va=va)

ax2.set_ylabel('IPC Improvement (%)',
               color=COLORS_DARK['open_page'])
ax2.set_ylim(0, 8)
ax2.tick_params(axis='y', labelcolor=COLORS_DARK['open_page'])

# Legend
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
legend_elements = [
    Patch(facecolor=COLORS['closed_page'], edgecolor='white',
          label='Acc. < 50%'),
    Patch(facecolor=COLORS['craft'], edgecolor='white',
          label='Acc. ≥ 50%'),
    Line2D([0], [0], marker='s', color=COLORS_DARK['open_page'],
           markerfacecolor=COLORS['open_page'],
           markeredgecolor=COLORS_DARK['open_page'],
           markersize=4, linewidth=1.0,
           label='IPC Impr.'),
]
ax1.legend(handles=legend_elements, loc='upper left', ncol=3,
           fontsize=FONT_ANNOT, framealpha=0.9, edgecolor='gray',
           fancybox=False)

fig.tight_layout()
savefig(fig, 'timeout_accuracy')
