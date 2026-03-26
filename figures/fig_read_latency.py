#!/usr/bin/env python3
"""Figure: Average read latency bar chart for top-12 benchmarks."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

setup_style()

# ── data (from craft_final_evaluation.md, Average Read Latency table) ────
benchmarks = [
    'ligra/CF/roadNet-CA',
    'ligra/CF/higgs',
    'ligra/PageRank/higgs',
    'ligra/BFSCC/soc-pokec-short',
    'spec06/sphinx3/ref',
    'ligra/CF/soc-pokec',
    'ligra/Triangle/roadNet-CA',
    'ligra/PageRank/roadNet-CA',
    'crono/Triangle-Counting/roadNet-CA',
    'spec06/wrf/ref',
    'ligra/Components-Shortcut/soc-pokec',
    'ligra/Radii/higgs',
]

# Average read latency in DRAM cycles
craft = [95.32, 107.86, 111.80, 90.99, 82.31, 109.56, 124.94, 79.15, 89.70, 134.11, 112.85, 96.51]
abp   = [111.47, 116.80, 119.71, 101.30, 104.28, 113.56, 133.72, 98.78, 94.89, 148.35, 115.68, 107.06]
dympl = [104.99, 115.43, 115.73, 95.41, 87.43, 114.27, 128.34, 83.75, 94.80, 137.52, 113.44, 100.19]
intap = [101.04, 109.88, 112.97, 94.28, 88.41, 110.05, 128.32, 83.58, 90.83, 137.86, 113.10, 99.21]

# Compute arithmetic mean
craft_avg = sum(craft) / len(craft)
abp_avg   = sum(abp)   / len(abp)
dympl_avg = sum(dympl)  / len(dympl)
intap_avg = sum(intap)  / len(intap)

craft.append(craft_avg)
abp.append(abp_avg)
dympl.append(dympl_avg)
intap.append(intap_avg)

labels = [short_name(b) for b in benchmarks] + ['AVG']
n = len(labels)
x = np.arange(n)

# ── plot ─────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(LNCS_TEXT_WIDTH, 3.5))

bar_w = 0.17
policies = ['ABP', 'DYMPL', 'INTAP', 'CRAFT']
values   = [abp, dympl, intap, craft]
colors   = [COLORS['abp'], COLORS['dympl'], COLORS['intap'], COLORS['craft']]

for i, (p, vals, c) in enumerate(zip(policies, values, colors)):
    offset = (i - 1.5) * bar_w
    ax.bar(x + offset, vals, bar_w,
           label=p, color=c, edgecolor='white', linewidth=0.5)

# Axis styling
ymin = 70
ymax = 160
ax.set_ylim(ymin, ymax)
ax.set_yticks(np.arange(ymin, ymax + 1, 10))
ax.yaxis.set_minor_locator(mticker.MultipleLocator(5))

ax.set_ylabel('Average Read Latency (DRAM Cycles)', fontsize=8)
ax.set_xticks(x)
ax.set_xticklabels(labels, rotation=90, ha='center', fontsize=6)

# AVG separator
ax.axvline(x=n - 1.5, color='gray', linestyle='--', linewidth=0.8)

ax.legend(loc='upper center', ncol=4, fontsize=7,
          framealpha=0.9, edgecolor='gray', fancybox=False,
          bbox_to_anchor=(0.5, 1.15))
ax.grid(axis='y', linestyle=':', alpha=0.3)
ax.set_xlim(-0.6, n - 0.4)
ax.tick_params(axis='y', labelsize=6)

fig.tight_layout()
savefig(fig, 'read_latency')
