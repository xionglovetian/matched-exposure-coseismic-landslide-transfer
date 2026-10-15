"""Regenerate the revision-phase summary table for the equal-frequency calibration diagnostics.

Reads packaged machine-readable metrics under the repository root and writes the
Markdown summary shipped in reports/revision_20261015/.

Usage
-----
python scripts/report_e2_frequency_bins.py [--repo-root .] [--output reports/revision_20261015/E2_calibration_frequency_bins.md]
"""
from __future__ import annotations

import argparse
import json
import os as _repo_os

from pathlib import Path


DOMAINS = [("source_val", "CAS source validation"), ("hokkaido_iburi_tobu", "Hokkaido Iburi-Tobu"),
           ("lombok", "Lombok"), ("palu", "Palu")]
ARCHITECTURES = {"resunet": "ResUNet", "bottleneckliteask": "Bottleneck-LiteASK"}
ARMS = ["pooled", "cas-multistream"]
SEEDS = [42, 2026, 777]
T_CRITICAL_95_DF2 = 4.302652729911275


def t_interval(values: list[float]) -> tuple[float, float, float, float]:
    n = len(values)
    mean = sum(values) / n
    sd = (sum((value - mean) ** 2 for value in values) / (n - 1)) ** 0.5
    se = sd / n ** 0.5
    return mean, sd, mean - T_CRITICAL_95_DF2 * se, mean + T_CRITICAL_95_DF2 * se


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=str(_repo_os.environ.get("LANDSLIDE_PROJECT_ROOT", Path(__file__).resolve().parents[1])))
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    project = Path(args.repo_root).resolve()
    source = project / "metrics" / "calibration_e2"

    lines = ["# E2 (frequency-bin variant): reliability and ECE", "",
             "Equal-frequency 15 bins, as fixed in Supplementary Note S1. ECE = sum over bins of (bin pixel share) x |accuracy - mean confidence|.",
             "High-confidence error rate (confidence >= 0.90) recomputed here as a consistency check against the original implementation.", "",
             "| Backbone | Arm | Domain | ECE mean | ECE 95% CI | High-conf error mean (%) | High-conf error 95% CI (%) |",
             "|---|---|---|---:|---|---:|---|"]
    for key, label in ARCHITECTURES.items():
        for arm in ARMS:
            for domain, domain_label in DOMAINS:
                eces, high_conf = [], []
                for seed in SEEDS:
                    payload = json.loads((source / f"q2_x3_{key}_{arm}_seed{seed}.freqcalib.json").read_text(encoding="utf-8"))
                    cell = payload["domains"][domain]
                    eces.append(cell["ece_equal_freq_15"])
                    high_conf.append(cell["high_confidence_error_rate"] * 100.0)
                ece_mean, _, ece_low, ece_high = t_interval(eces)
                hc_mean, _, hc_low, hc_high = t_interval(high_conf)
                lines.append(f"| {label} | {arm} | {domain_label} | {ece_mean:.4f} | [{ece_low:+.4f}, {ece_high:+.4f}] "
                             f"| {hc_mean:.2f} | [{hc_low:+.2f}, {hc_high:+.2f}] |")
    lines.append("")

    output = Path(args.output) if args.output else project / "reports" / "revision_20261015" / "E2_calibration_frequency_bins.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
