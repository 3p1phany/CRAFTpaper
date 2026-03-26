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
RESULTS_DIR = '/root/data/smartPRE/champsim-la/results'
OUTPUT_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')

# ── LNCS template dimensions ─────────────────────────────────────────────
LNCS_TEXT_WIDTH = 4.803   # inches (12.2 cm)

# ── palette ───────────────────────────────────────────────────────────────
# Colorblind-friendly, grayscale-distinguishable, print-safe.

COLORS = {
    # Static policies (motivation)
    'open_page':   '#4472C4',  # steel blue
    'closed_page': '#C0504D',  # brick red

    # Our method
    'craft':       '#548235',  # forest green

    # Baselines
    'abp':         '#8B8B8B',  # slate gray
    'dympl':       '#ED7D31',  # sandy orange
    'intap':       '#7030A0',  # medium purple
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

# ── matplotlib defaults ───────────────────────────────────────────────────
def setup_style():
    """Call once at the top of each figure script."""
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.size': 10,
        'axes.linewidth': 0.8,
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

def short_name(bench):
    """Convert benchmark path to paper label.

    Examples:
        spec06/sphinx3/ref   -> SPEC06/sphinx3
        ligra/CF/higgs       -> Ligra/CF-higgs
        npb/CG               -> NPB/CG
        hpcc/RandAcc         -> HPCC/RandAcc
    """
    parts = bench.split('/')
    if len(parts) == 3:
        suite, prog, inp = parts
        sd = _SUITE_DISPLAY.get(suite, suite)
        if suite in ('spec06', 'spec17'):
            return f"{sd}/{prog}"
        g = _GRAPH_SHORT.get(inp, inp)
        return f"{sd}/{prog}-{g}"
    elif len(parts) == 2:
        suite, prog = parts
        sd = _SUITE_DISPLAY.get(suite, suite)
        return f"{sd}/{prog}"
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

def savefig(fig, name):
    """Save figure as both PNG (300 dpi) and PDF to output/."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for ext in ('png', 'pdf'):
        out = os.path.join(OUTPUT_DIR, f'{name}.{ext}')
        kwargs = {'dpi': 300} if ext == 'png' else {}
        fig.savefig(out, bbox_inches='tight', **kwargs)
    print(f'Saved to {OUTPUT_DIR}/{name}.{{png,pdf}}')
