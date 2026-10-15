# Matched-Exposure Coseismic Landslide Transfer

Reproducibility package for the manuscript

> **Region-dependent transferability of coseismic landslide mapping models between
> earthquakes: a matched-exposure assessment for rapid post-earthquake inventorying**
> (target journal: *Geomatics, Natural Hazards and Risk*)

The study is a retrospective, region-held-out benchmark of coseismic landslide
segmentation under cross-event domain shift. It asks whether the same model,
retrained with the same optimisation exposure, transfers equally well to a new
earthquake, and whether pooling several source inventories helps.

This repository contains the experiment code, frozen manifests and splits,
machine-readable metrics, the revision-phase statistical analyses, and the
audit/protocol reports. It does **not** contain the manuscript, the source or
target imagery, processed chips, model weights, or anything restricted by the
original data licences.

This repository supersedes `coseismic-landslide-transfer-benchmark`, which holds
the earlier two-architecture snapshot. The full two-architecture history is
preserved here as ordinary Git history, so that snapshot is still resolvable at
commit `7b143df`.

## Headline claims and where the numbers live

| Claim in the manuscript | Authoritative packaged file |
|---|---|
| Pooling raised MCC in all four backbones | `metrics/q2_x3_seed_stratified_bootstrap/q2_x3_seed_stratified_t_interval.csv` and `metrics/q2_x3_bootstrap/x3_target_macro_component.csv` |
| Macro IoU improved in three of the four backbones | same two files, `iou` rows |
| Per-seed effects behind both endpoints | `metrics/q2_x3_seed_stratified_bootstrap/q2_x3_seed_level_macro_effects.csv` |
| Region-level source-expansion contrast | `reports/selected/e1_exposure_matched_contrasts.csv` |
| Source-domain validation did not predict new-event performance | `reports/selected/benchmark_v2_zero_shot_region_summary.csv` |
| High-confidence error under the source-only configuration | `metrics/calibration_e2/e2__*__*.json` |
| Reliability and ECE (equal-frequency 15 bins) | `metrics/calibration_e2/q2_x3_*.freqcalib.json` |
| Resolution gain is a weight-scale artefact | `metrics/q2_x1_summary/grouped.csv` |
| Calibration figure source data | `metrics/figure8_source_data/` |

`PROVENANCE.md` maps every manuscript-level number to its packaged source and
records which files are superseded.

## Which number is authoritative

The headline exposure-matched macro IoU effect is the q2_x3 fixed-three-region
value with the seed-stratified interval taking precedence for architecture-level
inference (`+0.0773` for ResUNet, interval `[+0.0514, +0.1031]`). The value
`+0.0355` in `metrics/route1_bootstrap/route1_e1_tile_bootstrap.csv` is a
historical tile-level bootstrap variant and is **not** the manuscript headline.
Files with `fig4` in their name are plotting inputs and may lag the manuscript
tables. The current authoritative sources are
`reports/selected/e1_exposure_matched_contrasts.csv` and
`metrics/q2_x3_seed_stratified_bootstrap/q2_x3_seed_stratified_t_interval.csv`.

## Revision-phase experiments (2026-10-15)

Three additional experiments were pre-registered before they were run; the plan
is frozen in `reports/revision_20261015/PRE_REGISTRATION_S1.md`.

- **E3 - four-backbone matched-exposure contrast: PASS.** The pre-registered
  rule required the MCC effect to hold in at least three of four backbones. It
  holds in four of four (ResUNet `+0.1573`, Bottleneck-LiteASK `+0.0990`,
  SegFormer-B0 `+0.1047`, DeepLabV3+ `+0.1333`), with both interval families
  excluding zero and all three seeds sharing a sign. The macro IoU effect holds
  in three of four (ResUNet `+0.0773`, SegFormer-B0 `+0.0591`, DeepLabV3+
  `+0.0610`); Bottleneck-LiteASK (`+0.0456`, interval `[-0.0056, +0.0968]`)
  remains the documented exception. Eighteen new runs were added: six
  source-only source-domain initialisations for the two new backbones, and
  twelve matched-exposure contrast runs.
- **E2 - multi-seed calibration diagnostics: the source-only statement holds,
  the pooled statement does not.** Across 3 seeds x 2 architectures x 2 arms,
  the source-only arm shows a lower high-confidence error rate than every target
  region for every seed, with non-overlapping intervals. The pooled arm fails
  the same rule: on Palu the pooled ResUNet rate (`0.83%`) is below its own
  source-domain rate (`0.94%`), and the pooled Bottleneck-LiteASK Hokkaido
  interval crosses zero.
- **E1 - full-tile screening endpoints: blocked, not executed.** The
  pre-registered E1 requires tiles with zero reference foreground. The released
  region archives are already foreground-filtered, so those tiles were never
  distributed. Only a partial pixel-level diagnostic inside positive-containing
  tiles is reported (`reports/revision_20261015/E1_partial_background_false_alarm.md`,
  `metrics/e1_partial_background_false_alarm.csv`); it is not a substitute for
  E1.

## Repository layout

```text
src/                       core datasets, metrics and model definitions
scripts/                   training, evaluation, bootstrap and audit scripts
scripts/checks/            environment, artifact and manifest validators
scripts/setup/             input download and environment setup scripts
configs/records/           archived config.json / history.csv per run
configs/RUN_INDEX.csv      run inventory: config, history, metrics, checkpoints
data_manifests/            frozen manifests, split assignments, spatial index
metrics/                   machine-readable results (raw and summarised)
reports/selected/          frozen protocols, audits and result summaries
reports/revision_20261015/ revision-phase pre-registration, results, logs
logs/e3_runs/              curated run logs for the revision-phase experiment
figures/                   publication figure generators
```

## Quick validation

Python 3.10 is recommended. The release validator uses only the standard
library.

```powershell
git clone https://github.com/xionglovetian/matched-exposure-coseismic-landslide-transfer.git
cd matched-exposure-coseismic-landslide-transfer
python scripts/checks/validate_release.py
python scripts/checks/verify_manifest.py
```

## Recomputing the revision-phase tables from the packaged metrics

These four commands need no imagery and no checkpoints; they read only what is
committed here.

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

Both bootstrap scripts are deterministic: rerunning them reproduces the
committed CSVs byte for byte. The report generators likewise regenerate the
Markdown summaries under `reports/revision_20261015/` exactly.

## Data and checkpoints

The raw image data are not redistributed. Obtain each source from its original
provider and comply with the terms recorded in `DATA_LICENSES.md`; `INPUTS.md`
lists the pinned commits, DOIs and expected counts. The frozen manifests contain
image and mask path fields from the reference workstation, and
`scripts/checks/rebase_manifest_paths.py` rewrites them for a new data root.

Model weights are not stored in this Git repository because they are large
binary artifacts and their release policy depends on the source-data terms.
`CHECKPOINT_INDEX.csv` records which checkpoints each run produced, with sizes
and, where available, hashes. For the eighteen revision-phase runs the archived
weights are the ones the analyses consumed: `final_model.pth` for the contrast
runs and `best_model.pth` for the six source-only initialisation runs.
Intermediate step checkpoints of those runs were not retained. The code can
retrain every packaged configuration, and a checkpoint release should be
archived separately with an explicit licence and a persistent identifier.

## Reproduction status

Two levels of reproduction are supported:

1. **Metric-level reproduction:** rerun every packaged endpoint, interval and
   report from `metrics/` and `data_manifests/` without imagery or checkpoints.
   This is verified for the revision-phase tables, including the component
   bootstrap and the seed-stratified intervals.
2. **Model-level reproduction:** obtain the licensed data, materialise the
   expected layout, retrain or place the corresponding checkpoints, then run the
   evaluation and bootstrap scripts.

The second level is hardware- and data-dependent. One complete Gate-D path was
re-executed from the published code: X3 ResUNet pooled seed 42. It reproduced
the `metrics.json` and the full 2,737-row tile-metric CSV bitwise, and produced
278 identical checkpoint tensors (24,455,423 elements, zero differences); see
`reports/verification/GATE_D_X3_RESUNET_SEED42.md`. The same run was repeated on
an independent cloud host with an independently built environment and matched
the local record bitwise again (terminal source-validation IoU
`0.518395166665147`), which is the environment-equivalence check behind the
four-backbone results. The remaining multi-day queues are executable from the
pinned data and configurations but must still complete on the target machine
before the whole study is called independently reproduced.

## Archiving and DOI

GitHub alone does not mint DOIs. Connect this repository to Zenodo (Settings ->
Webhooks -> Zenodo, enable the repository toggle), publish a GitHub release, and
Zenodo archives that release and issues a DOI. `.zenodo.json` and `CITATION.cff`
are already in place with the metadata that archive needs; only the version DOI
has to be filled in after the release.

## Licence

Code and documentation in this repository are released under the MIT Licence.
Image data and derived annotations remain governed by their original licences;
see `DATA_LICENSES.md`.

## Repository URL

https://github.com/xionglovetian/matched-exposure-coseismic-landslide-transfer
