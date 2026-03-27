#!/usr/bin/env python3
"""
Fig 4: DRAM Row Buffer Access Scenarios and Timeout-Based Precharge Outcomes.

Panel (a): Three access scenarios (hit, miss/closed, conflict) with timing.
Panel (b): Three timeout precharge outcomes (right, wrong, conflict) with
           previous-CAS context, row buffer state labels, and penalty annotations.
"""

from common import *

setup_style()

# ── Timing parameters (DDR5-4800, in cycles) ──────────────────
tCAS = 40
tRCD = 40
tRP  = 40

# ── Palette ───────────────────────────────────────────────────
C_PRE   = COLORS['abp']          # slate gray  — precharge command
C_ACT   = COLORS['open_page']    # steel blue  — activate command
C_CAS   = COLORS['craft']        # forest green — CAS command
C_IDLE  = COLORS['idle']         # light gray  — idle period
C_TMOUT = COLORS['intap']        # medium purple — timeout marker
C_WRONG = COLORS['closed_page']  # brick red   — wrong precharge
C_TCONF = COLORS['dympl']        # sandy orange — conflict outcome

# Dark text variants
CD = COLORS_DARK

bar_h = 0.52

# ── Figure layout ─────────────────────────────────────────────
fig, (ax_a, ax_b) = plt.subplots(
    2, 1, figsize=(LNCS_TEXT_WIDTH, 6.0),
    gridspec_kw={'height_ratios': [1, 2.4], 'hspace': 0.2})

# ── Helpers ───────────────────────────────────────────────────

def cmd(ax, y, x, w, label, color, fs=FONT_ANNOT):
    """Draw a colored command block with centered label."""
    ax.barh(y, w, height=bar_h, left=x,
            color=color, edgecolor='black', linewidth=0.8)
    ax.text(x + w / 2, y, label, ha='center', va='center',
            fontsize=fs, color='white', fontweight='bold')
    return x + w

def idle_block(ax, y, x, w, fs=FONT_DETAIL):
    """Draw a light-gray idle period block."""
    ax.barh(y, w, height=bar_h, left=x,
            color=C_IDLE, edgecolor='black', linewidth=0.8)
    ax.text(x + w / 2, y, 'idle', ha='center', va='center',
            fontsize=fs, color='#555')
    return x + w

def closed_gap(ax, y, x, w):
    """Draw a dashed-border gap representing closed bank state."""
    ax.barh(y, w, height=bar_h, left=x,
            color='#F7F7F7', edgecolor='#bbb', linewidth=0.5,
            linestyle='--')
    return x + w

def padding_block(ax, y, x, w):
    """Draw a hatched padding block to equalize bar lengths."""
    ax.barh(y, w, height=bar_h, left=x,
            facecolor='#F8F8F8', edgecolor='#bbb', linewidth=0.5,
            hatch='////')
    return x + w

def bracket_above(ax, xl, xr, y, label, color):
    """Draw a measurement bracket above the bar with label."""
    ya = y + bar_h / 2 + 0.16
    tick = 0.10
    ax.annotate('', xy=(xr, ya), xytext=(xl, ya),
                arrowprops=dict(arrowstyle='<->', color='#444', lw=0.9))
    for xp in (xl, xr):
        ax.plot([xp, xp], [ya - tick, ya + tick], color='#444', lw=0.9)
    ax.text((xl + xr) / 2, ya + 0.08, label, ha='center', va='bottom',
            fontsize=FONT_DETAIL, fontweight='bold', color=color)

def bracket_below(ax, xl, xr, y, label, color):
    """Draw a penalty bracket below the bar with label."""
    yb = y - bar_h / 2 - 0.10
    ax.annotate('', xy=(xr, yb), xytext=(xl, yb),
                arrowprops=dict(arrowstyle='<->', color=color, lw=1.1))
    ax.text((xl + xr) / 2, yb - 0.12, label, ha='center', va='top',
            fontsize=FONT_DETAIL, fontweight='bold', color=color)

def timeout_mark(ax, x, y):
    """Draw a dashed timeout marker across the bar."""
    bot = y - bar_h * 0.55
    top = y + bar_h * 0.55
    ax.plot([x, x], [bot, top], color=C_TMOUT,
            linewidth=1.2, linestyle='--', zorder=5)
    ax.plot(x, top + 0.06, marker='v', color=C_TMOUT,
            markersize=4, zorder=5, clip_on=False)
    ax.text(x, top + 0.16, 'timeout', ha='center', va='bottom',
            fontsize=FONT_DETAIL, color=C_TMOUT, fontweight='bold')

def req_arrow(ax, x, y, label, color='#333'):
    """Draw a request-arrival arrow above the bar."""
    ax.annotate(label,
                xy=(x, y + bar_h / 2 + 0.03),
                xytext=(x + 20, y + bar_h / 2 + 0.55),
                fontsize=FONT_DETAIL, ha='center', fontweight='bold', color=color,
                arrowprops=dict(arrowstyle='->', color=color, lw=0.7))

def state_label(ax, x, y, label, color='#666'):
    """Place a row-buffer state label below the bar."""
    ax.text(x, y - bar_h / 2 - 0.20, label, ha='center', va='top',
            fontsize=5, fontstyle='italic', color=color)


def cas_mark(ax, x, y):
    """Draw a CAS command marker (dashed line with triangle, like timeout)."""
    bot = y - bar_h * 0.55
    top = y + bar_h * 0.55
    ax.plot([x, x], [bot, top], color=C_CAS,
            linewidth=1.2, linestyle='--', zorder=5)
    ax.plot(x, top + 0.06, marker='v', color=C_CAS,
            markersize=4, zorder=5, clip_on=False)
    ax.text(x, top + 0.16, 'CAS', ha='center', va='bottom',
            fontsize=FONT_DETAIL, color=CD['craft'], fontweight='bold')


def req_mark(ax, x, y, label, color='#333'):
    """Draw a request-arrival marker (dashed line with triangle, like timeout)."""
    bot = y - bar_h * 0.55
    top = y + bar_h * 0.55
    ax.plot([x, x], [bot, top], color=color,
            linewidth=1.2, linestyle='--', zorder=5)
    ax.plot(x, top + 0.06, marker='v', color=color,
            markersize=4, zorder=5, clip_on=False)
    ax.text(x, top + 0.16, label, ha='center', va='bottom',
            fontsize=FONT_DETAIL, color=color, fontweight='bold')


def ghost_timeout_mark(ax, x, y):
    """Draw a faint dashed line showing where timeout would have occurred."""
    bot = y - bar_h * 0.55
    top = y + bar_h * 0.55
    ax.plot([x, x], [bot, top], color=C_TMOUT,
            linewidth=1.2, linestyle=':', alpha=0.5, zorder=5)


# ═══════════════════════════════════════════════════════════════
# Panel (a): Three Access Scenarios
# ═══════════════════════════════════════════════════════════════
ax_a.set_xlim(-5, 175)
ax_a.set_ylim(-0.5, 4.2)
ax_a.axis('off')
ax_a.set_title('(a) Row Buffer Access Latency',
               fontsize=FONT_TITLE, fontweight='bold', pad=8)

ys_a = [3.2, 1.8, 0.4]
labels_a = ['Row Buffer Hit',
            'Row Buffer Miss\n(Closed Bank)',
            'Row Buffer Conflict\n(Wrong Row Open)']
x0 = 8

for y, lbl in zip(ys_a, labels_a):
    ax_a.text(x0 - 3, y, lbl, ha='right', va='center',
              fontsize=FONT_ANNOT, fontweight='bold')

# Hit: tCAS only
cmd(ax_a, ys_a[0], x0, tCAS, 'tCAS', C_CAS)
bracket_above(ax_a, x0, x0 + tCAS, ys_a[0], 'Total: tCAS', CD['craft'])

# Miss: tRCD + tCAS
cmd(ax_a, ys_a[1], x0, tRCD, 'tRCD', C_ACT)
cmd(ax_a, ys_a[1], x0 + tRCD, tCAS, 'tCAS', C_CAS)
bracket_above(ax_a, x0, x0 + tRCD + tCAS, ys_a[1],
              'Total: tRCD + tCAS', CD['dympl'])

# Conflict: tRP + tRCD + tCAS
cmd(ax_a, ys_a[2], x0, tRP, 'tRP', C_PRE)
cmd(ax_a, ys_a[2], x0 + tRP, tRCD, 'tRCD', C_ACT)
cmd(ax_a, ys_a[2], x0 + tRP + tRCD, tCAS, 'tCAS', C_CAS)
bracket_above(ax_a, x0, x0 + tRP + tRCD + tCAS, ys_a[2],
              'Total: tRP + tRCD + tCAS', CD['closed_page'])


# ═══════════════════════════════════════════════════════════════
# Panel (b): Four Timeout Precharge Outcomes
# ═══════════════════════════════════════════════════════════════
ax_b.set_xlim(-5, 210)
ax_b.set_ylim(-0.3, 9.8)
ax_b.axis('off')
ax_b.set_title('(b) Timeout-Based Speculative Precharge Outcomes',
               fontsize=FONT_TITLE, fontweight='bold', pad=8)

ys_b = [8.2, 6.0, 3.8, 1.6]
labels_b = ['Right Precharge',
            'Wrong Precharge',
            'Conflict',
            'Row Buffer Hit']

for y, lbl in zip(ys_b, labels_b):
    ax_b.text(-3, y, lbl, ha='right', va='center',
              fontsize=FONT_ANNOT, fontweight='bold')

# Shared reference positions
x0      = 5
tmx_pos = x0 + 36                         # standard timeout position: 41
gap_w   = 10                               # closed-bank gap width
x_end   = x0 + 36 + tRP + gap_w + tRCD    # bar end reference: 131

# ── Right Precharge ──────────────────────────────────────────
y = ys_b[0]
x = x0
cas_mark(ax_b, x, y)
idle_w = tmx_pos - x0                                       # 36
x = idle_block(ax_b, y, x, idle_w)                          # 5 → 41
timeout_mark(ax_b, x, y)                                    # at 41
x = cmd(ax_b, y, x, tRP, 'PRE', C_PRE, fs=FONT_TICK)              # 41 → 81
closed_start = x
x = closed_gap(ax_b, y, x, gap_w)                           # 81 → 91
req_mark(ax_b, closed_start + gap_w / 2, y, 'Req. (diff row)')
x = cmd(ax_b, y, x, tRCD, 'ACT', C_ACT, fs=FONT_TICK)             # 91 → 131
cas_mark(ax_b, x, y)
ax_b.text(x + 8, y, 'Penalty: 0', ha='left', va='center',
          fontsize=FONT_ANNOT, fontweight='bold', color=CD['craft'])
state_label(ax_b, x0 + idle_w / 2, y, 'Row A open')
state_label(ax_b, closed_start + gap_w / 2, y, 'closed', '#999')
state_label(ax_b, closed_start + gap_w + tRCD / 2, y, 'Row B open')

# ── Wrong Precharge ──────────────────────────────────────────
y = ys_b[1]
x = x0
cas_mark(ax_b, x, y)
x = idle_block(ax_b, y, x, idle_w)                          # 5 → 41
timeout_mark(ax_b, x, y)                                    # at 41
x = cmd(ax_b, y, x, tRP, 'PRE', C_PRE, fs=FONT_TICK)              # 41 → 81
closed_start = x
x = closed_gap(ax_b, y, x, gap_w)                           # 81 → 91
req_mark(ax_b, closed_start + gap_w / 2, y, 'Req. (same row)', C_WRONG)
act_end = cmd(ax_b, y, x, tRCD, 'ACT', C_ACT, fs=FONT_TICK)       # 91 → 131
cas_mark(ax_b, act_end, y)
ax_b.text(act_end + 8, y, 'Penalty: tRCD', ha='left', va='center',
          fontsize=FONT_ANNOT, fontweight='bold', color=CD['closed_page'])
state_label(ax_b, x0 + idle_w / 2, y, 'Row A open')
state_label(ax_b, closed_start + gap_w / 2, y, 'closed', '#999')
state_label(ax_b, closed_start + gap_w + tRCD / 2, y,
            'Row A  (reopened)', CD['closed_page'])

# ── Conflict ─────────────────────────────────────────────────
y = ys_b[2]
x = x0
cas_mark(ax_b, x, y)
conflict_idle = 26                                           # wider idle for spacing
x = idle_block(ax_b, y, x, conflict_idle)                   # 5 → 31
req_mark(ax_b, x, y, 'Req.(diff row)', C_TCONF)            # at 31
pre_start = x
# PRE block — shift label to left half to avoid collision with timeout marker
ax_b.barh(y, tRP, height=bar_h, left=pre_start,
          color=C_PRE, edgecolor='black', linewidth=0.8)
ax_b.text(pre_start + tRP * 0.4, y, 'PRE',
          ha='center', va='center',
          fontsize=FONT_DETAIL, color='white', fontweight='bold')
x = pre_start + tRP                                         # 71
ghost_timeout_mark(ax_b, tmx_pos, y)                        # at 41, faint reference
x = cmd(ax_b, y, x, tRCD, 'ACT', C_ACT, fs=FONT_TICK)     # 71 → 111
cas_mark(ax_b, x, y)                                        # at 111
# Hatched padding to equalize bar length
padding_block(ax_b, y, x, x_end - x)
ax_b.text(x_end + 8, y, 'Penalty: tRP + tRCD', ha='left', va='center',
          fontsize=FONT_ANNOT, fontweight='bold', color=CD['dympl'])
state_label(ax_b, x0 + conflict_idle / 2, y, 'Row A open')
state_label(ax_b, pre_start + tRP + tRCD / 2, y, 'Row B open')

# ── Row Buffer Hit (request arrives before timeout) ──────────
y = ys_b[3]
x = x0
cas_mark(ax_b, x, y)
hit_idle = 26                                                # wider idle for spacing
x = idle_block(ax_b, y, x, hit_idle)                        # 5 → 31
req_mark(ax_b, x, y, 'Req.(same row)', C_CAS)              # at 31
# Hatched padding to equalize bar length
padding_block(ax_b, y, x, x_end - x)
# Timeout marker — same style as other scenarios
ghost_timeout_mark(ax_b, tmx_pos, y)                         # at 41, faint reference
ax_b.text(x_end + 8, y, 'Penalty: 0', ha='left', va='center',
          fontsize=FONT_ANNOT, fontweight='bold', color=CD['craft'])
state_label(ax_b, x0 + hit_idle / 2, y, 'Row A open')

# ── Command legend ────────────────────────────────────────────
from matplotlib.patches import Patch
legend_patches = [
    Patch(facecolor=C_PRE, edgecolor='black', label='PRE (precharge)'),
    Patch(facecolor=C_ACT, edgecolor='black', label='ACT (activate)'),
    Patch(facecolor=C_CAS, edgecolor='black', label='CAS (column access)'),
    Patch(facecolor=C_IDLE, edgecolor='black', label='Idle'),
]
ax_a.legend(handles=legend_patches, loc='upper right',
            fontsize=FONT_DETAIL, framealpha=0.9, edgecolor='#ccc',
            ncol=1, handlelength=1.0)

savefig(fig, 'timing_diagram')
