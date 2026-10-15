"""Driver for the equal-frequency calibration sweep (E2, reliability + ECE).

Runs scripts/calibration_equal_frequency.py for every packaged matched-exposure
checkpoint and stores one JSON per run under metrics/calibration_e2/.

Usage
-----
python scripts/e2_frequency_bin_sweep.py \
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
    script = Path(__file__).resolve().parent / "calibration_equal_frequency.py"

    index = []
    for key, model in MODELS.items():
        for arm in ARMS:
            for seed in SEEDS:
                run_id = f"q2_x3_{key}_{arm}_seed{seed}"
                record = {"run_id": run_id, "arch": key, "model": model, "arm": arm, "seed": seed,
                          "checkpoint": str(project / "outputs" / run_id / "final_model.pth"),
                          "output": str(output_dir / f"{run_id}.freqcalib.json")}
                if not Path(record["checkpoint"]).exists():
                    record["status"] = "missing_checkpoint"
                elif Path(record["output"]).exists():
                    record["status"] = "already_done"
                else:
                    record["status"] = "pending"
                index.append(record)

    for record in index:
        if record["status"] != "pending":
            print(record["status"], record["run_id"], flush=True)
            continue
        started = time.time()
        command = [args.python, str(script), "--checkpoint", record["checkpoint"], "--model", record["model"],
                   "--run-id", record["run_id"], "--arch", record["arch"], "--arm", record["arm"],
                   "--seed", str(record["seed"]), "--output", record["output"],
                   "--batch-size", str(args.batch_size), "--num-workers", str(args.num_workers), "--amp"]
        completed = subprocess.run(command, capture_output=True, text=True)
        record["seconds"] = round(time.time() - started, 1)
        record["status"] = "ok" if completed.returncode == 0 else "failed"
        if completed.returncode != 0:
            record["stderr_tail"] = (completed.stderr or "")[-500:]
        print(f"{record['status']:6s} {record['run_id']} {record.get('seconds')}s", flush=True)

    (output_dir / "e2_freq_run_index.json").write_text(json.dumps(index, indent=2), encoding="utf-8")
    print("E2_FREQ_DONE", flush=True)


if __name__ == "__main__":
    main()
