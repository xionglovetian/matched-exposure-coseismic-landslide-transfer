# -*- coding: utf-8 -*-
"""Zero-shot evaluation of the source-scale models on the three primary targets.

Reuses the project's ManifestDataset and its SegmentationMetrics so the numbers are
directly comparable with the published reference benchmark.
"""

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, r"D:\landslide_unet_project")
sys.path.insert(0, r"D:\landslide_unet_project\scripts")
sys.path.insert(0, r"D:\landslide_unet_project\repos\AS-UNet")

import numpy as np
import torch
from torch.utils.data import DataLoader

from evaluate_external_benchmark import ManifestDataset, evaluate_checkpoint
from src.models import build_model

MANIFEST = r"D:\landslide_unet_project\data\processed\benchmark_v2_regions_512\manifest_benchmark_v2.csv"
TARGETS = ["hokkaido_iburi_tobu", "lombok", "palu"]
FLOOR = {"hokkaido_iburi_tobu": 0.1025, "lombok": 0.0307, "palu": 0.0121}
OUT = Path(r"C:\Users\ASUS\Desktop\五步协议\C2_瓦片级筛查\out\scale_experiment")

CKPTS = []
# k = 1 (baseline, existing checkpoints)
for seed in (42, 2026, 777):
    CKPTS.append((1, seed, Path(rf"D:\landslide_unet_project\outputs\q2_x2_aug_none_resunet_seed{seed}\best_model.pth")))
# k = 4 and 16 (new)
for k in (4, 16):
    for seed in (42, 2026, 777):
        CKPTS.append((k, seed, Path(rf"D:\landslide_unet_project\outputs\q2_sm_k{k}_resunet_seed{seed}\best_model.pth")))


def main():
    rows = list(csv.DictReader(open(MANIFEST, encoding="utf-8-sig")))
    rows = [r for r in rows if r.get("region") in TARGETS]
    print(f"evaluation tiles: {len(rows)} across {len(TARGETS)} regions")
    regions = TARGETS
    ds = ManifestDataset(rows, 128)
    loader = DataLoader(ds, batch_size=32, shuffle=False, num_workers=0, pin_memory=True)
    dev = torch.device("cuda")

    OUT.mkdir(parents=True, exist_ok=True)
    out = []
    for k, seed, ck in CKPTS:
        if not ck.exists():
            print(f"  missing k={k} seed={seed}: {ck}")
            continue
        state = torch.load(ck, map_location=dev, weights_only=False)
        model = build_model("ResUNet").to(dev)
        model.load_state_dict(state["state_dict"])
        metrics = evaluate_checkpoint(model, loader, regions, dev, True)
        rec = {"k": k, "seed": seed}
        for reg in regions:
            m = metrics[reg]["threshold_metrics"]["0.5"]
            rec[f"{reg}_iou"] = round(float(m["iou"]), 4)
        macro = float(np.mean([rec[f"{r}_iou"] for r in regions]))
        rec["macro_iou"] = round(macro, 4)
        out.append(rec)
        print(f"  k={k:<2} seed={seed:<5} macro={macro:.4f}  "
              + "  ".join(f"{r[:4]}={rec[f'{r}_iou']:.4f}" for r in regions), flush=True)
        del model
        torch.cuda.empty_cache()

    with open(OUT / "scale_zeroshot.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w.writeheader(); w.writerows(out)

    print("\n=== seed means by k ===")
    print(f"{'k':>3}{'macro IoU':>11}{'Hokkaido':>10}{'Lombok':>9}{'Palu':>8}{'above floor?':>15}")
    for k in sorted({r['k'] for r in out}):
        sel = [r for r in out if r["k"] == k]
        mm = np.mean([r["macro_iou"] for r in sel])
        hh = np.mean([r["hokkaido_iburi_tobu_iou"] for r in sel])
        lo = np.mean([r["lombok_iou"] for r in sel])
        pa = np.mean([r["palu_iou"] for r in sel])
        above = sum(1 for r in sel if r["hokkaido_iburi_tobu_iou"] > FLOOR["hokkaido_iburi_tobu"])
        print(f"{k:>3}{mm:>11.4f}{hh:>10.4f}{lo:>9.4f}{pa:>8.4f}{above:>10}/3  (Hokkaido floor 0.1025)")


if __name__ == "__main__":
    main()
