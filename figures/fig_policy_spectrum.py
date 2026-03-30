#!/usr/bin/env python3
"""
Fig: Row Buffer Management Policy Spectrum.

Shows the continuum from pure closed-page to pure open-page,
with timeout-based adaptive strategies positioned in between.
Highlights how timeout value controls the trade-off.
"""

from common import *
import matplotlib.patches as mpatches, matplotlib.patheffects as pe

setup_style()

fig, ax = plt.subplots(figsize=(LNCS_TEXT_WIDTH, 1.8))
ax.set_xlim(-0.5, 10.5)
ax.set_ylim(-0.1, 4.4)
ax.axis('off')

# ── Spectrum bar ──────────────────────────────────────────────────
bar_y = 1.8
bar_h = 0.7

# Gradient bar from closed-page (left) to open-page (right)
n_seg = 200
c_close = np.array([0.753, 0.314, 0.302])  # #C0504D
c_open  = np.array([0.267, 0.447, 0.769])  # #4472C4
for i in range(n_seg):
    frac = i / n_seg
    color = (1 - frac) * c_close + frac * c_open
    x_start = 0.5 + frac * 9.5
    ax.barh(bar_y, 9.5 / n_seg + 0.005, height=bar_h, left=x_start,
            color=color, linewidth=0)

# Border
from matplotlib.patches import Rectangle
rect = Rectangle((0.5, bar_y - bar_h/2), 9.5, bar_h,
                 linewidth=1.2, edgecolor='#333', facecolor='none', zorder=5)
ax.add_patch(rect)

# ── Endpoint labels ───────────────────────────────────────────────
ax.text(0.5, bar_y + bar_h/2 + 0.15, 'Close-Page', ha='center', va='bottom',
        fontsize=FONT_TICK, fontweight='bold', color=COLORS['closed_page'])
ax.text(0.5, bar_y - bar_h/2 - 0.1, 'timeout = 0', ha='center', va='top',
        fontsize=FONT_ANNOT, color='#666', fontstyle='italic')

ax.text(10.0, bar_y + bar_h/2 + 0.15, 'Open-Page', ha='center', va='bottom',
        fontsize=FONT_TICK, fontweight='bold', color=COLORS['open_page'])
ax.text(10.0, bar_y - bar_h/2 - 0.1, r'timeout $\rightarrow \infty$', ha='center', va='top',
        fontsize=FONT_ANNOT, color='#666', fontstyle='italic')

# ── Arrow showing timeout direction ──────────────────────────────
ax.annotate('', xy=(9.3, bar_y - bar_h/2 - 0.55), xytext=(1.2, bar_y - bar_h/2 - 0.55),
            arrowprops=dict(arrowstyle='->', color='#555', lw=1.2))
ax.text(5.25, bar_y - bar_h/2 - 0.75, 'Increasing Timeout Value',
        ha='center', va='top', fontsize=FONT_ANNOT, color='#555', fontstyle='italic')

# ── Strategy markers ─────────────────────────────────────────────
# Positions along the spectrum (0-10 scale)
strategies = [
    # (x_pos, label, sublabel, color, y_offset)
    (1.5,  'INTAP\n(fixed step)', '~200 B/ch', COLORS['intap'], 0),
    (4.5,  'CRAFT\n(cost-asymmetric)', '140 B/ch', COLORS['craft'], 0.4),
    (7.0,  'DYMPL\n(perceptron)', '3.39 KB/ch', COLORS['dympl'], 0),
    (8.8,  'ABP\n(per-row predictor)', '~20 KB/ch', COLORS['abp'], 0.35),
]

marker_base_y = bar_y + bar_h/2 + 0.6

for x, label, sublabel, color, y_off in strategies:
    my = marker_base_y + y_off
    # Vertical line from bar to marker
    ax.plot([x, x], [bar_y + bar_h/2, my], color=color, linewidth=1.2,
            linestyle='--', alpha=0.6, zorder=4)
    # Diamond marker — larger for CRAFT
    ms = 8 if 'CRAFT' in label else 6
    ax.plot(x, my, marker='D', markersize=ms, color=color, zorder=6,
            markeredgecolor='white', markeredgewidth=0.6)
    # Label
    ax.text(x, my + 0.15, label, ha='center', va='bottom',
            fontsize=FONT_DETAIL, fontweight='bold', color=color,
            path_effects=[pe.withStroke(linewidth=2, foreground='white')])

# Hardware cost above
for x, label, sublabel, color, y_off in strategies:
    my = marker_base_y + y_off
    if sublabel:
        ax.text(x, my + 0.15 + 0.30, sublabel, ha='center', va='bottom',
                fontsize=FONT_DETAIL, fontweight='bold', color=color,
                path_effects=[pe.withStroke(linewidth=2, foreground='white')])

# ── Trade-off labels at bottom ────────────────────────────────────
bottom_y = bar_y - bar_h/2 - 0.85
ax.text(0.5, bottom_y, 'Pessimistic on\nrow buffer locality', ha='center', va='center',
        fontsize=FONT_DETAIL, color=COLORS_DARK['closed_page'], fontstyle='italic')
ax.text(10.0, bottom_y, 'Opportunistic on\nrow buffer locality', ha='center', va='center',
        fontsize=FONT_DETAIL, color=COLORS_DARK['open_page'], fontstyle='italic')

plt.tight_layout()
savefig(fig, 'policy_spectrum')
