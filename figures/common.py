"""
Shared config for all CRAFT paper figures.

- COLORS / COLORS_DARK: unified palette
- short_name(): benchmark labeling
- read_summary() / read_comparison(): data loading helpers
- RESULTS_DIR: path to simulation results

Usage:
    from common import *
"""

import os
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

# ── data path ─────────────────────────────────────────────────────────────
RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'fig_data')
OUTPUT_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')

# ── LNCS template dimensions ─────────────────────────────────────────────
LNCS_TEXT_WIDTH = 4.803   # inches (12.2 cm)

# ── palette ───────────────────────────────────────────────────────────────
# Colorblind-friendly, grayscale-distinguishable, print-safe.

COLORS = {
    # Semantic anchors used across figures
    'open_page':   '#4472C4',  # steel blue — Open-Page policy
    'closed_page': '#C0504D',  # brick red  — Closed-Page policy
    'craft':       '#548235',  # forest green — CRAFT (our method)
    'dympl':       '#ED7D31',  # sandy orange — DYMPL baseline

    # Algorithm-specific neutrals
    'abp':         '#8B8B8B',  # slate gray — ABP baseline
    'intap':       '#7030A0',  # medium purple — INTAP baseline

    # Utility colors
    'trace':       '#566574',  # neutral line color for workload traces
    'idle':        '#EBEBEB',  # light gray — idle periods in timing diagrams
}

# Darker variants for text annotations
COLORS_DARK = {
    'open_page':   '#2B5080',
    'closed_page': '#8B2F2F',
    'craft':       '#3B5E25',
    'abp':         '#555555',
    'dympl':       '#B85A15',
    'intap':       '#4A1F6E',
}

# Light background fills for diagram boxes
COLORS_BG = {
    'closed_page': '#FCE8E8',  # wrong precharge background
    'craft':       '#E8F4E6',  # right precharge background
    'dympl':       '#FEF0E0',  # conflict background
    'open_page':   '#E6EEF5',  # timeout box background
}

# Hatch patterns for bar charts (black-and-white friendly)
HATCHES = {
    'open_page':   '////',
    'closed_page': '\\\\\\\\',
    'craft':       'xxxx',
    'abp':         '....',
    'dympl':       '++++',
    'intap':       'oooo',
}

# ── standardized font sizes ───────────────────────────────────────────────
# Use these constants in all figure scripts for consistency.
# Designed for LNCS single-column width (4.803 in / 12.2 cm).
FONT_TITLE      = 8    # subplot titles
FONT_AXIS_LABEL = 7    # axis labels (xlabel, ylabel)
FONT_TICK        = 6    # tick labels (x and y)
FONT_TICK_DENSE = 5.5  # dense categorical x-axis labels in bar charts
FONT_LEGEND      = 6    # legend text
FONT_ANNOT       = 5.5  # value annotations on bars / data points
FONT_DETAIL      = 5    # fine-grained labels (state labels, sub-annotations)

# ── matplotlib defaults ───────────────────────────────────────────────────
def setup_style():
    """Call once at the top of each figure script."""
    plt.rcParams.update({
        # Use a paper-standard Helvetica-style family across all figures.
        'font.family': 'TeX Gyre Heros',
        'font.sans-serif': ['TeX Gyre Heros'],
        'font.size': 7,
        'mathtext.fontset': 'custom',
        'mathtext.rm': 'TeX Gyre Heros',
        'mathtext.sf': 'TeX Gyre Heros',
        'mathtext.it': 'TeX Gyre Heros:italic',
        'mathtext.bf': 'TeX Gyre Heros:bold',
        'mathtext.default': 'regular',
        'pdf.fonttype': 42,
        'ps.fonttype': 42,
        'axes.unicode_minus': False,
        'axes.linewidth': 0.8,
        'axes.labelsize': FONT_AXIS_LABEL,
        'axes.labelweight': 'bold',
        'axes.titlesize': FONT_TITLE,
        'axes.titleweight': 'bold',
        'xtick.labelsize': FONT_TICK,
        'ytick.labelsize': FONT_TICK,
        'legend.fontsize': FONT_LEGEND,
    })

# ── benchmark naming ──────────────────────────────────────────────────────
_SUITE_DISPLAY = {
    'spec06': 'SPEC06', 'spec17': 'SPEC17',
    'ligra': 'Ligra', 'crono': 'Crono',
    'npb': 'NPB', 'hpcc': 'HPCC',
    'hashjoin': 'HashJoin', 'graph500': 'Graph500', 'spmv': 'SpMV',
}

_GRAPH_SHORT = {
    'roadNet-CA': 'road', 'soc-pokec': 'pokec',
    'soc-pokec-short': 'pokec-s', 'higgs': 'higgs',
    'Amazon0312': 'amzn', 's16-e10': 's16',
}

_PROG_SHORT = {
    'Components-Shortcut': 'CompS',
    'Triangle-Counting': 'TriCnt',
    'PageRank': 'PR',
    'Triangle': 'Tri',
    'RandAcc_LCG': 'LCG',
    'hj-8-NPO_st': 'hj-8',
}

def short_name(bench):
    """Convert benchmark path to paper label.

    Examples:
        spec06/sphinx3/ref                    -> SPEC06/sphinx3
        ligra/CF/higgs                        -> Ligra/CF-higgs
        ligra/Components-Shortcut/soc-pokec   -> Ligra/CompS-pokec
        npb/CG                                -> NPB/CG
    """
    parts = bench.split('/')
    if len(parts) == 3:
        suite, prog, inp = parts
        sd = _SUITE_DISPLAY.get(suite, suite)
        if suite in ('spec06', 'spec17'):
            return f"{sd}/{prog}"
        p = _PROG_SHORT.get(prog, prog)
        g = _GRAPH_SHORT.get(inp, inp)
        return f"{sd}/{p}-{g}"
    elif len(parts) == 2:
        suite, prog = parts
        sd = _SUITE_DISPLAY.get(suite, suite)
        p = _PROG_SHORT.get(prog, prog)
        return f"{sd}/{p}"
    return bench

# ── data loading ──────────────────────────────────────────────────────────
def read_summary(dirname):
    """Read results/<dirname>/summary.tsv -> {benchmark: ipc}."""
    path = os.path.join(RESULTS_DIR, dirname, 'summary.tsv')
    d = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith('benchmark') or not line:
                continue
            parts = line.split('\t')
            d[parts[0]] = float(parts[1])
    return d

def read_comparison(filename):
    """Read a comparison TSV -> {benchmark: (ipc_A, ipc_B)}."""
    path = os.path.join(RESULTS_DIR, filename)
    d = {}
    with open(path) as f:
        f.readline()  # header
        for line in f:
            line = line.strip()
            if not line or line.startswith('__'):
                continue
            parts = line.split('\t')
            d[parts[0]] = (float(parts[1]), float(parts[2]))
    return d

def set_categorical_xticks(ax, positions, labels, rotation=35, ha='right',
                           fontsize=FONT_TICK_DENSE):
    """Apply a unified style for dense categorical x-axis labels."""
    ax.set_xticks(positions)
    ax.set_xticklabels(labels, rotation=rotation, ha=ha)
    ax.tick_params(axis='x', labelsize=fontsize)

def savefig(fig, name):
    """Save figure as both PNG (300 dpi) and PDF to output/."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for ext in ('png', 'pdf'):
        out = os.path.join(OUTPUT_DIR, f'{name}.{ext}')
        kwargs = {'dpi': 300} if ext == 'png' else {}
        fig.savefig(out, bbox_inches='tight', pad_inches=0.02, **kwargs)
    print(f'Saved to {OUTPUT_DIR}/{name}.{{png,pdf}}')
