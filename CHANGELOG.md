# Changelog

## 2026-10-17 - scale negative controls

Added the two negative controls that the revision asks about, so that they are
resolvable from the archived tag rather than only from local runs.

- Source-domain coarsening. The pooled source domain was resampled to a common
  effective ground sampling distance before tiling, at k = 1, 4 and 16 relative
  to the native chips. Nine runs (three k values x three seeds) under
  `scripts/scale_experiments/`, results in
  `metrics/scale_experiments/source_coarsening.csv`.
- Evaluation-scale sweep. The held-out chip resolution was varied at
  s = 1, 2, 4, 8 and 16 for both model families. Thirty runs, results in
  `metrics/scale_experiments/evaluation_scale_sweep.csv`.
- Both controls move macro IoU monotonically downward as the mismatch grows, and
  neither rescues the region effect; they are archived as evidence that the
  headline contrast is not an artefact of a resolution asymmetry between source
  and target domains.
- `metrics/README.md` now indexes `scale_experiments/`, `e3_four_backbone_raw/`
  and `calibration_e2/`.
- `.zenodo.json` now self-references this repository (it previously named the
  retired two-architecture repository) and its description covers the scale
  controls.

## 2026-10-15 - four-backbone revision release

Repository published as
`matched-exposure-coseismic-landslide-transfer`, superseding
`coseismic-landslide-transfer-benchmark`. The earlier two-architecture history
is preserved as ordinary Git history, so that snapshot stays resolvable at
commit `7b143df` and tag `repro-20260929-r6`.

Added:

- Four-backbone matched-exposure contrast. The seed-stratified reanalysis and
  the target-macro component bootstrap now cover ResUNet, Bottleneck-LiteASK,
  SegFormer-B0 and DeepLabV3+; the two original architectures reproduce their
  previous values exactly.
- Eighteen new runs: six source-only source-domain initialisations for the two
  new backbones and twelve matched-exposure contrast runs. Their
  `config.json`/`history.csv` are archived under `configs/records/`, their
  training metrics under `metrics/e3_four_backbone_raw/`, and their run logs
  under `logs/e3_runs/`.
- `configs/RUN_INDEX.csv` and `CHECKPOINT_INDEX.csv` extended with the eighteen
  runs.
- Multi-seed calibration diagnostics under `metrics/calibration_e2/`, plus
  `metrics/figure8_source_data/` for the calibration figure.
- Tile-level background false-alarm diagnostic:
  `metrics/e1_partial_background_false_alarm.csv`.
- Revision-phase reports under `reports/revision_20261015/`: the frozen
  pre-registration (Supplementary Note S1), the E3, E2 and E1 results, and an
  index that records the deviations actually taken.
- Analysis code for the above: `scripts/q2_x3_target_macro_component_bootstrap.py`,
  `scripts/e1_partial_background_false_alarm.py`,
  `scripts/e2_high_confidence_error_sweep.py`,
  `scripts/e2_frequency_bin_sweep.py`, the three `scripts/report_*.py`
  generators, `scripts/run_e3_four_backbone_queue.sh` and
  `scripts/setup/setup_e3_cloud_env.sh`.
- `CITATION.cff` and `.zenodo.json` so that a tagged release can be archived
  with a DOI.
- Correction to `README.md`, `PROVENANCE.md` and this changelog so that the
  superseded Route 1 numbers and the two-architecture interval snapshots are
  labelled as historical.

Changed:

- `metrics/q2_x3_seed_stratified_bootstrap/q2_x3_seed_stratified_t_interval.csv`,
  `q2_x3_seed_stratified_bootstrap.csv`, `q2_x3_seed_level_macro_effects.csv`
  and `summary_t_interval.md` were replaced by their four-backbone supersets.
  The two original architectures enter unchanged; the added rows carry the two
  new backbones and are bitwise reproducible with
  `scripts/q2_x3_seed_stratified_reanalysis.py`.
- `scripts/q2_x3_seed_stratified_reanalysis.py` and
  `scripts/q2_x3_spatial_bootstrap.py` now cover all four architectures and
  resolve paths from `LANDSLIDE_PROJECT_ROOT`, matching the rest of `scripts/`.
- `.gitignore` no longer excludes `logs/e3_runs/`, because the curated run logs
  of the revision-phase experiment are part of the evidence package.
- `MANIFEST_SHA256.csv` rebuilt over the new file set.

Fixed:

- `validate_release.py` anchors still pass: the four-backbone interval file
  keeps the two original architectures to within 1e-9 of the recorded values.

Not included:

- Model weights. `CHECKPOINT_INDEX.csv` records every run and its checkpoint
  sizes, but the binaries stay out of Git. For the eighteen revision-phase runs
  the archived weights are `final_model.pth` for the contrast runs and
  `best_model.pth` for the six source-only initialisation runs; intermediate
  step checkpoints were not retained.
- Per-sample training rows (`train_rows.csv`, `val_rows.csv`) of the new runs.

## 2026-09-28 - initial reproducibility package

- Published benchmark source, queue scripts, frozen manifests/splits,
  machine-readable metrics, and selected audit reports.
- Added portable `LANDSLIDE_PROJECT_ROOT` and `LANDSLIDE_PYTHON` handling to the
  Python and PowerShell entry points.
- Added repository, environment, metric-anchor, manifest-count and SHA-256
  validation utilities.
- Excluded manuscript files, raw imagery, processed chips, checkpoints and
  unrelated interim artifacts.
