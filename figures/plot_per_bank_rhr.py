"""
Per-bank row buffer hit rate bar chart.
Shows inter-bank RHR variance for three benchmarks under open-page policy.
Each benchmark is plotted as a separate subplot with per-bank bars.
"""

from common import *
import json

# ── data loading ─────────────────────────────────────────────────────────
DATA_DIR = '/root/data/smartPRE/champsim-la/results/per_bank_rhr'
NUM_BANKS = 32


def load_per_bank_rhr(bench):
    """Load per-bank row hit rate from ddr.json, aggregated across channels."""
    with open(os.path.join(DATA_DIR, bench, 'ddr.json')) as f:
        data = json.load(f)

    hits = [0] * NUM_BANKS
    misses = [0] * NUM_BANKS
    for ch_data in data.values():
        if 'per_bank_row_hits' not in ch_data:
            continue
        for bank_str, val in ch_data['per_bank_row_hits'].items():
            hits[int(bank_str)] += val
        for bank_str, val in ch_data['per_bank_row_misses'].items():
            misses[int(bank_str)] += val

    rhr = []
    for b in range(NUM_BANKS):
        total = hits[b] + misses[b]
        rhr.append(hits[b] / total * 100 if total > 0 else 0)
    return rhr


# ── load all benchmarks ──────────────────────────────────────────────────
benchmarks = [
    ('lbm',     'lbm (CoV = 0.001)'),
    ('mcf',     'mcf (CoV = 0.022)'),
    ('omnetpp', 'omnetpp (CoV = 1.512)'),
]

all_rhr = {}
for key, label in benchmarks:
    all_rhr[key] = load_per_bank_rhr(key)

# ── plot bar chart ───────────────────────────────────────────────────────
setup_style()

fig, axes = plt.subplots(3, 1, figsize=(LNCS_TEXT_WIDTH, 4.5), sharex=True)

bar_color_keys = ['open_page', 'dympl', 'intap']
bank_ids = np.arange(NUM_BANKS)
bar_width = 0.8

for idx, ((key, label), ax, ck) in enumerate(
        zip(benchmarks, axes, bar_color_keys)):
    rhr = all_rhr[key]
    ax.bar(bank_ids, rhr, width=bar_width, color=COLORS[ck], hatch=HATCHES[ck],
           edgecolor='black', linewidth=0.8)

    # y-axis: set range to highlight the actual data spread
    rhr_min, rhr_max = min(rhr), max(rhr)
    if rhr_max - rhr_min < 15:
        # narrow spread: zoom in to show the variation
        pad = max(3, (rhr_max - rhr_min) * 0.5)
        y_lo = max(0, rhr_min - pad)
        y_hi = min(100, rhr_max + pad)
    else:
        y_lo = 0
        y_hi = min(100, rhr_max + 5)
    ax.set_ylim(y_lo, y_hi)

    ax.set_ylabel('RBHR (%)')
    ax.set_title(label, pad=4)

    # light grid
    ax.yaxis.grid(True, linestyle=':', alpha=0.3)
    ax.set_axisbelow(True)

    # mean line with label placed at top-right inside the axes
    mean_val = np.mean(rhr)
    ax.axhline(mean_val, color='black', linestyle='--', linewidth=0.8,
               alpha=0.5, label=f'mean = {mean_val:.1f}%')
    ax.legend(fontsize=FONT_LEGEND, loc='upper right', framealpha=0.8,
              edgecolor='gray', handlelength=1.5)

axes[-1].set_xlabel('Bank ID')
axes[-1].set_xticks(range(0, NUM_BANKS, 4))
axes[-1].set_xticklabels([str(b) for b in range(0, NUM_BANKS, 4)])

fig.tight_layout(h_pad=0.8)
savefig(fig, 'per_bank_rhr_comparison')
print('Done.')
