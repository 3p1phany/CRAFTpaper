#!/usr/bin/env python3
"""
Fig: DRAM Row Buffer Access Scenarios and Timeout-Based Precharge Outcomes.

Top: Three access scenarios (hit, miss/closed, conflict) with timing.
Bottom: Three timeout precharge outcomes (right, wrong, conflict).
"""

from common import *
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch

setup_style()

# ── Timing parameters (DDR5-4800, in cycles) ──
tCAS = 40
tRCD = 40
tRP  = 40

# Colors
C_HIT     = '#4CAF50'   # green
C_MISS    = '#FF9800'   # orange
C_CONFLICT= '#F44336'   # red
C_PRE     = '#90A4AE'   # gray-blue
C_ACT     = '#42A5F5'   # blue
C_CAS     = '#66BB6A'   # green
C_IDLE    = '#E0E0E0'   # light gray
C_TIMEOUT = '#7E57C2'   # purple
C_RIGHT   = COLORS['craft']
C_WRONG   = COLORS['closed_page']
C_TCONFLICT = COLORS['intap']

fig, axes = plt.subplots(2, 1, figsize=(10, 5.2), gridspec_kw={'height_ratios': [1, 1.15]})

# ═══════════════════════════════════════════════════════════════════
# Panel (a): Three access scenarios
# ═══════════════════════════════════════════════════════════════════
ax = axes[0]
ax.set_xlim(-5, 165)
ax.set_ylim(-0.5, 3.5)
ax.axis('off')
ax.set_title('(a) DRAM Row Buffer Access Latency', fontsize=11, fontweight='bold', pad=8)

row_y = [2.6, 1.4, 0.2]
labels_left = ['Row Buffer Hit', 'Row Buffer Miss\n(Closed Bank)', 'Row Buffer Conflict\n(Wrong Row Open)']
bar_h = 0.6

for i, (y, label) in enumerate(zip(row_y, labels_left)):
    ax.text(-3, y + bar_h/2, label, ha='right', va='center', fontsize=8.5, fontweight='bold')

# Row 0: Hit — just CAS
x0 = 5
ax.barh(row_y[0], tCAS, height=bar_h, left=x0, color=C_CAS, edgecolor='white', linewidth=0.5)
ax.text(x0 + tCAS/2, row_y[0] + bar_h/2, f'CAS ({tCAS} cyc)', ha='center', va='center', fontsize=8, color='white', fontweight='bold')
# total
ax.annotate('', xy=(x0 + tCAS + 2, row_y[0] + bar_h + 0.15), xytext=(x0 - 1, row_y[0] + bar_h + 0.15),
            arrowprops=dict(arrowstyle='<->', color='#333', lw=1.2))
ax.text(x0 + tCAS/2, row_y[0] + bar_h + 0.35, f'Total: {tCAS} cycles', ha='center', va='bottom', fontsize=7.5, fontweight='bold', color=C_HIT)

# Row 1: Miss (closed) — ACT + CAS
x0 = 5
ax.barh(row_y[1], tRCD, height=bar_h, left=x0, color=C_ACT, edgecolor='white', linewidth=0.5)
ax.text(x0 + tRCD/2, row_y[1] + bar_h/2, f'ACT ({tRCD})', ha='center', va='center', fontsize=8, color='white', fontweight='bold')
ax.barh(row_y[1], tCAS, height=bar_h, left=x0 + tRCD, color=C_CAS, edgecolor='white', linewidth=0.5)
ax.text(x0 + tRCD + tCAS/2, row_y[1] + bar_h/2, f'CAS ({tCAS})', ha='center', va='center', fontsize=8, color='white', fontweight='bold')
total = tRCD + tCAS
ax.annotate('', xy=(x0 + total + 2, row_y[1] + bar_h + 0.15), xytext=(x0 - 1, row_y[1] + bar_h + 0.15),
            arrowprops=dict(arrowstyle='<->', color='#333', lw=1.2))
ax.text(x0 + total/2, row_y[1] + bar_h + 0.35, f'Total: {total} cycles', ha='center', va='bottom', fontsize=7.5, fontweight='bold', color='#E65100')

# Row 2: Conflict — PRE + ACT + CAS
x0 = 5
ax.barh(row_y[2], tRP, height=bar_h, left=x0, color=C_PRE, edgecolor='white', linewidth=0.5)
ax.text(x0 + tRP/2, row_y[2] + bar_h/2, f'PRE ({tRP})', ha='center', va='center', fontsize=8, color='white', fontweight='bold')
ax.barh(row_y[2], tRCD, height=bar_h, left=x0 + tRP, color=C_ACT, edgecolor='white', linewidth=0.5)
ax.text(x0 + tRP + tRCD/2, row_y[2] + bar_h/2, f'ACT ({tRCD})', ha='center', va='center', fontsize=8, color='white', fontweight='bold')
ax.barh(row_y[2], tCAS, height=bar_h, left=x0 + tRP + tRCD, color=C_CAS, edgecolor='white', linewidth=0.5)
ax.text(x0 + tRP + tRCD + tCAS/2, row_y[2] + bar_h/2, f'CAS ({tCAS})', ha='center', va='center', fontsize=8, color='white', fontweight='bold')
total = tRP + tRCD + tCAS
ax.annotate('', xy=(x0 + total + 2, row_y[2] + bar_h + 0.15), xytext=(x0 - 1, row_y[2] + bar_h + 0.15),
            arrowprops=dict(arrowstyle='<->', color='#333', lw=1.2))
ax.text(x0 + total/2, row_y[2] + bar_h + 0.35, f'Total: {total} cycles', ha='center', va='bottom', fontsize=7.5, fontweight='bold', color=C_CONFLICT)

# ═══════════════════════════════════════════════════════════════════
# Panel (b): Three timeout precharge outcomes
# ═══════════════════════════════════════════════════════════════════
ax2 = axes[1]
ax2.set_xlim(-5, 165)
ax2.set_ylim(-0.5, 3.8)
ax2.axis('off')
ax2.set_title('(b) Timeout-Based Speculative Precharge Outcomes', fontsize=11, fontweight='bold', pad=8)

row_y2 = [2.8, 1.5, 0.2]
outcome_labels = [
    'Right Precharge\n(different row arrives)',
    'Wrong Precharge\n(same row reopened)',
    'Conflict\n(on-demand PRE before\ntimeout expires)'
]

for i, (y, label) in enumerate(zip(row_y2, outcome_labels)):
    ax2.text(-3, y + bar_h/2, label, ha='right', va='center', fontsize=8.5, fontweight='bold')

# Right precharge: idle -> timeout fires -> PRE -> new row ACT -> CAS (correct speculation)
x0 = 5
idle_w = 25
ax2.barh(row_y2[0], idle_w, height=bar_h, left=x0, color=C_IDLE, edgecolor='#999', linewidth=0.5)
ax2.text(x0 + idle_w/2, row_y2[0] + bar_h/2, 'Idle', ha='center', va='center', fontsize=8, color='#666')
# timeout fires
ax2.axvline(x=x0+idle_w, ymin=0.72, ymax=0.92, color=C_TIMEOUT, linewidth=1.5, linestyle='--')
ax2.text(x0+idle_w, row_y2[0] + bar_h + 0.35, 'Timeout\nexpires', ha='center', va='bottom', fontsize=7, color=C_TIMEOUT, fontweight='bold')
# PRE
pre_x = x0 + idle_w
ax2.barh(row_y2[0], tRP, height=bar_h, left=pre_x, color=C_PRE, edgecolor='white', linewidth=0.5)
ax2.text(pre_x + tRP/2, row_y2[0] + bar_h/2, 'PRE', ha='center', va='center', fontsize=8, color='white', fontweight='bold')
# New request to different row -> ACT + CAS (saves PRE time)
diff_x = pre_x + tRP
ax2.barh(row_y2[0], tRCD, height=bar_h, left=diff_x, color=C_ACT, edgecolor='white', linewidth=0.5)
ax2.text(diff_x + tRCD/2, row_y2[0] + bar_h/2, 'ACT', ha='center', va='center', fontsize=8, color='white', fontweight='bold')
ax2.barh(row_y2[0], tCAS, height=bar_h, left=diff_x + tRCD, color=C_CAS, edgecolor='white', linewidth=0.5)
ax2.text(diff_x + tRCD + tCAS/2, row_y2[0] + bar_h/2, 'CAS', ha='center', va='center', fontsize=8, color='white', fontweight='bold')
# Result annotation
ax2.text(diff_x + tRCD + tCAS + 5, row_y2[0] + bar_h/2, 'Penalty: 0', ha='left', va='center',
         fontsize=8, fontweight='bold', color=C_RIGHT)

# Wrong precharge: idle -> timeout fires -> PRE -> same row ACT -> CAS (unnecessary PRE+ACT)
x0 = 5
ax2.barh(row_y2[1], idle_w, height=bar_h, left=x0, color=C_IDLE, edgecolor='#999', linewidth=0.5)
ax2.text(x0 + idle_w/2, row_y2[1] + bar_h/2, 'Idle', ha='center', va='center', fontsize=8, color='#666')
ax2.axvline(x=x0+idle_w, ymin=0.36, ymax=0.56, color=C_TIMEOUT, linewidth=1.5, linestyle='--')
ax2.text(x0+idle_w, row_y2[1] + bar_h + 0.35, 'Timeout\nexpires', ha='center', va='bottom', fontsize=7, color=C_TIMEOUT, fontweight='bold')
pre_x = x0 + idle_w
ax2.barh(row_y2[1], tRP, height=bar_h, left=pre_x, color=C_PRE, edgecolor='white', linewidth=0.5)
ax2.text(pre_x + tRP/2, row_y2[1] + bar_h/2, 'PRE', ha='center', va='center', fontsize=8, color='white', fontweight='bold')
same_x = pre_x + tRP
ax2.barh(row_y2[1], tRCD, height=bar_h, left=same_x, color=C_ACT, edgecolor='white', linewidth=0.5)
ax2.text(same_x + tRCD/2, row_y2[1] + bar_h/2, 'ACT', ha='center', va='center', fontsize=8, color='white', fontweight='bold')
ax2.barh(row_y2[1], tCAS, height=bar_h, left=same_x + tRCD, color=C_CAS, edgecolor='white', linewidth=0.5)
ax2.text(same_x + tRCD + tCAS/2, row_y2[1] + bar_h/2, 'CAS', ha='center', va='center', fontsize=8, color='white', fontweight='bold')
# Highlight penalty
penalty_start = pre_x
penalty_end = same_x + tRCD
ax2.annotate('', xy=(penalty_end, row_y2[1] - 0.15), xytext=(penalty_start, row_y2[1] - 0.15),
            arrowprops=dict(arrowstyle='<->', color=C_WRONG, lw=1.2))
ax2.text((penalty_start + penalty_end)/2, row_y2[1] - 0.35, f'Penalty: tRP + tRCD = {tRP+tRCD} cyc',
         ha='center', va='top', fontsize=7.5, fontweight='bold', color=C_WRONG)

# Conflict: request arrives before timeout -> on-demand PRE + ACT + CAS
x0 = 5
short_idle = 12
ax2.barh(row_y2[2], short_idle, height=bar_h, left=x0, color=C_IDLE, edgecolor='#999', linewidth=0.5)
ax2.text(x0 + short_idle/2, row_y2[2] + bar_h/2, 'Idle', ha='center', va='center', fontsize=7.5, color='#666')
# Request arrives (before timeout)
req_x = x0 + short_idle
ax2.annotate('Request\n(diff. row)', xy=(req_x, row_y2[2] + bar_h + 0.05),
             xytext=(req_x, row_y2[2] + bar_h + 0.65),
             fontsize=7, ha='center', fontweight='bold', color='#333',
             arrowprops=dict(arrowstyle='->', color='#333', lw=1.0))
# On-demand PRE
ax2.barh(row_y2[2], tRP, height=bar_h, left=req_x, color=C_PRE, edgecolor='white', linewidth=0.5)
ax2.text(req_x + tRP/2, row_y2[2] + bar_h/2, 'PRE', ha='center', va='center', fontsize=8, color='white', fontweight='bold')
act_x = req_x + tRP
ax2.barh(row_y2[2], tRCD, height=bar_h, left=act_x, color=C_ACT, edgecolor='white', linewidth=0.5)
ax2.text(act_x + tRCD/2, row_y2[2] + bar_h/2, 'ACT', ha='center', va='center', fontsize=8, color='white', fontweight='bold')
ax2.barh(row_y2[2], tCAS, height=bar_h, left=act_x + tRCD, color=C_CAS, edgecolor='white', linewidth=0.5)
ax2.text(act_x + tRCD + tCAS/2, row_y2[2] + bar_h/2, 'CAS', ha='center', va='center', fontsize=8, color='white', fontweight='bold')
# Highlight penalty (only tRP is the penalty vs. right precharge)
penalty_start2 = req_x
penalty_end2 = req_x + tRP
ax2.annotate('', xy=(penalty_end2, row_y2[2] - 0.15), xytext=(penalty_start2, row_y2[2] - 0.15),
            arrowprops=dict(arrowstyle='<->', color=C_TCONFLICT, lw=1.2))
ax2.text((penalty_start2 + penalty_end2)/2, row_y2[2] - 0.35, f'Penalty: tRP = {tRP} cyc (vs. right precharge)',
         ha='center', va='top', fontsize=7.5, fontweight='bold', color=C_TCONFLICT)

plt.tight_layout()
savefig(fig, 'timing_diagram')
