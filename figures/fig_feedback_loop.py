#!/usr/bin/env python3
"""
Fig 3: CRAFT timeout-control logic.

The diagram distinguishes two event sources under a timeout-based policy:
1. The timeout expires and the controller issues a speculative precharge.
   The next access then determines whether the decision was RIGHT or WRONG.
2. A new request arrives before timeout expiration. It becomes either a
   ROW HIT (same row still open) or a CONFLICT (different row requires an
   on-demand precharge).

Only WRONG and CONFLICT adjust the timeout value. RIGHT confirms the current
timeout, while ROW HIT stays outside the precharge feedback path.
"""

from common import *
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from matplotlib.path import Path as MPath


setup_style()
fig, ax = plt.subplots(figsize=(LNCS_TEXT_WIDTH * 1.18, 3.20))
ax.set_xlim(-0.50, 12.50)
ax.set_ylim(-0.10, 5.10)
ax.axis('off')


C_W = COLORS['closed_page']
C_R = COLORS['craft']
C_C = COLORS['dympl']
C_B = COLORS['open_page']
C_G = COLORS_DARK['abp']

C_WB = COLORS_BG['closed_page']
C_RB = COLORS_BG['craft']
C_CB = COLORS_BG['dympl']
C_BB = COLORS_BG['open_page']
C_NB = '#F3F3F3'
C_NE = '#8A8A8A'


def rbox(cx, cy, w, h, fc, ec, lw=1.3, pad=0.06):
    box = FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle=f"round,pad={pad}",
        fc=fc, ec=ec, lw=lw, zorder=2)
    ax.add_patch(box)


def ortho_arrow(vertices, color, lw=1.3, ms=13, capstyle='round', joinstyle='round'):
    codes = [MPath.MOVETO] + [MPath.LINETO] * (len(vertices) - 1)
    path = MPath(vertices, codes)
    patch = FancyArrowPatch(
        path=path,
        arrowstyle='->',
        color=color,
        lw=lw,
        mutation_scale=ms,
        capstyle=capstyle,
        joinstyle=joinstyle,
        zorder=3)
    ax.add_patch(patch)


_BOX_PAD = 0.04


# Layout
center_x = 6.0

top_cx, top_cy = center_x, 4.55
top_w, top_h = 5.40, 0.68

mid_y = 3.30
mid_w, mid_h = 3.80, 0.82
timeout_cx = center_x - 3.00
request_cx = center_x + 3.00

bw, bh = 2.65, 1.45
bot_y = 1.30
wrong_x, right_x, hit_x, conflict_x = 1.50, 4.50, 7.50, 10.50
bot_top = bot_y + bh / 2


# ── Top: Per-Bank Timeout Counter ──
rbox(top_cx, top_cy, top_w, top_h, '#F6F8FB', '#555', lw=1.2, pad=0.04)
ax.text(top_cx, top_cy + 0.12, 'Per-Bank Timeout Counter',
        fontsize=7.6, fontweight='bold', ha='center', va='center', color='#222')
ax.text(top_cx, top_cy - 0.16, 'timeout  [50, 3200] cycles   init = 200',
        fontsize=5.0, ha='center', va='center', color=C_G, fontstyle='italic')


# ── Middle: two event sources ──
rbox(timeout_cx, mid_y, mid_w, mid_h, '#F5F5F5', '#888', lw=1.0, pad=0.04)
ax.text(timeout_cx, mid_y + 0.12, 'Timeout Expires',
        fontsize=FONT_TICK, fontweight='bold', ha='center', va='center', color='#333')
ax.text(timeout_cx, mid_y - 0.16, 'speculative precharge issued',
        fontsize=4.6, ha='center', va='center', color=C_G, fontstyle='italic')

rbox(request_cx, mid_y, mid_w, mid_h, '#F5F5F5', '#888', lw=1.0, pad=0.04)
ax.text(request_cx, mid_y + 0.08, 'New Request Before Timeout',
        fontsize=FONT_TICK, fontweight='bold', ha='center', va='center', color='#333')
ax.text(request_cx, mid_y - 0.18, 'row remains open',
        fontsize=4.6, ha='center', va='center', color=C_G, fontstyle='italic')


# ── Orthogonal arrows: Top -> Middle (shared stem, right-angle branch) ──
_mid_split_y = (top_cy - top_h / 2 + mid_y + mid_h / 2) / 2

# Shared vertical stem
ax.plot([top_cx, top_cx], [top_cy - top_h / 2 - _BOX_PAD, _mid_split_y],
        color='#7A7A7A', lw=1.0, solid_capstyle='butt', zorder=3)
# Left branch
ortho_arrow(
    [(top_cx, _mid_split_y),
     (timeout_cx, _mid_split_y),
     (timeout_cx, mid_y + mid_h / 2 + _BOX_PAD)],
    color='#7A7A7A', lw=1.0, ms=11)
# Right branch
ortho_arrow(
    [(top_cx, _mid_split_y),
     (request_cx, _mid_split_y),
     (request_cx, mid_y + mid_h / 2 + _BOX_PAD)],
    color='#7A7A7A', lw=1.0, ms=11)


# ── Arrows: Middle -> Bottom outcomes ──
split_y = 2.38

ortho_arrow(
    [(timeout_cx, mid_y - mid_h / 2 - _BOX_PAD),
     (timeout_cx, split_y),
     (wrong_x, split_y),
     (wrong_x, bot_top + _BOX_PAD)],
    color=C_G, lw=1.0, ms=11)
ortho_arrow(
    [(timeout_cx, mid_y - mid_h / 2 - _BOX_PAD),
     (timeout_cx, split_y),
     (right_x, split_y),
     (right_x, bot_top + _BOX_PAD)],
    color=C_G, lw=1.0, ms=11)
ortho_arrow(
    [(request_cx, mid_y - mid_h / 2 - _BOX_PAD),
     (request_cx, split_y),
     (hit_x, split_y),
     (hit_x, bot_top + _BOX_PAD)],
    color=C_G, lw=1.0, ms=11)
ortho_arrow(
    [(request_cx, mid_y - mid_h / 2 - _BOX_PAD),
     (request_cx, split_y),
     (conflict_x, split_y),
     (conflict_x, bot_top + _BOX_PAD)],
    color=C_G, lw=1.0, ms=11)


# ── WRONG ──
rbox(wrong_x, bot_y, bw, bh, C_WB, C_W, lw=1.3, pad=0.04)
ax.text(wrong_x, bot_y + 0.48, 'WRONG',
        fontsize=FONT_TICK, fontweight='bold', color=C_W, ha='center')
ax.text(wrong_x, bot_y + 0.26, 'new_row = prev_row',
        fontsize=4.1, color=C_G, ha='center')
ax.text(wrong_x, bot_y - 0.05, 'ESCALATE',
        fontsize=FONT_ANNOT, fontweight='bold', fontstyle='italic',
        color=C_W, ha='center')
ax.text(wrong_x, bot_y - 0.32, 'increase timeout',
        fontsize=FONT_DETAIL, color='#333', ha='center')


# ── RIGHT ──
rbox(right_x, bot_y, bw, bh, C_RB, C_R, lw=1.3, pad=0.04)
ax.text(right_x, bot_y + 0.48, 'RIGHT',
        fontsize=FONT_TICK, fontweight='bold', color=C_R, ha='center')
ax.text(right_x, bot_y + 0.26, 'new_row != prev_row',
        fontsize=4.1, color=C_G, ha='center')
ax.text(right_x, bot_y - 0.05, 'DECAY',
        fontsize=FONT_ANNOT, fontweight='bold', fontstyle='italic',
        color=C_R, ha='center')
ax.text(right_x, bot_y - 0.32, 'reduce timeout',
        fontsize=FONT_DETAIL, color='#333', ha='center')


# ── HIT ──
rbox(hit_x, bot_y, bw, bh, C_NB, C_NE, lw=1.1, pad=0.04)
ax.text(hit_x, bot_y + 0.48, 'HIT',
        fontsize=FONT_TICK, fontweight='bold', color='#555', ha='center')
ax.text(hit_x, bot_y + 0.26, 'new_row = open_row',
        fontsize=4.1, color=C_G, ha='center')
ax.text(hit_x, bot_y - 0.05, 'KEEP OPEN',
        fontsize=FONT_ANNOT, fontweight='bold', fontstyle='italic',
        color='#555', ha='center')
ax.text(hit_x, bot_y - 0.32, 'no precharge event',
        fontsize=FONT_DETAIL, color='#333', ha='center')


# ── CONFLICT ──
rbox(conflict_x, bot_y, bw, bh, C_CB, C_C, lw=1.3, pad=0.04)
ax.text(conflict_x, bot_y + 0.48, 'CONFLICT',
        fontsize=FONT_TICK, fontweight='bold', color=C_C, ha='center')
ax.text(conflict_x, bot_y + 0.26, 'new_row != open_row',
        fontsize=4.1, color=C_G, ha='center')
ax.text(conflict_x, bot_y - 0.05, 'DE-ESCALATE',
        fontsize=FONT_ANNOT, fontweight='bold', fontstyle='italic',
        color=C_C, ha='center')
ax.text(conflict_x, bot_y - 0.32, 'reduce timeout',
        fontsize=FONT_DETAIL, color='#333', ha='center')


# ── Feedback: all four bottom boxes → Per-Bank Timeout Counter ──
_bot_bottom = bot_y - bh / 2 - _BOX_PAD          # visual bottom of outcome boxes
_collect_y = 0.15                                  # shared horizontal collection line
_fb_left_x = wrong_x - bw / 2 - _BOX_PAD - 0.30  # left riser
_fb_right_x = conflict_x + bw / 2 + _BOX_PAD + 0.30  # right riser
_top_left = top_cx - top_w / 2 - _BOX_PAD
_top_right = top_cx + top_w / 2 + _BOX_PAD

# Vertical stubs: each box bottom → collection line
for bx in [wrong_x, right_x, hit_x, conflict_x]:
    ax.plot([bx, bx], [_bot_bottom, _collect_y],
            color=C_G, lw=1.0, solid_capstyle='butt', zorder=3)

# Horizontal collection line spanning both risers
ax.plot([_fb_left_x, _fb_right_x], [_collect_y, _collect_y],
        color=C_G, lw=1.0, solid_capstyle='butt', zorder=3)

# Left riser → top box left side
ax.plot([_fb_left_x, _fb_left_x], [_collect_y, top_cy],
        color=C_G, lw=1.0, solid_capstyle='butt', zorder=3)
ortho_arrow(
    [(_fb_left_x, top_cy), (_top_left, top_cy)],
    color=C_G, lw=1.0, ms=11)

# Right riser → top box right side
ax.plot([_fb_right_x, _fb_right_x], [_collect_y, top_cy],
        color=C_G, lw=1.0, solid_capstyle='butt', zorder=3)
ortho_arrow(
    [(_fb_right_x, top_cy), (_top_right, top_cy)],
    color=C_G, lw=1.0, ms=11)


savefig(fig, 'feedback_loop')
