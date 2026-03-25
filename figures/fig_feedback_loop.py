#!/usr/bin/env python3
"""
Fig 6: CRAFT Core Feedback Loop.

Schematic showing the three precharge outcomes, their costs,
and the resulting asymmetric timeout adjustments forming
a closed-loop control mechanism.
"""
from common import *
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.path import Path as MPath

setup_style()
fig, ax = plt.subplots(figsize=(7.5, 5.6))
ax.set_xlim(-1.0, 8.0)
ax.set_ylim(-0.3, 5.6)
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

# ── Helpers ───────────────────────────────────────────────────────────────
def rbox(cx, cy, w, h, fc, ec, lw=1.3):
    b = FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle="round,pad=0.06",
        fc=fc, ec=ec, lw=lw, zorder=2)
    ax.add_patch(b)

def ortho_arrow(vertices, color, lw=1.3, ms=13):
    """Arrow along a right-angle polyline path (no seams)."""
    codes = [MPath.MOVETO] + [MPath.LINETO] * (len(vertices) - 1)
    path = MPath(vertices, codes)
    patch = FancyArrowPatch(
        path=path, arrowstyle='->', color=color,
        lw=lw, mutation_scale=ms, zorder=3)
    ax.add_patch(patch)

# ── Layout parameters ────────────────────────────────────────────────────
top_cx, top_cy = 3.5, 4.9
top_w, top_h = 4.6, 0.8

mid_cx, mid_cy = 3.5, 3.45
mid_w, mid_h = 3.6, 0.75          # taller to fit two lines

bw, bh = 2.3, 1.95
bot_y = 1.05
bot_xs = [0.85, 3.5, 6.15]        # WRONG, RIGHT, CONFLICT
bot_top = bot_y + bh / 2          # top edge of outcome boxes

# ── TOP: Per-Bank Timeout Counter ─────────────────────────────────────────
rbox(top_cx, top_cy, top_w, top_h, C_BB, C_B, lw=1.8)
ax.text(top_cx, top_cy + 0.15, 'Per-Bank Timeout Counter',
        fontsize=11, fontweight='bold', ha='center', va='center', color='#222')
ax.text(top_cx, top_cy - 0.2, 'timeout  [50, 3200] cycles   init = 200',
        fontsize=8.5, ha='center', va='center', color=C_G, fontstyle='italic')

# ── Arrow: Timeout → Classify (straight down) ────────────────────────────
ortho_arrow(
    [(top_cx, top_cy - top_h / 2 - 0.02),
     (mid_cx, mid_cy + mid_h / 2 + 0.05)],
    color=C_G, lw=1.3)

# ── MIDDLE: Classify Outcome (with "timeout expires" inside) ─────────────
rbox(mid_cx, mid_cy, mid_w, mid_h, '#F5F5F5', '#888', lw=1.0)
ax.text(mid_cx, mid_cy + 0.14, 'Timeout Expires',
        fontsize=8, color=C_G, ha='center', va='center', fontstyle='italic')
ax.text(mid_cx, mid_cy - 0.14, 'Classify Precharge Outcome',
        fontsize=10, fontweight='bold', ha='center', va='center', color='#333')

# ── Arrows: Classify → three outcome boxes (right-angle tree) ────────────
junction_y = 2.65

# CENTER (RIGHT) — straight down, no turn
ortho_arrow(
    [(mid_cx, mid_cy - mid_h / 2 - 0.02),
     (mid_cx, bot_top + 0.05)],
    color=C_R, lw=1.3)

# LEFT (WRONG) — down then left then down
wx = bot_xs[0]
ortho_arrow(
    [(mid_cx, mid_cy - mid_h / 2 - 0.02),
     (mid_cx, junction_y),
     (wx, junction_y),
     (wx, bot_top + 0.05)],
    color=C_W, lw=1.3)

# RIGHT side (CONFLICT) — down then right then down
ccx = bot_xs[2]
ortho_arrow(
    [(mid_cx, mid_cy - mid_h / 2 - 0.02),
     (mid_cx, junction_y),
     (ccx, junction_y),
     (ccx, bot_top + 0.05)],
    color=C_C, lw=1.3)

# ── BOTTOM: Three outcome boxes ──────────────────────────────────────────

# ── WRONG ─────────────────────────────────────────────────────────────────
rbox(wx, bot_y, bw, bh, C_WB, C_W, lw=1.5)
ax.text(wx, 1.82, 'WRONG',
        fontsize=11, fontweight='bold', color=C_W, ha='center')
ax.text(wx, 1.55, 'new_row = prev_row',
        fontsize=7.5, color=C_G, ha='center')
ax.text(wx, 1.28, 'Penalty: tRP + tRCD',
        fontsize=8, fontweight='bold', color='#444', ha='center')
ax.plot([wx - bw * 0.35, wx + bw * 0.35], [1.08, 1.08],
        color=C_W, lw=0.6, alpha=0.4)
ax.text(wx, 0.85, 'ESCALATE',
        fontsize=9.5, fontweight='bold', color=C_W, ha='center')
ax.text(wx, 0.55, r'timeout += B $\cdot$ 2$^{streak}$',
        fontsize=8, color='#333', ha='center')
ax.text(wx, 0.25, '(exponential backoff)',
        fontsize=7, color=C_G, ha='center', fontstyle='italic')

# ── RIGHT ─────────────────────────────────────────────────────────────────
rx = bot_xs[1]
rbox(rx, bot_y, bw, bh, C_RB, C_R, lw=1.5)
ax.text(rx, 1.82, 'RIGHT',
        fontsize=11, fontweight='bold', color=C_R, ha='center')
ax.text(rx, 1.55, u'new_row \u2260 prev_row',
        fontsize=7.5, color=C_G, ha='center')
ax.text(rx, 1.28, 'Saved: tRP',
        fontsize=8, fontweight='bold', color='#444', ha='center')
ax.plot([rx - bw * 0.35, rx + bw * 0.35], [1.08, 1.08],
        color=C_R, lw=0.6, alpha=0.4)
ax.text(rx, 0.85, 'NO CHANGE',
        fontsize=9.5, fontweight='bold', color=C_R, ha='center')
ax.text(rx, 0.55, 'right_streak++',
        fontsize=8.5, color='#333', ha='center')
ax.text(rx, 0.25, '(timeout confirmed)',
        fontsize=7, color=C_G, ha='center', fontstyle='italic')

# ── CONFLICT ──────────────────────────────────────────────────────────────
rbox(ccx, bot_y, bw, bh, C_CB, C_C, lw=1.5)
ax.text(ccx, 1.82, 'CONFLICT',
        fontsize=11, fontweight='bold', color=C_C, ha='center')
ax.text(ccx, 1.55, 'on-demand precharge',
        fontsize=7.5, color=C_G, ha='center')
ax.text(ccx, 1.28, 'Penalty: tRP',
        fontsize=8, fontweight='bold', color='#444', ha='center')
ax.plot([ccx - bw * 0.35, ccx + bw * 0.35], [1.08, 1.08],
        color=C_C, lw=0.6, alpha=0.4)
ax.text(ccx, 0.85, 'DE-ESCALATE',
        fontsize=9.5, fontweight='bold', color=C_C, ha='center')
ax.text(ccx, 0.55, r'timeout $-$= B $\cdot \frac{tRP}{tRP+tRCD}$',
        fontsize=8, color='#333', ha='center')
ax.text(ccx, 0.25, '(cost-proportional)',
        fontsize=7, color=C_G, ha='center', fontstyle='italic')

# ── Feedback arrows (right-angle, native path) ───────────────────────────
fb_lw, fb_ms = 2.2, 14

# WRONG → Timeout (escalate — left side, 3-segment L)
lx = wx - bw / 2 - 0.35
wy_mid = bot_y + 0.3
wy_top = top_cy - 0.1
ortho_arrow(
    [(wx - bw / 2, wy_mid),
     (lx, wy_mid),
     (lx, wy_top),
     (top_cx - top_w / 2, wy_top)],
    color=C_W, lw=fb_lw, ms=fb_ms)

# CONFLICT → Timeout (de-escalate — right side, 3-segment L)
rrx = ccx + bw / 2 + 0.35
cy_mid = bot_y + 0.3
cy_top = top_cy - 0.1
ortho_arrow(
    [(ccx + bw / 2, cy_mid),
     (rrx, cy_mid),
     (rrx, cy_top),
     (top_cx + top_w / 2, cy_top)],
    color=C_C, lw=fb_lw, ms=fb_ms)

# ── Save ──────────────────────────────────────────────────────────────────
savefig(fig, 'feedback_loop')
