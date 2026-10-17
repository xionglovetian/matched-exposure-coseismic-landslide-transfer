# -*- coding: utf-8 -*-
"""Train the scale-coarsened source models (ResUNet, 50 epochs, no augmentation),
matching the configuration of the existing q2_x2_aug_none_* checkpoints exactly."""

import subprocess
import sys
import time
from pathlib import Path

PY = r"D:\landslide_unet_project\venv\Scripts\python.exe"
SCRIPT = r"D:\landslide_unet_project\scripts\train_unified.py"
BASE = Path(r"D:\landslide_unet_project\repos\AS-UNet\inputs")
OUT = Path(r"D:\landslide_unet_project\outputs")

RUNS = []
for k in (4, 16):
    for seed in (42, 2026, 777):
        RUNS.append({
            "k": k, "seed": seed,
            "train_root": str(BASE / f"data_sum_moxizhen+bijie_k{k}_128"),
            "output_dir": str(OUT / f"q2_sm_k{k}_resunet_seed{seed}"),
        })


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    t0 = time.time()
    for i, r in enumerate(RUNS, 1):
        tag = f"q2_sm_k{r['k']}_resunet_seed{r['seed']}"
        if only and only != tag:
            continue
        done = Path(r["output_dir"]) / "best_model.pth"
        if done.exists():
            print(f"[{i}/{len(RUNS)}] SKIP {tag} (exists)", flush=True)
            continue
        cmd = [
            PY, SCRIPT,
            "--model", "ResUNet",
            "--loss", "PolyGHMDiceLoss",
            "--train-root", r["train_root"],
            "--output-dir", r["output_dir"],
            "--epochs", "50",
            "--batch-size", "32",
            "--input-size", "128",
            "--lr", "0.0001",
            "--weight-decay", "0.0001",
            "--num-workers", "0",
            "--seed", str(r["seed"]),
            "--val-interval", "5",
            "--grad-accum-steps", "1",
            "--checkpoint-interval", "0",
            "--amp",
            "--skip-external-eval",
            "--train-fraction", "1.0",
            "--subset-seed", str(r["seed"]),
            "--augmentation", "none",
        ]
        print(f"[{i}/{len(RUNS)}] START {tag}  ({time.time()-t0:.0f}s elapsed)", flush=True)
        st = time.time()
        p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if p.returncode != 0:
            print(f"    FAILED rc={p.returncode}")
            print((p.stderr or "")[-2000:])
            continue
        tail = [ln for ln in (p.stdout or "").strip().splitlines() if ln.strip()][-3:]
        for ln in tail:
            print("    " + ln)
        print(f"    took {time.time()-st:.0f}s", flush=True)
    print(f"ALL DONE in {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
