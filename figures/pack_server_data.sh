#!/bin/bash
# Run this on the server to pack all data files needed by figure scripts.
# Usage: bash pack_server_data.sh
# Output: ~/fig_data.tar.gz

set -e

BASE="/root/data/smartPRE/champsim-la"
RESULTS="$BASE/results"
TMPDIR=$(mktemp -d)
DEST="$TMPDIR/fig_data"
mkdir -p "$DEST"

echo "=== Packing fig_motivation_combined data ==="

# Panel (a): IPC comparison TSVs
mkdir -p "$DEST/GS_1c"
cp "$RESULTS/GS_1c/compare_vs_open.tsv" "$DEST/GS_1c/"
cp "$RESULTS/compare_GS_vs_smart_close_1c.tsv" "$DEST/"

# Panel (b): epoch data for 4 benchmarks
for p in \
    "open_page_1c/spec17/mcf/ref/5" \
    "open_page_1c/crono/PageRank/soc-pokec/0" \
    "open_page_1c/spec06/GemsFDTD/ref/17" \
    "open_page_1c/spec06/zeusmp/ref/23"; do
    mkdir -p "$DEST/$p"
    cp "$RESULTS/$p/ddrepoch.json" "$DEST/$p/"
    echo "  copied $p/ddrepoch.json"
done

echo "=== Packing fig_timeout_evolution data ==="

# Manifest
cp "$BASE/benchmarks_selected.tsv" "$DEST/"

# CRAFT_PRECHARGE_1c epoch data for 3 benchmarks (all slices from manifest)
for bench in "ligra/CF/roadNet-CA" "ligra/CF/higgs" "spec06/sphinx3/ref"; do
    # Extract slice IDs from manifest
    slices=$(awk -v b="$bench" '$1 == b {print $2}' "$BASE/benchmarks_selected.tsv")
    for s in $slices; do
        src="$RESULTS/CRAFT_PRECHARGE_1c/$bench/$s/ddrepoch.json"
        if [ -f "$src" ]; then
            mkdir -p "$DEST/CRAFT_PRECHARGE_1c/$bench/$s"
            cp "$src" "$DEST/CRAFT_PRECHARGE_1c/$bench/$s/"
            echo "  copied CRAFT_PRECHARGE_1c/$bench/$s/ddrepoch.json"
        else
            echo "  WARNING: $src not found, skipping"
        fi
    done
done

# Pack
OUTFILE="$HOME/fig_data.tar.gz"
tar -czf "$OUTFILE" -C "$TMPDIR" fig_data
rm -rf "$TMPDIR"
echo ""
echo "=== Done! ==="
echo "Output: $OUTFILE ($(du -h "$OUTFILE" | cut -f1))"
echo ""
echo "Transfer to local machine:"
echo "  scp server:~/fig_data.tar.gz ."
