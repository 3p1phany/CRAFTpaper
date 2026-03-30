#!/usr/bin/env python3
"""Figure: Ablation study — stacked bar: BASE foundation + feature contribution."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

setup_style()
# Figure is saved at LNCS_TEXT_WIDTH but included at 0.7×textwidth.
_PRINT_SCALE = 0.7

# LNCS compliance: override font sizes (minimum 7 pt for readability in print)
_FONT_AXIS  = FONT_AXIS_LABEL  # axis label — match Fig 4
_FONT_TICK  = FONT_TICK  # tick labels — match Fig 4
_FONT_ANNOT = 7   # bar annotations and category labels
plt.rcParams.update({
    'axes.labelsize':   _FONT_AXIS,
    'ytick.labelsize':  _FONT_TICK,
})

# ── data (from craft_final_evaluation.md, ablation results) ──────────────
# GEOMEAN IPC improvement over best baseline per benchmark (%)
variants = [
    'BASE',       # Core feedback loop only
    '+RS',        # Right Streak de-escalation
    '+RW',        # Read/Write cost differentiation
    '+SD',        # Streak Decay
    '+PR',        # Phase Reset
    '+QDSD',      # Queue-Depth Scaled De-escalation
    'PRE',        # RS + RW + SD
    'ALL',        # All five enhancements
]
geomean_abs = [0.653, 0.704, 0.775, 0.699, 0.613, 0.653, 0.861, 0.789]

# Normalize: BASE improvement = 100%
base_val = geomean_abs[0]
ratios = [g / base_val * 100 for g in geomean_abs]
deltas = [r - 100.0 for r in ratios]

# Category colors for delta segments
delta_colors = [
    COLORS['craft'],       # BASE (delta=0, invisible)
    COLORS['open_page'],   # +RS
    COLORS['open_page'],   # +RW
    COLORS['open_page'],   # +SD
    COLORS['closed_page'], # +PR
    COLORS['closed_page'], # +QDSD
    COLORS['craft'],       # PRECHARGE
    COLORS['abp'],         # ALL
]
delta_dark = [
    COLORS_DARK['craft'],
    COLORS_DARK['open_page'],
    COLORS_DARK['open_page'],
    COLORS_DARK['open_page'],
    COLORS_DARK['closed_page'],
    COLORS_DARK['closed_page'],
    COLORS_DARK['craft'],
    COLORS_DARK['abp'],
]

n = len(variants)
x = np.arange(n)

# ── plot ─────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(LNCS_TEXT_WIDTH, 2.8))

# Base portion: all bars share BASE = 100% (light fill)
ax.bar(x, [100.0] * n, width=0.40, color=COLORS['craft'], alpha=0.25,
       edgecolor='black', linewidth=0.8, label='Core Loop (BASE)')

# Delta portion stacked on top of BASE
# Positive deltas extend upward; negative deltas extend downward into base
ax.bar(x, deltas, width=0.40, bottom=[100.0] * n,
       color=delta_colors, edgecolor='black', linewidth=0.8,
       label='Feature Contribution')

# Highlight PRECHARGE bar with a thicker edge
precharge_idx = 6
ax.bar(x[precharge_idx], deltas[precharge_idx], width=0.40, bottom=100.0,
       color=delta_colors[precharge_idx],
       edgecolor=COLORS_DARK['craft'], linewidth=1.5)

# Reference line at BASE = 100%
ax.axhline(y=100, color=COLORS_DARK['craft'], linestyle='--',
           linewidth=0.8, alpha=0.6, zorder=0)

# ── annotations ──────────────────────────────────────────────────────────
for i, (v, r, d) in enumerate(zip(variants, ratios, deltas)):
    if i == 0:
        ax.text(i, 101.5, '100%', ha='center', va='bottom',
                fontsize=_FONT_ANNOT, fontweight='bold', color=COLORS_DARK['craft'])
    elif d > 0.5:
        ax.text(i, r + 1.5, f'+{d:.1f}%', ha='center', va='bottom',
                fontsize=_FONT_ANNOT, fontweight='bold', color=delta_dark[i])
    elif d < -0.5:
        ax.text(i, r - 1.5, f'{d:.1f}%', ha='center', va='top',
                fontsize=_FONT_ANNOT, fontweight='bold', color=delta_dark[i])
    else:
        ax.text(i, 101.5, '+0.0%', ha='center', va='bottom',
                fontsize=_FONT_ANNOT, fontweight='bold', color=delta_dark[i])

# Category labels below x-axis
cat_y = -0.28
ax.text(0, cat_y, 'Core Loop', ha='center', fontsize=_FONT_ANNOT,
        color=COLORS_DARK['craft'], transform=ax.get_xaxis_transform())
ax.text(2, cat_y, 'Precharge-path', ha='center', fontsize=_FONT_ANNOT,
        color=COLORS_DARK['open_page'], transform=ax.get_xaxis_transform())
ax.text(4.5, cat_y, 'Conflict-path', ha='center', fontsize=_FONT_ANNOT,
        color=COLORS_DARK['closed_page'], transform=ax.get_xaxis_transform())
ax.text(6.5, cat_y, 'Combined', ha='center', fontsize=_FONT_ANNOT,
        color='#444444', transform=ax.get_xaxis_transform())

# Vertical separators between categories
for sep_x in [0.5, 3.5, 5.5]:
    ax.axvline(x=sep_x, color='gray', linestyle=':', linewidth=0.6, alpha=0.4)

# ── axis styling ─────────────────────────────────────────────────────────
ax.set_ylabel('Normalized IPC Gain\n(BASE = 100%)')
set_categorical_xticks(ax, x, variants, rotation=90, ha='center',
                       fontsize=FONT_TICK_DENSE / _PRINT_SCALE)
# Bold key variants
for i, tl in enumerate(ax.get_xticklabels()):
    if variants[i] in ('BASE', 'PRE', 'ALL'):
        tl.set_fontweight('bold')
ax.set_ylim(80, 145)
ax.set_yticks(np.arange(80, 141, 10))
ax.yaxis.set_minor_locator(plt.MultipleLocator(5))
ax.grid(axis='y', linestyle=':', alpha=0.3)
ax.set_xlim(-0.5, n - 0.5)

fig.subplots_adjust(bottom=0.20, top=0.94, left=0.15, right=0.96)
savefig(fig, 'ablation')
