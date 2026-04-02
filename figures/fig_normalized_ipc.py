#!/usr/bin/env python3
"""Figure: Normalized IPC bar chart (CRAFT = 1.0) for top-12 benchmarks."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from matplotlib.patches import Patch

setup_style()
# Fig 3 is saved at 7.0 in but printed at ~4.32 in (0.9 × LNCS textwidth,
# scale ≈ 0.617). Fig 4 is at LNCS_TEXT_WIDTH printed at 0.7× (scale ≈ 0.70).
# Multiply common.py defaults by 0.70/0.617 ≈ 1.13 so both figures read the
# same size on the printed page.
plt.rcParams.update({
    'font.size':       7,
    'axes.labelsize':  8,
    'ytick.labelsize': 7,
    'legend.fontsize': 7,
})
# Compensate for scale-down: this figure is saved at 7.0 in but included at
# 0.9×textwidth (~4.32 in), so the effective print scale is ~0.617.
_PRINT_SCALE = 0.9 * LNCS_TEXT_WIDTH / 7.0

# Hatch patterns for this figure — chosen for clear visual separation
_HATCHES = {
    'abp':   '\\\\',   # dense backslash diagonal
    'dympl': '//',     # forward diagonal
    'intap': '--',     # horizontal lines
    'craft': '',       # solid — CRAFT is the reference bar, no hatch needed
}

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
fig, ax = plt.subplots(figsize=(7.0, 2.0))

bar_w = 0.22
policies = ['ABP', 'DYMPL', 'INTAP', 'CRAFT']
values   = [abp, dympl, intap, craft]
color_keys = ['abp', 'dympl', 'intap', 'craft']

for i, (p, vals, ck) in enumerate(zip(policies, values, color_keys)):
    offset = (i - 1.5) * bar_w
    edge_lw = 1.2 if ck == 'craft' else 0.8
    edge_col = COLORS_DARK['craft'] if ck == 'craft' else 'black'
    ax.bar(x + offset, vals, bar_w,
           label=p, color=COLORS[ck], hatch=_HATCHES[ck],
           edgecolor=edge_col, linewidth=edge_lw)

# Axis styling
ymin = 0.88
ax.set_ylim(ymin, 1.02)
ax.set_yticks(np.arange(ymin, 1.021, 0.02))
ax.yaxis.set_minor_locator(mticker.MultipleLocator(0.02))

ax.set_ylabel('Normalized IPC (CRAFT = 1.0)')
set_categorical_xticks(ax, x, labels, rotation=35, ha='right',
                       fontsize=FONT_TICK_DENSE / _PRINT_SCALE)
# Bold GEOMEAN label
tick_labels = ax.get_xticklabels()
tick_labels[-1].set_fontweight('bold')

# GEOMEAN separator
ax.axvline(x=n - 1.5, color='gray', linestyle='--', linewidth=0.8)

# Reference line at 1.0
ax.axhline(y=1.0, color='black', linestyle='-', linewidth=0.6, zorder=0)

legend_handles = [
    Patch(facecolor=COLORS['abp'], edgecolor='black',
          hatch=_HATCHES['abp'], linewidth=0.8, label='ABP'),
    Patch(facecolor=COLORS['dympl'], edgecolor='black',
          hatch=_HATCHES['dympl'], linewidth=0.8, label='DYMPL'),
    Patch(facecolor=COLORS['intap'], edgecolor='black',
          hatch=_HATCHES['intap'], linewidth=0.8, label='INTAP'),
    Patch(facecolor=COLORS['craft'], edgecolor=COLORS_DARK['craft'],
          hatch=_HATCHES['craft'], linewidth=1.2, label='CRAFT'),
]
legend = ax.legend(handles=legend_handles, loc='upper center', ncol=4, fontsize=7,
          framealpha=0.9, edgecolor='gray', fancybox=False,
          bbox_to_anchor=(0.5, -0.52), handlelength=1.8,
          handleheight=0.8, columnspacing=1.0)
legend.get_texts()[-1].set_fontweight('bold')
ax.grid(axis='y', linestyle=':', alpha=0.3)
ax.set_xlim(-0.6, n - 0.4)

fig.tight_layout()
fig.subplots_adjust(bottom=0.05)
savefig(fig, 'normalized_ipc')
