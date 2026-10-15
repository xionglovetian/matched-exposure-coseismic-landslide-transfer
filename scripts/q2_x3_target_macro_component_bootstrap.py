"""Target-macro connected-component bootstrap for the four-backbone X3 contrast.

This reproduces the component-bootstrap interval reported for every backbone in
the manuscript's matched-exposure contrast table. The three target regions are
collapsed into one macro average and only connected components of the reference
mask are resampled; the training seed is fixed. Regions and seeds are the frozen
Hokkaido Iburi-Tobu / Lombok / Palu and 42 / 2026 / 777.

Usage
-----
python scripts/q2_x3_target_macro_component_bootstrap.py \
    --tile-root metrics/q2_x3_tiles \
    --spatial-index data_manifests/target_spatial_index.csv \
    --output metrics/q2_x3_bootstrap/x3_target_macro_component.csv
"""
from __future__ import annotations

import argparse
import csv
import os as _repo_os
import sys
from pathlib import Path

import numpy as np

PROJECT = Path(_repo_os.environ.get("LANDSLIDE_PROJECT_ROOT", Path(__file__).resolve().parents[1])).resolve()
sys.path.insert(0, str(PROJECT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import route1_spatial_cluster_bootstrap as spatial
from q2_x3_spatial_bootstrap import REGIONS, SEEDS, build_pairs

ARCHITECTURES = {
    "resunet": "ResUNet",
    "bottleneckliteask": "Bottleneck-LiteASK",
    "segformerb0": "SegFormer-B0",
    "deeplabv3plus": "DeepLabV3+",
}
SEED_BASE = 20260927
SCHEME_INDEX = 1   # "component"
REGION_INDEX = 0   # "target_macro"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tile-root", default=str(PROJECT / "metrics" / "q2_x3_tiles"))
    parser.add_argument("--spatial-index", default=str(PROJECT / "data_manifests" / "target_spatial_index.csv"))
    parser.add_argument("--output", default=str(PROJECT / "metrics" / "q2_x3_bootstrap" / "x3_target_macro_component.csv"))
    parser.add_argument("--draws", type=int, default=10000)
    args = parser.parse_args()

    spatial.REGIONS = REGIONS
    spatial.SEEDS = SEEDS
    spatial_index = spatial.load_spatial_index(Path(args.spatial_index))

    rows_all = []
    for architecture_index, (slug, label) in enumerate(ARCHITECTURES.items()):
        pairs = build_pairs(Path(args.tile_root), slug)
        rng = np.random.default_rng(SEED_BASE + 10000 * architecture_index + 100 * SCHEME_INDEX + REGION_INDEX)
        rows = spatial.bootstrap_contrast(pairs, "target_macro", "component", spatial_index, rng, args.draws)
        for row in rows:
            row["architecture"] = label
        rows_all.extend(rows)
        print("done", label, flush=True)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows_all[0].keys()))
        writer.writeheader()
        writer.writerows(rows_all)
    print(f"wrote {output} ({len(rows_all)} rows)")


if __name__ == "__main__":
    main()
