"""Equal-frequency (15-bin) calibration diagnostics + the original high-confidence error rate.

Local analysis copy. Reads the same checkpoints and manifests as
scripts/evaluate_confidence_calibration.py but reports the binning rule fixed in
Supplementary Note S1 (15 equal-frequency bins) alongside the original
equal-width bins.
"""
from __future__ import annotations
import argparse, csv, json, sys
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader

PROJECT = Path(r"D:\landslide_unet_project")
sys.path.insert(0, str(PROJECT))
sys.path.insert(0, str(PROJECT / "scripts"))
from src.datasets import build_dataset
from src.models import build_model
from evaluate_external_benchmark import ManifestDataset

REGIONS = ["hokkaido_iburi_tobu", "lombok", "palu"]
HIGH_CONF = 0.90
N_FREQ_BINS = 15
N_WIDTH_BINS = 15


def collect(model, loader, device, amp):
    model.eval()
    probs, targets = [], []
    with torch.inference_mode():
        for image, mask, _ in loader:
            image = image.to(device, non_blocking=True)
            with torch.amp.autocast("cuda", dtype=torch.bfloat16, enabled=amp and device.type == "cuda"):
                p = torch.sigmoid(model(image).float()).cpu().numpy()[:, 0]
            probs.append(p.reshape(-1).astype(np.float32))
            targets.append((mask.numpy()[:, 0] >= 0.5).reshape(-1))
    return np.concatenate(probs), np.concatenate(targets)


def summarise(probs, targets):
    confidence = np.maximum(probs, 1.0 - probs)
    predicted = probs >= 0.5
    errors = predicted != targets
    n = confidence.size

    high = confidence >= HIGH_CONF
    out = {
        "pixels": int(n),
        "error_rate": float(errors.mean()),
        "mean_confidence": float(confidence.mean()),
        "positive_rate": float(predicted.mean()),
        "high_confidence_pixels": int(high.sum()),
        "high_confidence_fraction": float(high.mean()),
        "high_confidence_error_rate": float(errors[high].mean()) if high.any() else 0.0,
    }

    order = np.argsort(confidence, kind="stable")
    cs, ce = confidence[order], errors[order]
    freq_bins = []
    for idx in np.array_split(np.arange(n), N_FREQ_BINS):
        if idx.size == 0:
            continue
        freq_bins.append({
            "pixels": int(idx.size),
            "pixel_fraction": float(idx.size / n),
            "mean_confidence": float(cs[idx].mean()),
            "error_rate": float(ce[idx].mean()),
            "lower": float(cs[idx].min()),
            "upper": float(cs[idx].max()),
        })
    out["bins_equal_freq"] = freq_bins
    out["ece_equal_freq_15"] = float(sum(b["pixel_fraction"] * abs((1.0 - b["error_rate"]) - b["mean_confidence"]) for b in freq_bins))

    edges = np.linspace(0.5, 1.0, N_WIDTH_BINS + 1)
    width_bins = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (confidence >= lo) & (confidence < hi if hi < 1.0 else confidence <= hi)
        if not m.any():
            continue
        width_bins.append({
            "lower": float(lo), "upper": float(hi),
            "pixels": int(m.sum()), "pixel_fraction": float(m.mean()),
            "mean_confidence": float(confidence[m].mean()),
            "error_rate": float(errors[m].mean()),
        })
    out["bins_equal_width"] = width_bins
    out["ece_equal_width_15"] = float(sum(b["pixel_fraction"] * abs((1.0 - b["error_rate"]) - b["mean_confidence"]) for b in width_bins))
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--arch", required=True)
    parser.add_argument("--arm", required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--input-size", type=int, default=128)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--num-workers", type=int, default=4)
    parser.add_argument("--amp", action="store_true")
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    ckpt = torch.load(args.checkpoint, map_location=device, weights_only=False)
    model = build_model(args.model).to(device)
    model.load_state_dict(ckpt.get("state_dict", ckpt))

    source = build_dataset(str(PROJECT / "repos" / "AS-UNet" / "inputs" / "data_sum_moxizhen+bijie"),
                           "val", args.input_size, train=False)
    results = {}
    loader = DataLoader(source, batch_size=args.batch_size, shuffle=False, num_workers=args.num_workers, pin_memory=True)
    results["source_val"] = summarise(*collect(model, loader, device, args.amp))

    rows = list(csv.DictReader((PROJECT / "data" / "processed" / "benchmark_v2_regions_512" / "manifest_benchmark_v2.csv").open(encoding="utf-8-sig")))
    for region in REGIONS:
        region_rows = [r for r in rows if r["region"] == region]
        loader = DataLoader(ManifestDataset(region_rows, args.input_size), batch_size=args.batch_size,
                            shuffle=False, num_workers=args.num_workers, pin_memory=True)
        results[region] = summarise(*collect(model, loader, device, args.amp))

    payload = {"run_id": args.run_id, "arch": args.arch, "arm": args.arm, "seed": args.seed,
               "model": args.model, "checkpoint": args.checkpoint,
               "high_confidence_threshold": HIGH_CONF, "domains": results}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if not kk.startswith("bins")} for k, v in results.items()}, indent=2))


if __name__ == "__main__":
    main()