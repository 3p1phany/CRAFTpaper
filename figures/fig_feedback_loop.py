#!/usr/bin/env python3
"""
Fig 6: CRAFT timeout-control logic.

The diagram distinguishes two event sources under a timeout-based policy:
1. The timeout expires and the controller issues a speculative precharge.
   The next access then determines whether the decision was RIGHT or WRONG.
2. A new request arrives before timeout expiration. It becomes either a
   ROW HIT (same row still open) or a CONFLICT (different row requires an
   on-demand precharge).

WRONG and CONFLICT are the primary feedback signals. RIGHT decays the
reopen_streak counter [SD] and, after four or more consecutive occurrences,
gradually reduces the timeout [RS]. ROW HIT stays outside the feedback path.
"""

from common import *
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from matplotlib.path import Path as MPath


setup_style()
fig, ax = plt.subplots(figsize=(LNCS_TEXT_WIDTH * 1.18, 3.80))
ax.set_xlim(-1.10, 13.10)
ax.set_ylim(-0.15, 5.80)
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
C_EDGE = '#555555'
C_TEXT = '#222222'
C_SUB = '#666666'
C_ARROW = '#606060'


def rbox(cx, cy, w, h, fc, ec, lw=1.0, pad=0.03):
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


_BOX_PAD = 0.01


# Layout
center_x = 6.0

top_cx, top_cy = center_x, 4.90
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
rbox(top_cx, top_cy, top_w, top_h, '#F6F8FB', C_EDGE, lw=1.1, pad=0.025)
ax.text(top_cx, top_cy + 0.12, 'Per-Bank Timeout Counter',
        fontsize=7.4, fontweight='bold', ha='center', va='center', color=C_TEXT)
ax.text(top_cx, top_cy - 0.18, 'timeout  [50, 3200] cycles   init = 200',
        fontsize=5.0, ha='center', va='center', color=C_SUB, fontstyle='italic')


# Middle: two event sources
rbox(timeout_cx, mid_y, mid_w, mid_h, '#FAFAFA', '#8A8A8A', lw=0.9, pad=0.02)
ax.text(timeout_cx, mid_y + 0.12, 'Timeout Expires',
        fontsize=FONT_TICK, fontweight='bold', ha='center', va='center', color='#333')
ax.text(timeout_cx, mid_y - 0.16, 'speculative precharge issued',
        fontsize=4.6, ha='center', va='center', color=C_SUB, fontstyle='italic')

rbox(request_cx, mid_y, mid_w, mid_h, '#FAFAFA', '#8A8A8A', lw=0.9, pad=0.02)
ax.text(request_cx, mid_y + 0.17, 'New Request',
        fontsize=FONT_TICK, fontweight='bold', ha='center', va='center', color='#333')
ax.text(request_cx, mid_y - 0.01, 'Before Timeout',
        fontsize=FONT_TICK, fontweight='bold', ha='center', va='center', color='#333')
ax.text(request_cx, mid_y - 0.25, 'row remains open',
        fontsize=4.6, ha='center', va='center', color=C_SUB, fontstyle='italic')


# Counter -> event-source arrows (shared stem, then branch)
_mid_split_y = (top_cy - top_h / 2 + mid_y + mid_h / 2) / 2
# Shared vertical stem from top box center
ax.plot([top_cx, top_cx], [top_cy - top_h / 2 - _BOX_PAD, _mid_split_y],
        color='#7A7A7A', lw=1.0, solid_capstyle='butt', zorder=3)
# Left branch to Timeout Expires
ortho_arrow(
    [(top_cx, _mid_split_y),
     (timeout_cx, _mid_split_y),
     (timeout_cx, mid_y + mid_h / 2 + _BOX_PAD)],
    color='#7A7A7A', lw=1.0, ms=11)
# Right branch to New Request
ortho_arrow(
    [(top_cx, _mid_split_y),
     (request_cx, _mid_split_y),
     (request_cx, mid_y + mid_h / 2 + _BOX_PAD)],
    color='#7A7A7A', lw=1.0, ms=11)


# Event sources -> outcomes
split_y = 2.58

ortho_arrow(
    [(timeout_cx, mid_y - mid_h / 2 - _BOX_PAD),
     (timeout_cx, split_y),
     (wrong_x, split_y),
     (wrong_x, bot_top + _BOX_PAD)],
    color=C_ARROW, lw=1.0, ms=11)
ortho_arrow(
    [(timeout_cx, mid_y - mid_h / 2 - _BOX_PAD),
     (timeout_cx, split_y),
     (right_x, split_y),
     (right_x, bot_top + _BOX_PAD)],
    color=C_ARROW, lw=1.0, ms=11)
ortho_arrow(
    [(request_cx, mid_y - mid_h / 2 - _BOX_PAD),
     (request_cx, split_y),
     (hit_x, split_y),
     (hit_x, bot_top + _BOX_PAD)],
    color=C_ARROW, lw=1.0, ms=11)
ortho_arrow(
    [(request_cx, mid_y - mid_h / 2 - _BOX_PAD),
     (request_cx, split_y),
     (conflict_x, split_y),
     (conflict_x, bot_top + _BOX_PAD)],
    color=C_ARROW, lw=1.0, ms=11)


# WRONG
rbox(wrong_x, bot_y, bw, bh, '#FBF1F1', C_W, lw=1.1, pad=0.025)
ax.text(wrong_x, bot_y + 0.88, 'WRONG',
        fontsize=FONT_TICK, fontweight='bold', color=C_W, ha='center')
ax.text(wrong_x, bot_y + 0.64, 'new_row = prev_row',
        fontsize=4.1, color=C_SUB, ha='center')
ax.text(wrong_x, bot_y + 0.40, 'Avoidable cost: tRP + tRCD',
        fontsize=5.0, fontweight='bold', color='#444', ha='center')
ax.plot([wrong_x - bw * 0.33, wrong_x + bw * 0.33], [bot_y + 0.18, bot_y + 0.18],
        color=C_W, lw=0.6, alpha=0.4)
ax.text(wrong_x, bot_y - 0.02, 'ESCALATE',
        fontsize=FONT_ANNOT, fontweight='bold', color=C_W, ha='center')
ax.text(wrong_x, bot_y - 0.28, 'timeout +=',
        fontsize=FONT_DETAIL, color='#333', ha='center')
ax.text(wrong_x, bot_y - 0.48, 'B \u00b7 2^reopen_streak',
        fontsize=FONT_DETAIL, color='#333', ha='center')
ax.text(wrong_x, bot_y - 0.72, '(exponential backoff)',
        fontsize=4.8, color=C_SUB, ha='center', fontstyle='italic')


# RIGHT
rbox(right_x, bot_y, bw, bh, '#F2F8F0', C_R, lw=1.1, pad=0.025)
ax.text(right_x, bot_y + 0.88, 'RIGHT',
        fontsize=FONT_TICK, fontweight='bold', color=C_R, ha='center')
ax.text(right_x, bot_y + 0.64, 'new_row != prev_row',
        fontsize=4.1, color=C_SUB, ha='center')
ax.text(right_x, bot_y + 0.40, 'Avoidable cost: 0',
        fontsize=FONT_ANNOT, fontweight='bold', color='#444', ha='center')
ax.plot([right_x - bw * 0.33, right_x + bw * 0.33], [bot_y + 0.18, bot_y + 0.18],
        color=C_R, lw=0.6, alpha=0.4)
ax.text(right_x, bot_y - 0.02, 'DECAY',
        fontsize=FONT_ANNOT, fontweight='bold', color=C_R, ha='center')
ax.text(right_x, bot_y - 0.24, 'reopen_streak -= 1',
        fontsize=FONT_DETAIL, color='#333', ha='center')
ax.text(right_x, bot_y - 0.40, 'right_streak++',
        fontsize=FONT_DETAIL, color='#333', ha='center')
ax.text(right_x, bot_y - 0.58, 'after 4+ consecutive:',
        fontsize=FONT_DETAIL, color='#333', ha='center')
ax.text(right_x, bot_y - 0.74, 'reduce timeout',
        fontsize=FONT_DETAIL, color='#333', ha='center')
ax.text(right_x, bot_y - 0.94, '(gradual reduction)',
        fontsize=4.8, color=C_SUB, ha='center', fontstyle='italic')


# ROW HIT
rbox(hit_x, bot_y, bw, bh, '#F6F6F6', C_NE, lw=1.0, pad=0.025)
ax.text(hit_x, bot_y + 0.88, 'HIT',
        fontsize=FONT_TICK, fontweight='bold', color='#555', ha='center')
ax.text(hit_x, bot_y + 0.64, 'new_row = open_row',
        fontsize=4.1, color=C_SUB, ha='center')
ax.text(hit_x, bot_y + 0.40, 'Avoidable cost: 0',
        fontsize=FONT_ANNOT, fontweight='bold', color='#444', ha='center')
ax.plot([hit_x - bw * 0.33, hit_x + bw * 0.33], [bot_y + 0.18, bot_y + 0.18],
        color=C_NE, lw=0.6, alpha=0.4)
ax.text(hit_x, bot_y - 0.02, 'KEEP OPEN',
        fontsize=FONT_ANNOT, fontweight='bold', color='#555', ha='center')
ax.text(hit_x, bot_y - 0.32, 'no precharge event',
        fontsize=FONT_DETAIL, color='#333', ha='center')
ax.text(hit_x, bot_y - 0.70, '(outside feedback loop)',
        fontsize=4.8, color=C_SUB, ha='center', fontstyle='italic')


# CONFLICT
rbox(conflict_x, bot_y, bw, bh, '#FCF4EC', C_C, lw=1.1, pad=0.025)
ax.text(conflict_x, bot_y + 0.88, 'CONFLICT',
        fontsize=FONT_TICK, fontweight='bold', color=C_C, ha='center')
ax.text(conflict_x, bot_y + 0.64, 'new_row != open_row',
        fontsize=4.1, color=C_SUB, ha='center')
ax.text(conflict_x, bot_y + 0.40, 'Avoidable cost: tRP',
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
        fontsize=4.7, color=C_SUB, ha='center', fontstyle='italic')


savefig(fig, 'feedback_loop')
