"""Driver for the multi-seed high-confidence error sweep (E2, main endpoint).

Evaluates every packaged matched-exposure checkpoint with
scripts/evaluate_confidence_calibration.py and stores one JSON per
architecture x arm x seed under metrics/calibration_e2/.

Usage
-----
python scripts/e2_high_confidence_error_sweep.py \
    --project-root /path/to/landslide_unet_project \
    --python /path/to/python
"""
from __future__ import annotations

import argparse
import json
import os as _repo_os
import subprocess
import sys
import time
from pathlib import Path

MODELS = {"resunet": "ResUNet", "bottleneckliteask": "BottleneckLiteASKUNetPlusPlus"}
ARMS = ["pooled", "cas-multistream"]
SEEDS = [42, 2026, 777]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=_repo_os.environ.get("LANDSLIDE_PROJECT_ROOT", "."))
    parser.add_argument("--python", default=_repo_os.environ.get("LANDSLIDE_PYTHON", sys.executable))
    parser.add_argument("--output-dir", default="metrics/calibration_e2")
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--num-workers", type=int, default=4)
    args = parser.parse_args()

    project = Path(args.project_root).resolve()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    script = project / "scripts" / "evaluate_confidence_calibration.py"

    index = []
    for key, model_name in MODELS.items():
        for arm in ARMS:
            for seed in SEEDS:
                checkpoint = project / "outputs" / f"q2_x3_{key}_{arm}_seed{seed}" / "final_model.pth"
                out = output_dir / f"e2__{key}__{arm}__seed{seed}.json"
                record = {"arch": key, "model": model_name, "arm": arm, "seed": seed,
                          "checkpoint": str(checkpoint), "output": str(out),
                          "checkpoint_exists": checkpoint.exists(), "status": "pending"}
                if not checkpoint.exists():
                    record["status"] = "missing_checkpoint"
                elif out.exists():
                    record["status"] = "already_done"
                index.append(record)

    todo = [record for record in index if record["status"] == "pending"]
    print(f"total={len(index)} todo={len(todo)}", flush=True)
    for record in todo:
        started = time.time()
        command = [args.python, str(script), "--checkpoint", record["checkpoint"], "--model", record["model"],
                   "--batch-size", str(args.batch_size), "--num-workers", str(args.num_workers), "--amp",
                   "--output", record["output"]]
        completed = subprocess.run(command, capture_output=True, text=True)
        record["seconds"] = round(time.time() - started, 1)
        record["status"] = "ok" if completed.returncode == 0 else "failed"
        if completed.returncode != 0:
            record["stderr_tail"] = (completed.stderr or "")[-500:]
        print(f"{record['status']:6s} {record['arch']}/{record['arm']}/seed{record['seed']} {record.get('seconds')}s", flush=True)

    (output_dir / "e2_run_index.json").write_text(json.dumps(index, indent=2), encoding="utf-8")
    print("E2_DONE", flush=True)


if __name__ == "__main__":
    main()
