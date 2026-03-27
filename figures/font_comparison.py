#!/usr/bin/env python3
"""Font comparison for academic paper figures."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import os

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')

# Sample data (from normalized IPC)
labels = ['Ligra/CF-road', 'Ligra/CF-higgs', 'Ligra/PR-higgs',
          'SPEC06/sphinx3', 'SPEC06/wrf', 'GEOMEAN']
abp   = [0.891, 0.929, 0.925, 0.907, 0.924, 0.922]
craft = [1.0] * 6

COLORS = {
    'abp':   '#8B8B8B',
    'craft': '#548235',
    'dympl': '#ED7D31',
    'intap': '#7030A0',
}

# Font candidates
fonts = [
    ('DejaVu Sans',       'Current (DejaVu Sans)\nmatplotlib default, wide strokes'),
    ('TeX Gyre Heros',    'TeX Gyre Heros (= Helvetica)\nTop choice for CS papers'),
    ('Liberation Sans',   'Liberation Sans (= Arial)\nClean, widely available'),
    ('Roboto',            'Roboto\nGoogle\'s modern sans-serif'),
    ('Latin Modern Sans', 'Latin Modern Sans\nMatches LaTeX sans-serif'),
    ('TeX Gyre Termes',   'TeX Gyre Termes (= Times)\nMatches body text (serif)'),
]

fig, axes = plt.subplots(3, 2, figsize=(10, 12))

for ax, (font_name, desc) in zip(axes.flat, fonts):
    plt.rcParams.update({
        'font.family': font_name,
        'font.size': 7,
        'axes.linewidth': 0.8,
        'axes.labelsize': 7,
        'axes.titlesize': 8,
        'xtick.labelsize': 6,
        'ytick.labelsize': 6,
        'legend.fontsize': 6,
    })

    n = len(labels)
    x = np.arange(n)
    bar_w = 0.28

    ax.bar(x - bar_w*1.5, abp, bar_w, label='ABP', color=COLORS['abp'],
           edgecolor='white', linewidth=0.5)
    ax.bar(x - bar_w*0.5, [0.965]*6, bar_w, label='DYMPL', color=COLORS['dympl'],
           edgecolor='white', linewidth=0.5)
    ax.bar(x + bar_w*0.5, [0.970]*6, bar_w, label='INTAP', color=COLORS['intap'],
           edgecolor='white', linewidth=0.5)
    ax.bar(x + bar_w*1.5, craft, bar_w, label='CRAFT', color=COLORS['craft'],
           edgecolor='white', linewidth=0.5)

    ax.set_ylim(0.85, 1.03)
    ax.set_ylabel('Normalized IPC (CRAFT = 1.0)', fontfamily=font_name)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=35, ha='right', fontfamily=font_name)
    ax.tick_params(axis='y')
    ax.axhline(y=1.0, color='black', linestyle='-', linewidth=0.6, zorder=0)
    ax.axvline(x=n - 1.5, color='gray', linestyle='--', linewidth=0.8)
    ax.legend(loc='upper center', ncol=4, framealpha=0.9,
              edgecolor='gray', fancybox=False, bbox_to_anchor=(0.5, 1.18),
              prop={'family': font_name})
    ax.grid(axis='y', linestyle=':', alpha=0.3)

    # Title with description
    ax.set_title(desc, fontsize=9, fontweight='bold', fontfamily='DejaVu Sans',
                 pad=20)

fig.tight_layout(h_pad=3.0)
os.makedirs(OUTPUT_DIR, exist_ok=True)
fig.savefig(os.path.join(OUTPUT_DIR, 'font_comparison.png'),
            dpi=300, bbox_inches='tight')
print(f'Saved to {OUTPUT_DIR}/font_comparison.png')
