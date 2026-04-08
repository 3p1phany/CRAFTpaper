#!/usr/bin/env python3
"""
Fig 6: CRAFT timeout-control logic.

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
fig, ax = plt.subplots(figsize=(LNCS_TEXT_WIDTH * 1.18, 3.55))
ax.set_xlim(-1.10, 13.10)
ax.set_ylim(-0.15, 5.45)
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


def rbox(cx, cy, w, h, fc, ec, lw=1.3):
    box = FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle="round,pad=0.06",
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


_BOX_PAD = 0.09


# Layout
center_x = 6.0

top_cx, top_cy = center_x, 4.55
top_w, top_h = 6.20, 0.72

mid_y = 3.35
mid_w, mid_h = 4.10, 0.96
timeout_cx = center_x - 3.0
request_cx = center_x + 3.0

bw, bh = 2.70, 2.24
bot_y = 1.05
wrong_x, right_x, hit_x, conflict_x = 1.50, 4.50, 7.50, 10.50
bot_top = bot_y + bh / 2


# Top: per-bank timeout counter
rbox(top_cx, top_cy, top_w, top_h, C_BB, C_B, lw=1.8)
ax.text(top_cx, top_cy + 0.12, 'Per-Bank Timeout Counter',
        fontsize=7.6, fontweight='bold', ha='center', va='center', color='#222')
ax.text(top_cx, top_cy - 0.18, 'timeout  [50, 3200] cycles   init = 200',
        fontsize=5.2, ha='center', va='center', color=C_G, fontstyle='italic')


# Middle: two event sources
rbox(timeout_cx, mid_y, mid_w, mid_h, '#F5F5F5', '#888', lw=1.0)
ax.text(timeout_cx, mid_y + 0.12, 'Timeout Expires',
        fontsize=FONT_TICK, fontweight='bold', ha='center', va='center', color='#333')
ax.text(timeout_cx, mid_y - 0.16, 'speculative precharge issued',
        fontsize=4.6, ha='center', va='center', color=C_G, fontstyle='italic')

rbox(request_cx, mid_y, mid_w, mid_h, '#F5F5F5', '#888', lw=1.0)
ax.text(request_cx, mid_y + 0.17, 'New Request',
        fontsize=FONT_TICK, fontweight='bold', ha='center', va='center', color='#333')
ax.text(request_cx, mid_y - 0.01, 'Before Timeout',
        fontsize=FONT_TICK, fontweight='bold', ha='center', va='center', color='#333')
ax.text(request_cx, mid_y - 0.25, 'row remains open',
        fontsize=4.6, ha='center', va='center', color=C_G, fontstyle='italic')


# Counter -> event-source arrows
ortho_arrow(
    [(top_cx - 1.10, top_cy - top_h / 2 - _BOX_PAD),
     (timeout_cx, mid_y + mid_h / 2 + _BOX_PAD)],
    color=C_B, lw=1.3)
ortho_arrow(
    [(top_cx + 1.10, top_cy - top_h / 2 - _BOX_PAD),
     (request_cx, mid_y + mid_h / 2 + _BOX_PAD)],
    color=C_B, lw=1.3)


# Event sources -> outcomes
split_y = 2.58

ortho_arrow(
    [(timeout_cx, mid_y - mid_h / 2 - _BOX_PAD),
     (timeout_cx, split_y),
     (wrong_x, split_y),
     (wrong_x, bot_top + 0.04)],
    color=C_G, lw=1.3)
ortho_arrow(
    [(timeout_cx, mid_y - mid_h / 2 - _BOX_PAD),
     (timeout_cx, split_y),
     (right_x, split_y),
     (right_x, bot_top + 0.04)],
    color=C_G, lw=1.3)
ortho_arrow(
    [(request_cx, mid_y - mid_h / 2 - _BOX_PAD),
     (request_cx, split_y),
     (hit_x, split_y),
     (hit_x, bot_top + 0.04)],
    color=C_G, lw=1.3)
ortho_arrow(
    [(request_cx, mid_y - mid_h / 2 - _BOX_PAD),
     (request_cx, split_y),
     (conflict_x, split_y),
     (conflict_x, bot_top + 0.04)],
    color=C_G, lw=1.3)


# WRONG
rbox(wrong_x, bot_y, bw, bh, C_WB, C_W, lw=1.5)
ax.text(wrong_x, bot_y + 0.88, 'WRONG',
        fontsize=FONT_TICK, fontweight='bold', color=C_W, ha='center')
ax.text(wrong_x, bot_y + 0.64, 'new_row = prev_row',
        fontsize=4.1, color=C_G, ha='center')
ax.text(wrong_x, bot_y + 0.40, 'Penalty: tRP + tRCD',
        fontsize=5.1, fontweight='bold', color='#444', ha='center')
ax.plot([wrong_x - bw * 0.33, wrong_x + bw * 0.33], [bot_y + 0.18, bot_y + 0.18],
        color=C_W, lw=0.6, alpha=0.4)
ax.text(wrong_x, bot_y - 0.02, 'ESCALATE',
        fontsize=FONT_ANNOT, fontweight='bold', color=C_W, ha='center')
ax.text(wrong_x, bot_y - 0.28, 'timeout +=',
        fontsize=FONT_DETAIL, color='#333', ha='center')
ax.text(wrong_x, bot_y - 0.48, 'B * 2^streak',
        fontsize=FONT_DETAIL, color='#333', ha='center')
ax.text(wrong_x, bot_y - 0.72, '(exponential backoff)',
        fontsize=4.8, color=C_G, ha='center', fontstyle='italic')


# RIGHT
rbox(right_x, bot_y, bw, bh, C_RB, C_R, lw=1.5)
ax.text(right_x, bot_y + 0.88, 'RIGHT',
        fontsize=FONT_TICK, fontweight='bold', color=C_R, ha='center')
ax.text(right_x, bot_y + 0.64, 'new_row != prev_row',
        fontsize=4.1, color=C_G, ha='center')
ax.text(right_x, bot_y + 0.40, 'Saved: tRP',
        fontsize=FONT_ANNOT, fontweight='bold', color='#444', ha='center')
ax.plot([right_x - bw * 0.33, right_x + bw * 0.33], [bot_y + 0.18, bot_y + 0.18],
        color=C_R, lw=0.6, alpha=0.4)
ax.text(right_x, bot_y - 0.02, 'NO CHANGE',
        fontsize=FONT_ANNOT, fontweight='bold', color=C_R, ha='center')
ax.text(right_x, bot_y - 0.32, 'right_streak++',
        fontsize=FONT_DETAIL, color='#333', ha='center')
ax.text(right_x, bot_y - 0.70, '(timeout confirmed)',
        fontsize=4.8, color=C_G, ha='center', fontstyle='italic')


# ROW HIT
rbox(hit_x, bot_y, bw, bh, C_NB, C_NE, lw=1.3)
ax.text(hit_x, bot_y + 0.88, 'ROW HIT',
        fontsize=FONT_TICK, fontweight='bold', color='#555', ha='center')
ax.text(hit_x, bot_y + 0.64, 'new_row = open_row',
        fontsize=4.1, color=C_G, ha='center')
ax.text(hit_x, bot_y + 0.40, 'Cost: 0',
        fontsize=FONT_ANNOT, fontweight='bold', color='#444', ha='center')
ax.plot([hit_x - bw * 0.33, hit_x + bw * 0.33], [bot_y + 0.18, bot_y + 0.18],
        color=C_NE, lw=0.6, alpha=0.4)
ax.text(hit_x, bot_y - 0.02, 'KEEP OPEN',
        fontsize=FONT_ANNOT, fontweight='bold', color='#555', ha='center')
ax.text(hit_x, bot_y - 0.32, 'no precharge event',
        fontsize=FONT_DETAIL, color='#333', ha='center')
ax.text(hit_x, bot_y - 0.70, '(outside feedback loop)',
        fontsize=4.8, color=C_G, ha='center', fontstyle='italic')


# CONFLICT
rbox(conflict_x, bot_y, bw, bh, C_CB, C_C, lw=1.5)
ax.text(conflict_x, bot_y + 0.88, 'CONFLICT',
        fontsize=FONT_TICK, fontweight='bold', color=C_C, ha='center')
ax.text(conflict_x, bot_y + 0.64, 'new_row != open_row',
        fontsize=4.1, color=C_G, ha='center')
ax.text(conflict_x, bot_y + 0.40, 'Penalty: tRP',
        fontsize=FONT_ANNOT, fontweight='bold', color='#444', ha='center')
ax.plot([conflict_x - bw * 0.33, conflict_x + bw * 0.33], [bot_y + 0.18, bot_y + 0.18],
        color=C_C, lw=0.6, alpha=0.4)
ax.text(conflict_x, bot_y - 0.02, 'DE-ESCALATE',
        fontsize=FONT_ANNOT, fontweight='bold', color=C_C, ha='center')
ax.text(conflict_x, bot_y - 0.28, 'timeout -= B * tRP /',
        fontsize=4.8, color='#333', ha='center')
ax.text(conflict_x, bot_y - 0.55, '(tRP + tRCD)',
        fontsize=4.8, color='#333', ha='center')
ax.text(conflict_x, bot_y - 0.84, '(cost-proportional)',
        fontsize=4.7, color=C_G, ha='center', fontstyle='italic')


# Feedback arrows
fb_lw, fb_ms = 2.2, 14

left_fb_x = -0.85
left_fb_y = bot_y
top_left_y = top_cy
ortho_arrow(
    [(wrong_x - bw / 2, left_fb_y),
     (left_fb_x, left_fb_y),
     (left_fb_x, top_left_y),
     (top_cx - top_w / 2, top_left_y)],
    color=C_W, lw=fb_lw, ms=fb_ms, capstyle='butt', joinstyle='miter')

right_fb_x = 12.85
right_fb_y = bot_y
top_right_y = top_cy
ortho_arrow(
    [(conflict_x + bw / 2, right_fb_y),
     (right_fb_x, right_fb_y),
     (right_fb_x, top_right_y),
     (top_cx + top_w / 2, top_right_y)],
    color=C_C, lw=fb_lw, ms=fb_ms, capstyle='butt', joinstyle='miter')


savefig(fig, 'feedback_loop')
