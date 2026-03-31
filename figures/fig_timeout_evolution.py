#!/usr/bin/env python3
"""Figure: Timeout distribution evolution over execution epochs.

Shows how CRAFT's timeout values adapt over time for three representative
benchmarks, one from each adaptation regime (Keep Open, Balanced, Aggressive Close).

Concatenates epoch data from all weighted slices to show the full execution.
"""

import sys, os, json
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

setup_style()

# ── config ────────────────────────────────────────────────────────────────
BASE = os.path.join(RESULTS_DIR, 'CRAFT_PRECHARGE_1c')
MANIFEST_PATH = os.path.join(RESULTS_DIR, 'benchmarks_selected.tsv')

# Representative benchmarks
BENCHMARKS = [
    ('ligra/CF/roadNet-CA', 'CF/roadNet-CA — Keep Open'),
    ('ligra/CF/higgs',      'CF/higgs — Gradual Transition'),
    ('spec06/sphinx3/ref',  'sphinx3 — Periodic Phases'),
]

LOW_BINS  = [f'craft_timeout_value_sum[{lo}-{lo+99}]' for lo in range(0, 800, 100)]
MID_BINS  = [f'craft_timeout_value_sum[{lo}-{lo+99}]' for lo in range(800, 2000, 100)]
HIGH_BINS = [f'craft_timeout_value_sum[{lo}-{lo+99}]' for lo in range(2000, 3200, 100)]
HIGH_BINS.append('craft_timeout_value_sum[3200-]')

# Colors matching fig_timeout_distribution.py
COLOR_LOW  = COLORS['closed_page']
COLOR_MID  = COLORS['dympl']
COLOR_HIGH = COLORS['open_page']

SMOOTH_MIN_WIN = 9  # minimum smoothing window


def smooth_and_renorm(lows, mids, highs):
    """Moving-average smooth each series, then renormalize to 100%."""
    n = len(lows)
    win = max(SMOOTH_MIN_WIN, int(n * 0.08)) | 1  # ensure odd, at least 9
    kernel = np.ones(win) / win
    pad = win // 2
    s_lo = np.convolve(np.pad(lows, pad, mode='edge'), kernel, mode='valid')
    s_mi = np.convolve(np.pad(mids, pad, mode='edge'), kernel, mode='valid')
    s_hi = np.convolve(np.pad(highs, pad, mode='edge'), kernel, mode='valid')
    total = s_lo + s_mi + s_hi
    total[total == 0] = 1
    s_lo = 100.0 * s_lo / total
    s_mi = 100.0 * s_mi / total
    s_hi = 100.0 * s_hi / total
    return s_lo.tolist(), s_mi.tolist(), s_hi.tolist()


def load_manifest():
    """Load benchmarks_selected.tsv -> {benchmark: [(slice_id, weight), ...]}"""
    manifest = defaultdict(list)
    with open(MANIFEST_PATH) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if parts[0].lower() == 'benchmark':
                continue
            bench, sl, weight = parts[0], parts[1], float(parts[2])
            manifest[bench].append((sl, weight))
    return dict(manifest)


def load_epoch_series_single(bench_path, slice_id):
    """Load ddrepoch.json for a single slice, aggregate across channels.

    Returns lists of (low%, mid%, high%) per time point,
    skipping time points with zero precharges.
    """
    ep_path = os.path.join(BASE, bench_path, str(slice_id), 'ddrepoch.json')
    with open(ep_path) as f:
        epochs = json.load(f)

    n_channels = 4
    n_timepoints = len(epochs) // n_channels

    lows, mids, highs = [], [], []
    for t in range(n_timepoints):
        total_prech = 0
        total_low = 0
        total_high = 0
        for c in range(n_channels):
            ep = epochs[t * n_channels + c]
            prech = ep.get('craft_timeout_precharges', 0)
            total_prech += prech
            total_low += sum(ep.get(b, 0) for b in LOW_BINS)
            total_high += sum(ep.get(b, 0) for b in HIGH_BINS)
        if total_prech == 0:
            continue
        total_mid = total_prech - total_low - total_high
        lows.append(100.0 * total_low / total_prech)
        mids.append(100.0 * total_mid / total_prech)
        highs.append(100.0 * total_high / total_prech)

    return lows, mids, highs


def load_epoch_series_all(bench_path, slices):
    """Load and concatenate epoch data from all slices, scaled by weight.

    Returns (t_pct, lows, mids, highs) where t_pct maps to [0, 100].
    Each slice occupies a portion of the x-axis proportional to its weight.
    """
    total_weight = sum(w for _, w in slices)

    all_t = []
    all_lows = []
    all_mids = []
    all_highs = []

    cumulative_pct = 0.0
    for sl_id, weight in sorted(slices, key=lambda x: int(x[0])):
        slice_span = 100.0 * weight / total_weight

        lows, mids, highs = load_epoch_series_single(bench_path, sl_id)
        if not lows:
            cumulative_pct += slice_span
            continue

        n = len(lows)
        for i in range(n):
            t = cumulative_pct + slice_span * i / max(n - 1, 1)
            all_t.append(t)
            all_lows.append(lows[i])
            all_mids.append(mids[i])
            all_highs.append(highs[i])

        cumulative_pct += slice_span

    return all_t, all_lows, all_mids, all_highs


# ── load manifest ────────────────────────────────────────────────────────
manifest = load_manifest()

# ── plot (vertical stack for LNCS single-column) ─────────────────────────
fig, axes = plt.subplots(3, 1, figsize=(LNCS_TEXT_WIDTH, 3.5), sharey=True)

for ax, (bench, title) in zip(axes, BENCHMARKS):
    slices = manifest.get(bench, [('0', 1.0)])
    t_pct, lows, mids, highs = load_epoch_series_all(bench, slices)
    lows, mids, highs = smooth_and_renorm(lows, mids, highs)

    ax.fill_between(t_pct, 0, lows, color=COLOR_LOW, alpha=0.85, linewidth=0)
    ax.fill_between(t_pct, lows, [l + m for l, m in zip(lows, mids)],
                    color=COLOR_MID, alpha=0.85, linewidth=0)
    ax.fill_between(t_pct, [l + m for l, m in zip(lows, mids)],
                    [l + m + h for l, m, h in zip(lows, mids, highs)],
                    color=COLOR_HIGH, alpha=0.85, linewidth=0)

    ax.set_title(title, fontsize=FONT_TITLE, fontweight='bold')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_xlabel('Execution Progress (%)')
    ax.grid(axis='y', linestyle=':', alpha=0.3)

axes[0].set_ylabel('Timeout Dist. (%)')
axes[1].set_ylabel('Timeout Dist. (%)')
axes[2].set_ylabel('Timeout Dist. (%)')

# Shared legend
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor=COLOR_LOW, label='Low [50, 800)'),
    Patch(facecolor=COLOR_MID, label='Mid [800, 2 000)'),
    Patch(facecolor=COLOR_HIGH, label='High [2 000, 3 200]'),
]
fig.legend(handles=legend_elements, loc='upper center', ncol=3,
           fontsize=FONT_LEGEND, framealpha=0.9, edgecolor='gray',
           fancybox=False, bbox_to_anchor=(0.5, 1.03))

fig.tight_layout(rect=[0, 0, 1, 0.96])
savefig(fig, 'timeout_evolution')
