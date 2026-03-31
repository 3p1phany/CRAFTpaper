#!/usr/bin/env python3
"""Figure: Combined DRAM-level performance — (a) Read RBHR, (b) Read Latency."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from matplotlib.patches import Patch
import matplotlib.gridspec as gridspec

setup_style()

# ── data ────────────────────────────────────────────────────────────────────
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
rbhr_craft = [91.15, 71.30, 34.46, 82.03, 87.85, 62.64, 89.44, 83.97, 90.17, 93.21, 36.90, 72.88]
rbhr_abp   = [72.13, 60.81, 25.13, 63.80, 53.21, 55.96, 70.89, 47.47, 78.59, 65.85, 26.78, 52.64]
rbhr_dympl = [81.90, 63.29, 29.16, 75.20, 80.09, 56.60, 84.09, 74.83, 84.48, 88.23, 31.98, 66.20]
rbhr_intap = [81.56, 64.86, 32.87, 74.96, 76.17, 58.48, 80.46, 74.85, 86.71, 86.93, 35.08, 66.17]

# Averages
rbhr_craft.append(sum(rbhr_craft) / 12)
rbhr_abp.append(sum(rbhr_abp) / 12)
rbhr_dympl.append(sum(rbhr_dympl) / 12)
rbhr_intap.append(sum(rbhr_intap) / 12)

# Average Read Latency (DRAM cycles)
lat_craft = [95.32, 107.86, 111.80, 90.99, 82.31, 109.56, 124.94, 79.15, 89.70, 134.11, 112.85, 96.51]
lat_abp   = [111.47, 116.80, 119.71, 101.30, 104.28, 113.56, 133.72, 98.78, 94.89, 148.35, 115.68, 107.06]
lat_dympl = [104.99, 115.43, 115.73, 95.41, 87.43, 114.27, 128.34, 83.75, 94.80, 137.52, 113.44, 100.19]
lat_intap = [101.04, 109.88, 112.97, 94.28, 88.41, 110.05, 128.32, 83.58, 90.83, 137.86, 113.10, 99.21]

lat_craft.append(sum(lat_craft) / 12)
lat_abp.append(sum(lat_abp) / 12)
lat_dympl.append(sum(lat_dympl) / 12)
lat_intap.append(sum(lat_intap) / 12)

labels = [short_name(b) for b in benchmarks] + ['AVG']
n = len(labels)
x = np.arange(n)

# Hatch patterns matching fig_normalized_ipc.py
_HATCHES = {
    'abp':   '\\\\',
    'dympl': '//',
    'intap': '--',
    'craft': '',
}

# ── plot ────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(LNCS_TEXT_WIDTH, 4.2))
gs = gridspec.GridSpec(2, 1, hspace=0.45)
ax_a = fig.add_subplot(gs[0])
ax_b = fig.add_subplot(gs[1])

bar_w = 0.19
policies = ['ABP', 'DYMPL', 'INTAP', 'CRAFT']
color_keys = ['abp', 'dympl', 'intap', 'craft']

# ── (a) Read RBHR ──────────────────────────────────────────────────────────
rbhr_vals = [rbhr_abp, rbhr_dympl, rbhr_intap, rbhr_craft]
for i, (p, vals, ck) in enumerate(zip(policies, rbhr_vals, color_keys)):
    offset = (i - 1.5) * bar_w
    edge_lw = 1.2 if ck == 'craft' else 0.8
    edge_col = COLORS_DARK['craft'] if ck == 'craft' else 'black'
    ax_a.bar(x + offset, vals, bar_w,
             label=p, color=COLORS[ck], hatch=_HATCHES[ck],
             edgecolor=edge_col, linewidth=edge_lw)

ax_a.set_ylim(0, 105)
ax_a.set_yticks(np.arange(0, 101, 20))
ax_a.yaxis.set_minor_locator(mticker.MultipleLocator(10))
ax_a.set_ylabel('Read Row Buffer\nHit Rate (%)')
set_categorical_xticks(ax_a, x, labels, rotation=35, ha='right')
tick_labels_a = ax_a.get_xticklabels()
tick_labels_a[-1].set_fontweight('bold')
ax_a.axvline(x=n - 1.5, color='gray', linestyle='--', linewidth=0.8)
ax_a.grid(axis='y', linestyle=':', alpha=0.3)
ax_a.set_xlim(-0.6, n - 0.4)
ax_a.text(-0.08, 1.05, '(a)', transform=ax_a.transAxes,
          fontsize=FONT_TITLE, fontweight='bold', va='bottom')

# ── (b) Read Latency ──────────────────────────────────────────────────────
lat_vals = [lat_abp, lat_dympl, lat_intap, lat_craft]
for i, (p, vals, ck) in enumerate(zip(policies, lat_vals, color_keys)):
    offset = (i - 1.5) * bar_w
    edge_lw = 1.2 if ck == 'craft' else 0.8
    edge_col = COLORS_DARK['craft'] if ck == 'craft' else 'black'
    ax_b.bar(x + offset, vals, bar_w,
             label=p, color=COLORS[ck], hatch=_HATCHES[ck],
             edgecolor=edge_col, linewidth=edge_lw)

ax_b.set_ylim(70, 160)
ax_b.set_yticks(np.arange(70, 161, 20))
ax_b.yaxis.set_minor_locator(mticker.MultipleLocator(10))
ax_b.set_ylabel('Avg Read Latency\n(DRAM Cycles)')
set_categorical_xticks(ax_b, x, labels, rotation=35, ha='right')
tick_labels_b = ax_b.get_xticklabels()
tick_labels_b[-1].set_fontweight('bold')
ax_b.axvline(x=n - 1.5, color='gray', linestyle='--', linewidth=0.8)
ax_b.grid(axis='y', linestyle=':', alpha=0.3)
ax_b.set_xlim(-0.6, n - 0.4)
ax_b.text(-0.08, 1.05, '(b)', transform=ax_b.transAxes,
          fontsize=FONT_TITLE, fontweight='bold', va='bottom')

# ── Shared legend ──────────────────────────────────────────────────────────
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
legend = fig.legend(handles=legend_handles, loc='upper center', ncol=4,
                    fontsize=FONT_LEGEND, framealpha=0.9, edgecolor='gray',
                    fancybox=False, bbox_to_anchor=(0.5, -0.01),
                    handlelength=1.8, handleheight=0.8, columnspacing=1.0)
legend.get_texts()[-1].set_fontweight('bold')

fig.tight_layout()
fig.subplots_adjust(bottom=0.08)
savefig(fig, 'dram_level')
