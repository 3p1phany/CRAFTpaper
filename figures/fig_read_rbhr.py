#!/usr/bin/env python3
"""Figure: Read Row Buffer Hit Rate (%) grouped bar chart for top-12 benchmarks."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

setup_style()

# ── data (from craft_final_evaluation.md, Read Row Buffer Hit Rate table) ─
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

# Read Row Buffer Hit Rate (%)
craft = [91.15, 71.30, 34.46, 82.03, 87.85, 62.64, 89.44, 83.97, 90.17, 93.21, 36.90, 72.88]
abp   = [72.13, 60.81, 25.13, 63.80, 53.21, 55.96, 70.89, 47.47, 78.59, 65.85, 26.78, 52.64]
dympl = [81.90, 63.29, 29.16, 75.20, 80.09, 56.60, 84.09, 74.83, 84.48, 88.23, 31.98, 66.20]
intap = [81.56, 64.86, 32.87, 74.96, 76.17, 58.48, 80.46, 74.85, 86.71, 86.93, 35.08, 66.17]

# Compute averages
craft_avg = sum(craft) / len(craft)
abp_avg   = sum(abp)   / len(abp)
dympl_avg = sum(dympl)  / len(dympl)
intap_avg = sum(intap)  / len(intap)

craft.append(craft_avg)
abp.append(abp_avg)
dympl.append(dympl_avg)
intap.append(intap_avg)

labels = [short_name(b) for b in benchmarks] + ['Average']
n = len(labels)
x = np.arange(n)

# ── plot ─────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(LNCS_TEXT_WIDTH, 2.7))

bar_w = 0.17
policies = ['ABP', 'DYMPL', 'INTAP', r'$\bf{CRAFT}$']
values   = [abp, dympl, intap, craft]
color_keys = ['abp', 'dympl', 'intap', 'craft']

for i, (p, vals, ck) in enumerate(zip(policies, values, color_keys)):
    offset = (i - 1.5) * bar_w
    ax.bar(x + offset, vals, bar_w,
           label=p, color=COLORS[ck], hatch=HATCHES[ck],
           edgecolor='black', linewidth=0.8)

# Axis styling
ax.set_ylim(0, 105)
ax.set_yticks(np.arange(0, 101, 20))
ax.yaxis.set_minor_locator(mticker.MultipleLocator(10))

ax.set_ylabel('Read Row Buffer Hit Rate (%)')
set_categorical_xticks(ax, x, labels, rotation=35, ha='right')
tick_labels = ax.get_xticklabels()
tick_labels[-1].set_fontweight('bold')

# Average separator
ax.axvline(x=n - 1.5, color='gray', linestyle='--', linewidth=0.8)

ax.legend(loc='upper center', ncol=4, fontsize=FONT_LEGEND,
          framealpha=0.9, edgecolor='gray', fancybox=False,
          bbox_to_anchor=(0.5, 1.15))
ax.grid(axis='y', linestyle=':', alpha=0.3)
ax.set_xlim(-0.6, n - 0.4)

fig.tight_layout()
savefig(fig, 'read_rbhr')
