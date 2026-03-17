#!/usr/bin/env python3
"""
Fig: CRAFT Core Feedback Loop.

Schematic showing the three precharge outcomes, their costs,
and the resulting asymmetric timeout adjustments forming
a closed-loop control mechanism.
"""
from common import *
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

setup_style()
fig, ax = plt.subplots(figsize=(7, 4.8))
ax.set_xlim(-0.6, 7.6)
ax.set_ylim(-0.15, 5.0)
ax.axis('off')

# ── Colors ────────────────────────────────────────────────────────────────
C_W  = '#C0504D'       # Wrong  — brick red
C_R  = '#548235'       # Right  — forest green
C_C  = '#ED7D31'       # Conflict — orange
C_B  = '#4472C4'       # Timeout box — blue
C_G  = '#555555'       # Gray text

C_WB = '#FCEAEA'       # Wrong background
C_RB = '#E8F0E0'       # Right background
C_CB = '#FFF3E6'       # Conflict background
C_BB = '#E8EEF5'       # Timeout background

# ── Helper ────────────────────────────────────────────────────────────────
def rbox(cx, cy, w, h, fc, ec, lw=1.3):
    b = FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle="round,pad=0.06",
        fc=fc, ec=ec, lw=lw, zorder=2)
    ax.add_patch(b)

# ── TOP: Per-Bank Timeout Counter ─────────────────────────────────────────
rbox(3.5, 4.4, 4.2, 0.8, C_BB, C_B, lw=1.5)
ax.text(3.5, 4.55, 'Per-Bank Timeout Counter',
        fontsize=10.5, fontweight='bold', ha='center', va='center', color='#222')
ax.text(3.5, 4.2, r'$\tau$ $\in$ [50, 3200] cycles   ·   init = 200',
        fontsize=8.5, ha='center', va='center', color=C_G)

# ── Arrow: Timeout → Classify ─────────────────────────────────────────────
ax.annotate('', xy=(3.5, 3.45), xytext=(3.5, 4.0),
            arrowprops=dict(arrowstyle='->', color=C_G, lw=1.2))
ax.text(5.55, 3.7,
        r'$\tau$ expires $\rightarrow$ speculative PRE $\rightarrow$ next ACT',
        fontsize=7.5, ha='center', va='center', color=C_G, fontstyle='italic')

# ── MIDDLE: Classify Outcome ─────────────────────────────────────────────
rbox(3.5, 3.05, 4.2, 0.55, '#F5F5F5', '#888', lw=1.0)
ax.text(3.5, 3.05, 'Classify Precharge Outcome',
        fontsize=10, fontweight='bold', ha='center', va='center', color='#333')

# ── Arrows to three outcome boxes ─────────────────────────────────────────
for sx, tx, c in [(2.3, 1.2, C_W), (3.5, 3.5, C_R), (4.7, 5.8, C_C)]:
    ax.annotate('', xy=(tx, 2.12), xytext=(sx, 2.78),
                arrowprops=dict(arrowstyle='->', color=c, lw=1.2))

# ── BOTTOM: Three outcome boxes ──────────────────────────────────────────
bw, bh = 2.2, 1.95

# ── WRONG ─────────────────────────────────────────────────────────────────
rbox(1.2, 1.05, bw, bh, C_WB, C_W, lw=1.5)
ax.text(1.2, 1.82, 'WRONG',
        fontsize=11, fontweight='bold', color=C_W, ha='center')
ax.text(1.2, 1.52, 'new_row = prev_row',
        fontsize=7.5, color=C_G, ha='center')
ax.text(1.2, 1.22, 'Penalty: tRP + tRCD',
        fontsize=8, fontweight='bold', color='#444', ha='center')
ax.text(1.2, 0.82, 'ESCALATE',
        fontsize=9.5, fontweight='bold', color=C_W, ha='center')
ax.text(1.2, 0.52, r'$\tau$ += B $\cdot$ 2$^{streak}$',
        fontsize=8.5, color='#333', ha='center')
ax.text(1.2, 0.24, '(exponential backoff)',
        fontsize=7, color=C_G, ha='center', fontstyle='italic')

# ── RIGHT ─────────────────────────────────────────────────────────────────
rbox(3.5, 1.05, bw, bh, C_RB, C_R, lw=1.5)
ax.text(3.5, 1.82, 'RIGHT',
        fontsize=11, fontweight='bold', color=C_R, ha='center')
ax.text(3.5, 1.52, 'new_row \u2260 prev_row',
        fontsize=7.5, color=C_G, ha='center')
ax.text(3.5, 1.22, 'Saved: tRP',
        fontsize=8, fontweight='bold', color='#444', ha='center')
ax.text(3.5, 0.82, 'NO CHANGE',
        fontsize=9.5, fontweight='bold', color=C_R, ha='center')
ax.text(3.5, 0.52, 'right_streak++',
        fontsize=8.5, color='#333', ha='center')
ax.text(3.5, 0.24, '(timeout confirmed)',
        fontsize=7, color=C_G, ha='center', fontstyle='italic')

# ── CONFLICT ──────────────────────────────────────────────────────────────
rbox(5.8, 1.05, bw, bh, C_CB, C_C, lw=1.5)
ax.text(5.8, 1.82, 'CONFLICT',
        fontsize=11, fontweight='bold', color=C_C, ha='center')
ax.text(5.8, 1.52, 'on-demand precharge',
        fontsize=7.5, color=C_G, ha='center')
ax.text(5.8, 1.22, 'Penalty: tRP',
        fontsize=8, fontweight='bold', color='#444', ha='center')
ax.text(5.8, 0.82, 'DE-ESCALATE',
        fontsize=9.5, fontweight='bold', color=C_C, ha='center')
ax.text(5.8, 0.52, r'$\tau$ $-$= B $\cdot$ tRP/(tRP+tRCD)',
        fontsize=8.5, color='#333', ha='center')
ax.text(5.8, 0.24, '(cost-proportional)',
        fontsize=7, color=C_G, ha='center', fontstyle='italic')

# ── Feedback arrows ───────────────────────────────────────────────────────
# WRONG → Timeout (escalate via left side)
fb_w = FancyArrowPatch(
    posA=(0.1, 1.3), posB=(1.4, 4.55),
    arrowstyle='->', color=C_W, lw=2.0, mutation_scale=15,
    connectionstyle='arc3,rad=-0.35', zorder=3)
ax.add_patch(fb_w)
ax.text(-0.35, 3.1, r'$\tau$ $\uparrow$',
        fontsize=11, fontweight='bold', color=C_W,
        ha='center', va='center', rotation=90)

# CONFLICT → Timeout (de-escalate via right side)
fb_c = FancyArrowPatch(
    posA=(6.9, 1.3), posB=(5.6, 4.55),
    arrowstyle='->', color=C_C, lw=2.0, mutation_scale=15,
    connectionstyle='arc3,rad=0.35', zorder=3)
ax.add_patch(fb_c)
ax.text(7.35, 3.1, r'$\tau$ $\downarrow$',
        fontsize=11, fontweight='bold', color=C_C,
        ha='center', va='center', rotation=-90)

# ── Save ──────────────────────────────────────────────────────────────────
savefig(fig, 'feedback_loop')
