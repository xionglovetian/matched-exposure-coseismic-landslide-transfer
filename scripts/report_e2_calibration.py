"""Regenerate the revision-phase summary table for the multi-seed high-confidence error sweep.

Reads packaged machine-readable metrics under the repository root and writes the
Markdown summary shipped in reports/revision_20261015/.

Usage
-----
python scripts/report_e2_calibration.py [--repo-root .] [--output reports/revision_20261015/E2_calibration_multiseed.md]
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

    lines = ["# E2 result: calibration diagnostics across 3 seeds x 2 architectures", "",
             "Endpoint: error rate among pixel predictions with confidence >= 0.90 (same convention as the existing single-seed report).",
             "Domains: CAS source validation plus the three fixed target regions. Arms: pooled source and CAS replay control.",
             "Interval: seed-stratified Student t across the three training seeds (df = 2).", ""]

    per_arch: dict = {}
    for key, label in ARCHITECTURES.items():
        per_arch[label] = {}
        for arm in ARMS:
            lines.append("## " + label + " / " + arm)
            lines.append("")
            lines.append("| Domain | Seeds 42 / 2026 / 777 (%) | Mean (%) | SD | 95% CI (%) |")
            lines.append("|---|---|---:|---:|---|")
            for domain, domain_label in DOMAINS:
                values = []
                for seed in SEEDS:
                    payload = json.loads((source / f"e2__{key}__{arm}__seed{seed}.json").read_text(encoding="utf-8"))
                    values.append(payload[domain]["high_confidence_error_rate"] * 100.0)
                mean, sd, low, high = t_interval(values)
                per_arch[label][(arm, domain)] = {"vals": values, "mean": mean, "sd": sd, "lo": low, "hi": high}
                lines.append("| " + domain_label + " | " + " / ".join(f"{value:.2f}" for value in values)
                             + f" | {mean:.2f} | {sd:.2f} | [{low:+.2f}, {high:+.2f}] |")
            lines.append("")

    lines += ["## Pre-registered E2 decision", ""]
    verdicts = []
    for label in ARCHITECTURES.values():
        for arm in ARMS:
            source_cell = per_arch[label][(arm, "source_val")]
            direction_ok = all(source_cell["vals"][i] < per_arch[label][(arm, domain)]["vals"][i]
                               for domain in ("hokkaido_iburi_tobu", "lombok", "palu") for i in range(3))
            overlap = [domain for domain in ("hokkaido_iburi_tobu", "lombok", "palu")
                       if not (source_cell["hi"] < per_arch[label][(arm, domain)]["lo"])]
            verdicts.append((label, arm, direction_ok, overlap))
            lines.append(f"- {label} / {arm}: direction (source < all three targets for every seed) = {direction_ok}; "
                         f"source interval strictly below target intervals for = "
                         f"{'all three target regions' if not overlap else 'no (' + ', '.join(overlap) + ' overlap)'} "
                         f"(source mean {source_cell['mean']:.2f}% vs Hokkaido {per_arch[label][(arm,'hokkaido_iburi_tobu')]['mean']:.2f}%, "
                         f"Lombok {per_arch[label][(arm,'lombok')]['mean']:.2f}%, Palu {per_arch[label][(arm,'palu')]['mean']:.2f}%)")

    all_direction = all(row[2] for row in verdicts)
    all_separated = all(not row[3] for row in verdicts)
    lines += ["",
              f"- Every one of the 3 seeds x 2 architectures x 2 arms combinations shows a lower source-domain high-confidence error rate than each target region: **{all_direction}**.",
              f"- Source-domain interval strictly below all three target-region intervals in every combination: **{all_separated}**.",
              "- Pre-registered rule (direction holds for all 3 seeds x 2 architectures and intervals do not overlap): **"
              + ("PASS" if (all_direction and all_separated) else ("PARTIAL" if all_direction else "FAIL")) + "**."]

    output = Path(args.output) if args.output else project / "reports" / "revision_20261015" / "E2_calibration_multiseed.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
