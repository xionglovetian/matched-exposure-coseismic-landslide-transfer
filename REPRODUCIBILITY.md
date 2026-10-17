# Reproducibility Guide

## 1. Reference environment

- OS used for the experiments: Windows 11
- Python: 3.10.21
- CUDA runtime: 12.6
- PyTorch: 2.14.0+cu126
- GPU used for the reported runs: NVIDIA GeForce RTX 4060 Laptop GPU, 8 GB

`environment-full.txt` is the original environment export. `requirements.txt`
is a reduced pinned set for the benchmark code.

## 2. Path configuration

The scripts use `LANDSLIDE_PROJECT_ROOT` and default to the repository root.

```powershell
$env:LANDSLIDE_PROJECT_ROOT = (Get-Location).Path
$env:LANDSLIDE_PYTHON = (Get-Command python).Source
```

The reference data layout is:

```text
$LANDSLIDE_PROJECT_ROOT/
  repos/AS-UNet/inputs/data_sum_moxizhen+bijie/
  data/processed/benchmark_v2_regions_512/
  data/processed/external_regions_512/
  data/processed/fewshot_target_splits/
  outputs/
  reports/
  logs/
```

The image data are not included. Place licensed data at the layout above or set
`LANDSLIDE_PROJECT_ROOT` to an existing local experiment root.

The packaged manifest paths point to the original workstation. Rebase a copy
without modifying the frozen source CSV:

```powershell
python scripts/checks/rebase_manifest_paths.py `
  --input data_manifests/manifest_benchmark_v2.csv `
  --output data/processed/benchmark_v2_regions_512/manifest_benchmark_v2.csv `
  --old-root "D:/landslide_unet_project" `
  --new-root $env:LANDSLIDE_PROJECT_ROOT
```

Use the same command for `manifest_external.csv` and the few-shot split CSVs.

## 3. Package checks

```powershell
python scripts/checks/validate_release.py
python scripts/checks/verify_manifest.py
python scripts/checks/check_environment.py
```

`validate_release.py` checks manifest counts, required metric files, reported
numerical anchors, and the absence of raw imagery/checkpoints.
`verify_manifest.py` verifies SHA-256 hashes for every file listed in
`MANIFEST_SHA256.csv`.

## 4. Metric-level reproduction

This level requires no imagery or checkpoint files.

- X2 augmentation selection:
  `metrics/q2_x2_augmentation/`
- X1 resolution three-arm results:
  `metrics/q2_x1_resolution_raw/`,
  `metrics/q2_x1_a1c_raw/`,
  `metrics/q2_x1_128ref_eval_raw/`, and
  `metrics/q2_x1_summary/`
- X3 matched-exposure and spatial bootstrap:
  `metrics/q2_x3_raw/`, `metrics/q2_x3_tiles/`, and
  `metrics/q2_x3_bootstrap/`
- Six-region LORO extension:
  `metrics/q2_x3_loro_tiles/` and `metrics/q2_x3_loro_bootstrap/`
- Route 1 frozen contrast and calibration outputs:
  `metrics/route1_recomputed/` and `metrics/route1_bootstrap/`

The packaged CSVs and JSON files are the frozen inputs for the numerical claims
in the accompanying manuscript.

## 5. Model-level workflow

After obtaining licensed data and materializing the expected layout:

1. Inspect available arguments:
   `python scripts/train_unified.py --help`
   `python scripts/train_exposure_matched.py --help`
   `python scripts/evaluate_q2_checkpoint.py --help`
   `python scripts/q2_x3_spatial_bootstrap.py --help`
2. Run X2 first, because `none` was selected before target evaluation:
   `powershell -ExecutionPolicy Bypass -File scripts/run_q2_x2_augmentation.ps1`
3. Run X1 resolution arms:
   `powershell -ExecutionPolicy Bypass -File scripts/run_q2_x1_resolution.ps1`
4. Run the two-architecture X3 source-expansion experiment:
   one invocation per architecture using
   `scripts/run_q2_x3_resunet.ps1` or the corresponding Bottleneck queue.
5. Run tile-level evaluation and the component bootstrap:
   `python scripts/evaluate_q2_tile_metrics.py --help`
   `python scripts/q2_x3_spatial_bootstrap.py --help`
6. Run the exploratory six-region LORO extension only after preserving the
   primary three-region contrast.

All queue scripts are restartable: they skip completed runs unless `-Force` is
specified.

## 6. Numerical anchors

The release validator checks these anchors:

| Object | Anchor |
|---|---:|
| X2 `none-current` source-validation IoU delta | `+0.0431505334` |
| X3 ResUNet target-macro IoU delta | `+0.0772718654` |
| X3 Bottleneck target-macro IoU delta | `+0.0455875690` |
| X1 ResUNet retrained-256 minus 128 target IoU | `-0.0243143426` |
| X1 SegFormer-B0 retrained-256 minus 128 target IoU | `+0.0028660398` |

## 7. Evidence boundaries

The package supports a retrospective benchmark over positive image chips. It
does not establish prospective next-event performance, complete-map
false-positive area, operational readiness, spatially independent source
splitting, or independently annotated target validation. Those boundaries are
retained in the selected reports and must remain in downstream claims.

## 8. Verification status

One complete model-level Gate-D anchor was rerun from the published code:
X3 ResUNet pooled seed 42. The rerun reproduced the source-validation metrics
and 2,737-row target-tile CSV bitwise, and the learned checkpoint tensors were
identical (278 tensors, 24,455,423 elements, zero differences). See
`reports/verification/GATE_D_X3_RESUNET_SEED42.md`.

The other long-running queues are fully specified by pinned inputs,
configuration snapshots, and executable queue scripts, but they are not
represented as independently rerun in this repository until a clean-machine
execution of `FULL_REPRODUCTION.md` completes. Full reproduction requires the
licensed CAS data and approximately 20 GiB of Q2 checkpoints or the compute
time needed to regenerate them.

## 9. Revision-phase experiments (2026-10-15)

Everything below is regenerated from packaged files only; no imagery and no
checkpoints are needed.

```powershell
python scripts/q2_x3_seed_stratified_reanalysis.py `
  --tile-root metrics/q2_x3_tiles `
  --spatial-index data_manifests/target_spatial_index.csv `
  --output-dir metrics/q2_x3_seed_stratified_bootstrap --draws 10000

python scripts/q2_x3_target_macro_component_bootstrap.py `
  --tile-root metrics/q2_x3_tiles `
  --spatial-index data_manifests/target_spatial_index.csv `
  --output metrics/q2_x3_bootstrap/x3_target_macro_component.csv --draws 10000

python scripts/report_e3_four_backbone.py
python scripts/report_e2_calibration.py
python scripts/report_e2_frequency_bins.py
python scripts/e1_partial_background_false_alarm.py
```

Both bootstrap scripts are deterministic. Rerunning them reproduces the
committed CSVs byte for byte, and the report generators reproduce the Markdown
summaries under `reports/revision_20261015/` exactly. This was verified against
the committed files before this release.

The revision phase adds eighteen trained runs:

```bash
LANDSLIDE_ROOT=/path/to/landslide_unet_project ./scripts/run_e3_four_backbone_queue.sh all
```

The queue is restartable and skips completed runs. It needs the same licensed
data as `FULL_REPRODUCTION.md`. Six runs are source-only source-domain
initialisations for SegFormer-B0 and DeepLabV3+; twelve are matched-exposure
contrast runs for those two backbones.

### Environment equivalence

The eighteen runs were produced on a rented CUDA host with an independently
built virtual environment (see `scripts/setup/setup_e3_cloud_env.sh`). Before
the queue was launched, ResUNet / pooled / seed 42 was retrained end to end for
all 1,120 steps on that host and compared against the local record. The four
logged checkpoints matched bitwise on `train_loss`, `lr`, `source_val_iou` and
`source_val_dice`, with terminal source-validation IoU `0.518395166665147`. That
check is what licenses treating the new runs as directly comparable to the
eighteen original ones.

### Model-level prerequisites for E2

The calibration sweeps re-evaluate the packaged checkpoints:

```powershell
python scripts/e2_high_confidence_error_sweep.py --project-root $env:LANDSLIDE_PROJECT_ROOT
python scripts/e2_frequency_bin_sweep.py --project-root $env:LANDSLIDE_PROJECT_ROOT
```

Both write into `metrics/calibration_e2/`. They require the matched-exposure
checkpoints, that is, either the weights or the compute needed to retrain them.

### Known gap

`reports/requirements-lock.txt` of the original experiment root did not pin
`segmentation-models-pytorch` or `opencv-python`. The repository-level
`requirements.txt` does pin both (`segmentation-models-pytorch==0.5.0`,
`opencv-python-headless==5.0.0.93`), so use `requirements.txt` for a clean
environment.

## 10. Scale negative controls (2026-10-17)

Two controls answer the objection that the region effect is a resolution
asymmetry between the source and target domains. Unlike Section 9 these need
imagery and training, so only their outputs are regenerated from the package.

### Source-domain coarsening

The pooled source domain is resampled to a common effective ground sampling
distance before tiling, at k = 1, 4 and 16 relative to the native chips:

```powershell
python scripts/scale_experiments/coarsen_source.py --k 4
python scripts/scale_experiments/cache_input_128.py --k 4
python scripts/scale_experiments/train_coarsened_sources.py --k 4
python scripts/scale_experiments/evaluate_source_coarsening.py
```

### Evaluation-scale sweep

The held-out chip resolution is varied at s = 1, 2, 4, 8 and 16 for both model
families:

```powershell
python scripts/scale_experiments/evaluate_scale_sweep.py
```

Results land in `metrics/scale_experiments/source_coarsening.csv` (nine runs)
and `metrics/scale_experiments/evaluation_scale_sweep.csv` (thirty runs). Both
controls reduce macro IoU monotonically as the mismatch grows; the sweep also
shows that only Lombok gains at s = 2. Neither changes the sign or the ranking
of the region effect reported in the manuscript.
