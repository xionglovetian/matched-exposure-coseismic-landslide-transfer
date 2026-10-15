"""Partial E1 diagnostic: pixel-level background false-alarm rate.

This is NOT the pre-registered E1. The pre-registered E1 requires tiles with
zero reference foreground, and those tiles do not exist in the distributed
archive (the released region archives are already foreground-filtered). What can
be computed from the packaged tile metrics is the false-positive share of
background pixels inside the evaluated positive-containing tiles: FP / (FP + TN).

Usage
-----
python scripts/e1_partial_background_false_alarm.py \
    --tile-root metrics/q2_x3_tiles \
    --output-md reports/revision_20261015/E1_partial_background_false_alarm.md \
    --output-csv metrics/e1_partial_background_false_alarm.csv
"""
from __future__ import annotations

import argparse
import csv
import os as _repo_os
from pathlib import Path

PROJECT = Path(_repo_os.environ.get("LANDSLIDE_PROJECT_ROOT", Path(__file__).resolve().parents[1])).resolve()

ARCHITECTURES = {
    "resunet": "ResUNet",
    "bottleneckliteask": "Bottleneck-LiteASK",
    "segformerb0": "SegFormer-B0",
    "deeplabv3plus": "DeepLabV3+",
}
REGIONS = ["hokkaido_iburi_tobu", "lombok", "palu"]
SEEDS = [42, 2026, 777]
ARMS = ["pooled", "cas-multistream"]
T_CRITICAL_95_DF2 = 4.302652729911275


def load(tile_root: Path, slug: str, arm: str, seed: int) -> list[dict]:
    path = tile_root / f"q2_x3_{slug}_{arm}_seed{seed}.tiles.csv"
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def background_false_positive_rate(rows: list[dict], region: str) -> float:
    fp = tn = 0
    for row in rows:
        if row["region"] != region:
            continue
        fp += int(row["fp"])
        tn += int(row["tn"])
    return fp / (fp + tn) if (fp + tn) else float("nan")


def t_interval(values: list[float]) -> tuple[float, float, float, float]:
    n = len(values)
    mean = sum(values) / n
    sd = (sum((value - mean) ** 2 for value in values) / (n - 1)) ** 0.5
    se = sd / n ** 0.5
    return mean, sd, mean - T_CRITICAL_95_DF2 * se, mean + T_CRITICAL_95_DF2 * se


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tile-root", default=str(PROJECT / "metrics" / "q2_x3_tiles"))
    parser.add_argument("--output-md", default=str(PROJECT / "reports" / "revision_20261015" / "E1_partial_background_false_alarm.md"))
    parser.add_argument("--output-csv", default=str(PROJECT / "metrics" / "e1_partial_background_false_alarm.csv"))
    args = parser.parse_args()

    tile_root = Path(args.tile_root)
    summary: dict[tuple[str, str, str], tuple[float, float, float]] = {}
    csv_rows = []
    for slug, label in ARCHITECTURES.items():
        for arm in ARMS:
            for region in REGIONS:
                values = [background_false_positive_rate(load(tile_root, slug, arm, seed), region) * 100.0 for seed in SEEDS]
                mean, sd, low, high = t_interval(values)
                summary[(label, arm, region)] = (mean, low, high)
                csv_rows.append({
                    "architecture": label, "arm": arm, "region": region, "unit": "pixel_within_positive_tiles",
                    "mean_background_fp_rate_percent": mean, "sd_across_seeds": sd,
                    "ci95_low": low, "ci95_high": high,
                    "seed_values_percent": ";".join(f"{value:.6f}" for value in values),
                })
            macro = sum(summary[(label, arm, region)][0] for region in REGIONS) / len(REGIONS)
            csv_rows.append({
                "architecture": label, "arm": arm, "region": "three_region_mean", "unit": "pixel_within_positive_tiles",
                "mean_background_fp_rate_percent": macro, "sd_across_seeds": "", "ci95_low": "", "ci95_high": "",
                "seed_values_percent": "",
            })

    csv_path = Path(args.output_csv)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(csv_rows[0].keys()))
        writer.writeheader()
        writer.writerows(csv_rows)

    lines = [
        "# E1 partial: pixel-level background false-alarm rate from existing tile outputs",
        "",
        "This is NOT the pre-registered E1. The pre-registered E1 needs tiles with zero reference foreground, which do not exist",
        "in the distributed dataset. What can be computed from outputs already on disk is the false-positive share of",
        "background pixels inside the evaluated (positive-containing) tiles: FP / (FP + TN).",
        "",
        "| Backbone | Arm | Region | Background FP rate (%) | Seeds 42 / 2026 / 777 |",
        "|---|---|---|---:|---|",
    ]
    for slug, label in ARCHITECTURES.items():
        for arm in ARMS:
            for region in REGIONS:
                values = [background_false_positive_rate(load(tile_root, slug, arm, seed), region) * 100.0 for seed in SEEDS]
                lines.append(f"| {label} | {arm} | {region} | {summary[(label, arm, region)][0]:.3f} | "
                             + " / ".join(f"{value:.3f}" for value in values) + " |")
            macro = sum(summary[(label, arm, region)][0] for region in REGIONS) / len(REGIONS)
            lines.append(f"| {label} | {arm} | **three-region mean** | **{macro:.3f}** | |")
    lines += [
        "",
        "## Reading",
        "",
        "The direction is region-dependent, not uniform:",
        "",
        "- **Hokkaido Iburi-Tobu**: the pooled arm cuts the background false-positive share sharply in all four backbones.",
        "- **Palu**: a smaller reduction in all four backbones.",
        "- **Lombok**: the pooled arm *raises* the background false-positive share in all four backbones.",
        "",
        "So the false-alarm side of the ledger follows the same region dependence as the headline effect, and Lombok moves in the",
        "opposite direction on this endpoint.",
        "",
        "**Scope.** This is a pixel-level measure inside tiles that contain at least one reference landslide pixel. It does **not**",
        "measure tile-level false alarms on tiles that contain no reference landslide, which is what the pre-registered E1 requires.",
        "It can be reported as a supporting diagnostic, never as a substitute for E1.",
    ]
    md_path = Path(args.output_md)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {md_path} and {csv_path}")


if __name__ == "__main__":
    main()
