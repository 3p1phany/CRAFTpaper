#!/usr/bin/env python3
"""Figure: Causal chain — Read HR improvement -> Latency reduction -> IPC gain."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

setup_style()

# ── data (from row_buffer_hit_rate_analysis.md Section 6) ────────────────
benchmarks = [
    'ligra/CF/roadNet-CA',
    'ligra/CF/higgs',
    'ligra/PageRank/higgs',
    'ligra/BFSCC/soc-pokec-short',
    'spec06/sphinx3/ref',
    'ligra/CF/soc-pokec',
    'ligra/Triangle/roadNet-CA',
    'ligra/PageRank/roadNet-CA',
    'crono/Triangle-Counting/roadNet-CA',
    'spec06/wrf/ref',
    'ligra/Components-Shortcut/soc-pokec',
    'ligra/Radii/higgs',
]

# Read HR improvement (pp), latency reduction (%), IPC improvement (%)
read_hr = [9.25, 6.44, 1.59, 6.83, 7.76, 4.15, 5.35, 9.12, 3.46, 4.98, 1.82, 6.68]
latency = [5.66, 1.84, 1.03, 3.49, 5.86, 0.45, 2.63, 5.29, 1.24, 2.48, 0.22, 2.72]
ipc     = [5.79, 3.10, 2.87, 2.85, 2.60, 2.02, 2.00, 1.89, 1.74, 1.65, 1.63, 1.61]

labels = [short_name(b) for b in benchmarks]
n = len(labels)
x = np.arange(n)

# ── three-panel figure (vertical stack for LNCS single-column) ───────────
fig, axes = plt.subplots(3, 1, figsize=(LNCS_TEXT_WIDTH, 7.0), sharey=False)

panel_data = [
    (read_hr, 'Read HR Improvement (pp)', '#4472C4', '+{:.1f}'),
    (latency, 'Read Latency Reduction (%)', '#C0504D', '-{:.1f}'),
    (ipc,     'IPC Improvement (%)',         COLORS['craft'], '+{:.1f}'),
]

panel_titles = [
    '(a) Read Row Buffer Hit Rate',
    '(b) Average Read Latency',
    '(c) IPC vs. Best Baseline',
]

# Add arrow annotations between panels
arrow_positions = [0.68, 0.37]

for ax, (data, ylabel, color, fmt), title in zip(axes, panel_data, panel_titles):
    bars = ax.bar(x, data, 0.65, color=color, edgecolor='white', linewidth=0.5)

    # Value annotations
    for xi, val in zip(x, data):
        ax.text(xi, val + 0.15, fmt.format(val),
                ha='center', va='bottom', fontsize=5, fontweight='bold',
                color=color)

    # Averages
    avg = sum(data) / len(data)
    ax.axhline(y=avg, color='black', linestyle='--', linewidth=0.8, alpha=0.5)
    ax.text(n - 0.5, avg + 0.15, f'avg {fmt.format(avg)}',
            ha='right', va='bottom', fontsize=5.5, fontstyle='italic')

    ax.set_ylabel(ylabel, fontsize=7)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=90, ha='center', fontsize=5.5)
    ax.set_title(title, fontsize=8, fontweight='bold')
    ax.tick_params(axis='y', labelsize=6)
    ax.grid(axis='y', linestyle=':', alpha=0.3)
    ax.set_xlim(-0.5, n - 0.5)

for y_pos in arrow_positions:
    fig.text(0.5, y_pos, r'$\Downarrow$', fontsize=14,
             ha='center', va='center', fontweight='bold')

fig.tight_layout(rect=[0, 0, 1, 0.98], h_pad=2.5)
savefig(fig, 'causal_chain')
