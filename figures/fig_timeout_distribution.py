#!/usr/bin/env python3
"""Figure: Timeout distribution stacked bar — Low / Mid / High per benchmark."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

setup_style()

# ── data (from craft_timeout_distribution.tsv) ───────────────────────────
labels_raw = [
    'PR/higgs', 'Comp/pokec', 'CF/higgs', 'CF/pokec',
    'wrf', 'Radii/higgs', 'sphinx3', 'BFSCC/pokec',
    'CF/roadNet', 'Tri/roadNet', 'PR/roadNet', 'TriCnt/roadNet',
]

low  = [96.9, 73.5, 35.7, 36.9, 25.7, 14.8,  9.2,  7.2,  3.9,  6.7,  3.6,  2.8]
mid  = [ 2.9, 19.9, 38.0, 46.7, 17.1, 24.3, 15.8, 18.2, 10.8,  8.3,  5.4,  5.2]
high = [ 0.2,  6.6, 26.3, 16.4, 57.3, 60.9, 75.0, 74.7, 85.2, 85.0, 90.9, 92.0]

# Sort by Low% descending (aggressive close -> balanced -> keep open)
order = sorted(range(len(low)), key=lambda i: low[i], reverse=True)
labels_raw = [labels_raw[i] for i in order]
low  = [low[i]  for i in order]
mid  = [mid[i]  for i in order]
high = [high[i] for i in order]

n = len(labels_raw)
x = np.arange(n)

# ── plot ─────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 4.5))

bar_w = 0.55
color_low  = '#C0504D'   # brick red   — aggressive close
color_mid  = '#ED7D31'   # sandy orange — balanced
color_high = '#4472C4'   # steel blue   — keep open

b1 = ax.bar(x, low, bar_w, label='Low [50, 800)', color=color_low,
            edgecolor='white', linewidth=0.5)
b2 = ax.bar(x, mid, bar_w, bottom=low, label='Mid [800, 2000)', color=color_mid,
            edgecolor='white', linewidth=0.5)
b3 = ax.bar(x, high, bar_w, bottom=[l+m for l, m in zip(low, mid)],
            label='High [2000, 3200]', color=color_high,
            edgecolor='white', linewidth=0.5)

# Percentage labels on dominant segment
for i in range(n):
    vals = [low[i], mid[i], high[i]]
    bottoms = [0, low[i], low[i]+mid[i]]
    max_idx = vals.index(max(vals))
    if vals[max_idx] >= 15:  # only label if segment is large enough
        y_pos = bottoms[max_idx] + vals[max_idx] / 2
        ax.text(i, y_pos, f'{vals[max_idx]:.0f}%',
                ha='center', va='center', fontsize=7, fontweight='bold',
                color='white')

ax.set_ylabel('Distribution (%)', fontsize=11)
ax.set_xticks(x)
ax.set_xticklabels(labels_raw, rotation=35, ha='right', fontsize=9)
ax.set_ylim(0, 105)

# Region annotations
ax.annotate('Aggressive\nClose', xy=(1, 102), fontsize=8, ha='center',
            fontstyle='italic', color=COLORS_DARK['closed_page'])
ax.annotate('Balanced', xy=(4, 102), fontsize=8, ha='center',
            fontstyle='italic', color=COLORS_DARK['dympl'])
ax.annotate('Keep Open', xy=(9, 102), fontsize=8, ha='center',
            fontstyle='italic', color=COLORS_DARK['open_page'])

# Separator lines
ax.axvline(x=2.5, color='gray', linestyle=':', linewidth=0.8, alpha=0.5)
ax.axvline(x=5.5, color='gray', linestyle=':', linewidth=0.8, alpha=0.5)

ax.legend(loc='upper center', ncol=3, fontsize=10,
          framealpha=0.9, edgecolor='gray', fancybox=False,
          bbox_to_anchor=(0.5, -0.18))
ax.grid(axis='y', linestyle=':', alpha=0.3)

fig.tight_layout()
savefig(fig, 'timeout_distribution')
