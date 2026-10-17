# -*- coding: utf-8 -*-
"""Evaluation-scale sweep: does the model work better when the target imagery is
smoothed before inference?

Only the input image is resampled (down to 1/s then back to 128 px); the reference
mask and the geometry are untouched, so this isolates "how much fine detail does the
model need" from any change in the labels.
"""

import csv
import sys
from pathlib import Path

sys.path.insert(0, r"D:\landslide_unet_project")
sys.path.insert(0, r"D:\landslide_unet_project\scripts")
sys.path.insert(0, r"D:\landslide_unet_project\repos\AS-UNet")

import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader

from evaluate_external_benchmark import ManifestDataset
from src.models import build_model

MANIFEST = r"D:\landslide_unet_project\data\processed\benchmark_v2_regions_512\manifest_benchmark_v2.csv"
TARGETS = ["hokkaido_iburi_tobu", "lombok", "palu"]
FLOOR = {"hokkaido_iburi_tobu": 0.1025, "lombok": 0.0307, "palu": 0.0121}
SCALES = [1, 2, 4, 8, 16]
OUT = Path(r"C:\Users\ASUS\Desktop\五步协议\C2_瓦片级筛查\out\scale_sweep")

CKPTS = []
for seed in (42, 2026, 777):
    CKPTS.append(("source-only", seed,
                  Path(rf"D:\landslide_unet_project\outputs\q2_x2_aug_none_resunet_seed{seed}\best_model.pth")))
for seed in (42, 2026, 777):
    CKPTS.append(("pooled", seed,
                  Path(rf"D:\landslide_unet_project\outputs\q2_x3_resunet_pooled_seed{seed}\final_model.pth")))


def coarsen(x, s):
    if s == 1:
        return x
    n = max(1, x.shape[-1] // s)
    down = F.interpolate(x, size=(n, n), mode="bilinear", align_corners=False)
    return F.interpolate(down, size=x.shape[-2:], mode="bilinear", align_corners=False)


def main():
    rows = list(csv.DictReader(open(MANIFEST, encoding="utf-8-sig")))
    rows = [r for r in rows if r.get("region") in TARGETS]
    print(f"tiles: {len(rows)}")
    ds = ManifestDataset(rows, 128)
    loader = DataLoader(ds, batch_size=32, shuffle=False, num_workers=4, pin_memory=True)
    dev = torch.device("cuda")

    OUT.mkdir(parents=True, exist_ok=True)
    out = []
    for kind, seed, ck in CKPTS:
        if not ck.exists():
            print(f"  MISSING {kind} seed={seed}: {ck}")
            continue
        state = torch.load(ck, map_location=dev, weights_only=False)
        model = build_model("ResUNet").to(dev)
        model.load_state_dict(state["state_dict"])
        model.eval()
        for s in SCALES:
            counts = {r: {"tp": 0.0, "fp": 0.0, "fn": 0.0} for r in TARGETS}
            with torch.inference_mode():
                for image, mask, batch_regions in loader:
                    image = coarsen(image.to(dev, non_blocking=True), s)
                    target = (mask.to(dev, non_blocking=True) >= 0.5).float()
                    with torch.amp.autocast("cuda", dtype=torch.bfloat16):
                        prob = torch.sigmoid(model(image).float())
                    pred = (prob >= 0.5).float()
                    for i, reg in enumerate(batch_regions):
                        p = pred[i]
                        t = target[i]
                        counts[reg]["tp"] += float((p * t).sum())
                        counts[reg]["fp"] += float((p * (1 - t)).sum())
                        counts[reg]["fn"] += float(((1 - p) * t).sum())
            rec = {"model": kind, "seed": seed, "coarsen": s}
            for reg in TARGETS:
                c = counts[reg]
                rec[f"{reg}_iou"] = round(c["tp"] / (c["tp"] + c["fp"] + c["fn"] + 1e-12), 4)
            ious = [rec[f"{r}_iou"] for r in TARGETS]
            rec["macro_iou"] = round(float(np.mean(ious)), 4)
            rec["above_floor_hokkaido"] = bool(rec["hokkaido_iburi_tobu_iou"] > FLOOR["hokkaido_iburi_tobu"])
            out.append(rec)
            print(f"  {kind:<12} seed={seed:<5} s={s:<3} macro={rec['macro_iou']:.4f} "
                  f"hokk={rec['hokkaido_iburi_tobu_iou']:.4f} lomb={rec['lombok_iou']:.4f} "
                  f"palu={rec['palu_iou']:.4f}", flush=True)
        del model
        torch.cuda.empty_cache()

    with open(OUT / "scale_sweep.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w.writeheader(); w.writerows(out)

    print("\n=== seed means ===")
    print(f"{'model':<13}{'s':>3}{'macro':>9}{'Hokkaido':>10}{'Lombok':>9}{'Palu':>8}")
    for kind in ("source-only", "pooled"):
        for s in SCALES:
            sel = [r for r in out if r["model"] == kind and r["coarsen"] == s]
            if not sel:
                continue
            m = np.mean([r["macro_iou"] for r in sel])
            h = np.mean([r["hokkaido_iburi_tobu_iou"] for r in sel])
            l = np.mean([r["lombok_iou"] for r in sel])
            p = np.mean([r["palu_iou"] for r in sel])
            print(f"{kind:<13}{s:>3}{m:>9.4f}{h:>10.4f}{l:>9.4f}{p:>8.4f}")


if __name__ == "__main__":
    main()
