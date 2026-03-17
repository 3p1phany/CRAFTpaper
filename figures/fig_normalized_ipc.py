#!/usr/bin/env python3
"""Figure: Normalized IPC bar chart (CRAFT = 1.0) for top-12 benchmarks."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

setup_style()

# ── data (from craft_final_evaluation.md, Normalized IPC table) ──────────
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

# Normalized IPC values (CRAFT = 1.0)
abp   = [0.8913, 0.9288, 0.9247, 0.9335, 0.9067, 0.9626, 0.9249, 0.8963, 0.9261, 0.9243, 0.9219, 0.9480]
dympl = [0.9450, 0.9464, 0.9641, 0.9723, 0.9747, 0.9699, 0.9804, 0.9736, 0.9729, 0.9838, 0.9809, 0.9842]
intap = [0.9452, 0.9699, 0.9721, 0.9494, 0.9636, 0.9802, 0.9648, 0.9814, 0.9829, 0.9830, 0.9840, 0.9806]
craft = [1.0] * 12

# Compute GEOMEAN
abp_geo   = math.exp(sum(math.log(v) for v in abp)   / len(abp))
dympl_geo = math.exp(sum(math.log(v) for v in dympl) / len(dympl))
intap_geo = math.exp(sum(math.log(v) for v in intap) / len(intap))

abp.append(abp_geo)
dympl.append(dympl_geo)
intap.append(intap_geo)
craft.append(1.0)

labels = [short_name(b) for b in benchmarks] + ['GEOMEAN']
n = len(labels)
x = np.arange(n)

# ── plot ─────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 4.5))

bar_w = 0.19
policies = ['ABP', 'DYMPL', 'INTAP', 'CRAFT']
values   = [abp, dympl, intap, craft]
colors   = [COLORS['abp'], COLORS['dympl'], COLORS['intap'], COLORS['craft']]

for i, (p, vals, c) in enumerate(zip(policies, values, colors)):
    offset = (i - 1.5) * bar_w
    bars = ax.bar(x + offset, vals, bar_w,
                  label=p, color=c, edgecolor='white', linewidth=0.5)

# Axis styling
ymin = 0.86
ax.set_ylim(ymin, 1.02)
ax.set_yticks(np.arange(ymin, 1.021, 0.02))
ax.yaxis.set_minor_locator(mticker.MultipleLocator(0.01))

ax.set_ylabel('Normalized IPC (CRAFT = 1.0)', fontsize=11)
ax.set_xticks(x)
ax.set_xticklabels(labels, rotation=35, ha='right', fontsize=9)

# GEOMEAN separator
ax.axvline(x=n - 1.5, color='gray', linestyle='--', linewidth=0.8)

# Reference line at 1.0
ax.axhline(y=1.0, color='black', linestyle='-', linewidth=0.6, zorder=0)

# Loss annotations for GEOMEAN
geo_vals = {'ABP': abp_geo, 'DYMPL': dympl_geo, 'INTAP': intap_geo}
geo_colors = {'ABP': COLORS_DARK['abp'], 'DYMPL': COLORS_DARK['dympl'], 'INTAP': COLORS_DARK['intap']}
for i, (p, gv) in enumerate(geo_vals.items()):
    offset = (i - 1.5) * bar_w
    loss = (1.0 - gv) * 100
    ax.text(n - 1 + offset, gv - 0.004, f'-{loss:.1f}%',
            ha='center', va='top', fontsize=7, fontweight='bold',
            color=geo_colors[p])

ax.legend(loc='upper center', ncol=4, fontsize=10,
          framealpha=0.9, edgecolor='gray', fancybox=False,
          bbox_to_anchor=(0.5, 1.12))
ax.grid(axis='y', linestyle=':', alpha=0.3)
ax.set_xlim(-0.6, n - 0.4)

fig.tight_layout()
savefig(fig, 'normalized_ipc')
