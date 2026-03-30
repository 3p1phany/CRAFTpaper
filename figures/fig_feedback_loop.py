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
fig, ax = plt.subplots(figsize=(LNCS_TEXT_WIDTH, 3.0))
ax.set_xlim(-1.0, 8.0)
ax.set_ylim(-0.2, 5.0)
ax.axis('off')

# Scale factor for fonts (proportional to width reduction)
_sf = LNCS_TEXT_WIDTH / 7.5

# ── Colors (from unified palette) ─────────────────────────────────────────
C_W  = COLORS['closed_page']   # Wrong  — brick red
C_R  = COLORS['craft']         # Right  — forest green
C_C  = COLORS['dympl']         # Conflict — orange
C_B  = COLORS['open_page']     # Timeout box — blue
C_G  = COLORS_DARK['abp']      # Gray text

C_WB = COLORS_BG['closed_page']  # Wrong background
C_RB = COLORS_BG['craft']        # Right background
C_CB = COLORS_BG['dympl']        # Conflict background
C_BB = COLORS_BG['open_page']    # Timeout background

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
top_cx, top_cy = 3.5, 4.20
top_w, top_h = 4.6, 0.68

mid_cx, mid_cy = 3.5, 2.98
mid_w, mid_h = 3.6, 0.64

bw, bh = 2.3, 1.65
bot_y = 0.95
bot_xs = [0.85, 3.5, 6.15]        # WRONG, RIGHT, CONFLICT
bot_top = bot_y + bh / 2          # top edge of outcome boxes

# FancyBboxPatch pad=0.06 expands the actual drawn border 0.06 units outward.
# Add a small visual gap (0.03) so arrow tips sit just outside the visible edge.
_BOX_PAD = 0.06 + 0.03

# ── TOP: Per-Bank Timeout Counter ─────────────────────────────────────────
rbox(top_cx, top_cy, top_w, top_h, C_BB, C_B, lw=1.8)
ax.text(top_cx, top_cy + 0.13, 'Per-Bank Timeout Counter',
        fontsize=FONT_TITLE, fontweight='bold', ha='center', va='center', color='#222')
ax.text(top_cx, top_cy - 0.17, 'timeout  [50, 3200] cycles   init = 200',
        fontsize=FONT_ANNOT, ha='center', va='center', color=C_G, fontstyle='italic')

# ── Arrow: Timeout → Classify (straight down) ────────────────────────────
ortho_arrow(
    [(top_cx, top_cy - top_h / 2 - _BOX_PAD),
     (mid_cx, mid_cy + mid_h / 2 + _BOX_PAD)],
    color=C_B, lw=1.3)

# ── MIDDLE: Classify Outcome (with "timeout expires" inside) ─────────────
rbox(mid_cx, mid_cy, mid_w, mid_h, '#F5F5F5', '#888', lw=1.0)
ax.text(mid_cx, mid_cy + 0.12, 'Timeout Expires',
        fontsize=FONT_DETAIL, color=C_G, ha='center', va='center', fontstyle='italic')
ax.text(mid_cx, mid_cy - 0.12, 'Classify Precharge Outcome',
        fontsize=FONT_TICK, fontweight='bold', ha='center', va='center', color='#333')

# ── Arrows: Classify → three outcome boxes (right-angle tree) ────────────
junction_y = 2.30

# CENTER (RIGHT) — straight down, no turn
ortho_arrow(
    [(mid_cx, mid_cy - mid_h / 2 - _BOX_PAD),
     (mid_cx, bot_top + 0.05)],
    color=C_G, lw=1.3)

# LEFT (WRONG) — down then left then down
wx = bot_xs[0]
ortho_arrow(
    [(mid_cx, mid_cy - mid_h / 2 - _BOX_PAD),
     (mid_cx, junction_y),
     (wx, junction_y),
     (wx, bot_top + 0.05)],
    color=C_G, lw=1.3)

# RIGHT side (CONFLICT) — down then right then down
ccx = bot_xs[2]
ortho_arrow(
    [(mid_cx, mid_cy - mid_h / 2 - _BOX_PAD),
     (mid_cx, junction_y),
     (ccx, junction_y),
     (ccx, bot_top + 0.05)],
    color=C_G, lw=1.3)

# ── BOTTOM: Three outcome boxes ──────────────────────────────────────────

# ── WRONG ─────────────────────────────────────────────────────────────────
rbox(wx, bot_y, bw, bh, C_WB, C_W, lw=1.5)
ax.text(wx, 1.60, 'WRONG',
        fontsize=FONT_TICK, fontweight='bold', color=C_W, ha='center')
ax.text(wx, 1.37, 'new_row = prev_row',
        fontsize=FONT_DETAIL, color=C_G, ha='center')
ax.text(wx, 1.14, 'Penalty: tRP + tRCD',
        fontsize=FONT_ANNOT, fontweight='bold', color='#444', ha='center')
ax.plot([wx - bw * 0.35, wx + bw * 0.35], [0.97, 0.97],
        color=C_W, lw=0.6, alpha=0.4)
ax.text(wx, 0.77, 'ESCALATE',
        fontsize=FONT_ANNOT, fontweight='bold', color=C_W, ha='center')
ax.text(wx, 0.52, 'timeout += B * 2^streak',
        fontsize=FONT_DETAIL, color='#333', ha='center')
ax.text(wx, 0.27, '(exponential backoff)',
        fontsize=FONT_DETAIL, color=C_G, ha='center', fontstyle='italic')

# ── RIGHT ─────────────────────────────────────────────────────────────────
rx = bot_xs[1]
rbox(rx, bot_y, bw, bh, C_RB, C_R, lw=1.5)
ax.text(rx, 1.60, 'RIGHT',
        fontsize=FONT_TICK, fontweight='bold', color=C_R, ha='center')
ax.text(rx, 1.37, u'new_row \u2260 prev_row',
        fontsize=FONT_DETAIL, color=C_G, ha='center')
ax.text(rx, 1.14, 'Saved: tRP',
        fontsize=FONT_ANNOT, fontweight='bold', color='#444', ha='center')
ax.plot([rx - bw * 0.35, rx + bw * 0.35], [0.97, 0.97],
        color=C_R, lw=0.6, alpha=0.4)
ax.text(rx, 0.77, 'NO CHANGE',
        fontsize=FONT_ANNOT, fontweight='bold', color=C_R, ha='center')
ax.text(rx, 0.52, 'right_streak++',
        fontsize=FONT_DETAIL, color='#333', ha='center')
ax.text(rx, 0.27, '(timeout confirmed)',
        fontsize=FONT_DETAIL, color=C_G, ha='center', fontstyle='italic')

# ── CONFLICT ──────────────────────────────────────────────────────────────
rbox(ccx, bot_y, bw, bh, C_CB, C_C, lw=1.5)
ax.text(ccx, 1.60, 'CONFLICT',
        fontsize=FONT_TICK, fontweight='bold', color=C_C, ha='center')
ax.text(ccx, 1.37, 'on-demand precharge',
        fontsize=FONT_DETAIL, color=C_G, ha='center')
ax.text(ccx, 1.14, 'Penalty: tRP',
        fontsize=FONT_ANNOT, fontweight='bold', color='#444', ha='center')
ax.plot([ccx - bw * 0.35, ccx + bw * 0.35], [0.97, 0.97],
        color=C_C, lw=0.6, alpha=0.4)
ax.text(ccx, 0.77, 'DE-ESCALATE',
        fontsize=FONT_ANNOT, fontweight='bold', color=C_C, ha='center')
ax.text(ccx, 0.52, 'timeout -= B * tRP / (tRP + tRCD)',
        fontsize=FONT_DETAIL, color='#333', ha='center')
ax.text(ccx, 0.27, '(cost-proportional)',
        fontsize=FONT_DETAIL, color=C_G, ha='center', fontstyle='italic')

# ── Feedback arrows (right-angle, native path) ───────────────────────────
fb_lw, fb_ms = 2.2, 14

# WRONG → Timeout (escalate — left side, 3-segment L)
lx = wx - bw / 2 - 0.35
wy_mid = bot_y + 0.25
wy_top = top_cy - 0.10
ortho_arrow(
    [(wx - bw / 2 - _BOX_PAD, wy_mid),
     (lx, wy_mid),
     (lx, wy_top),
     (top_cx - top_w / 2, wy_top)],
    color=C_W, lw=fb_lw, ms=fb_ms)

# CONFLICT → Timeout (de-escalate — right side, 3-segment L)
rrx = ccx + bw / 2 + 0.35
cy_mid = bot_y + 0.25
cy_top = top_cy - 0.10
ortho_arrow(
    [(ccx + bw / 2 + _BOX_PAD, cy_mid),
     (rrx, cy_mid),
     (rrx, cy_top),
     (top_cx + top_w / 2, cy_top)],
    color=C_C, lw=fb_lw, ms=fb_ms)

# ── Save ──────────────────────────────────────────────────────────────────
savefig(fig, 'feedback_loop')
