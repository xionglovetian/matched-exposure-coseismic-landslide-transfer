# Supplementary Note S1 — Pre-registered analysis plan for three additional experiments

**Status:** fixed before running E1/E2/E3; written 2026-10-15 (Asia/Shanghai)
**Object manuscript:** *Region-dependent transferability of coseismic landslide mapping models between earthquakes: a matched-exposure assessment for rapid post-earthquake inventorying*
**Target journal:** Geomatics, Natural Hazards and Risk (Taylor & Francis)
**Purpose:** provide pre-specified evidence for three strong statements retained in the abstract and Key Policy Highlights:
- E1 -> "Pooled-source models can support response-phase screening"
- E2 -> "Confidence is not an out-of-domain alarm"
- E3 -> "cross-architecture"

This note fixes endpoints, units, interval families and pass/fail rules **before** any of the three experiments is run, so that no rule can be chosen after seeing results.

---

## 1. Endpoint definitions

All endpoints are computed from pixel-level confusion counts at a fixed decision threshold of 0.5 (predicted foreground where sigmoid(logit) >= 0.5; reference foreground where mask >= 0.5).

Given pooled counts `tp, fp, fn, tn` (`eps = 1e-12`):

| Endpoint | Definition |
|---|---|
| `iou` (foreground IoU, reported as macro IoU) | `tp / (tp + fp + fn + eps)` |
| `background_iou` | `tn / (tn + fp + fn + eps)` |
| `balanced_iou` | `0.5 * (foreground_iou + background_iou)` |
| `mcc` | `(tp*tn - fp*fn) / sqrt((tp+fp)*(tp+fn)*(tn+fp)*(tn+fn))`, `0` if the denominator is `0` |
| `precision` | `tp / (tp + fp + eps)` |
| `recall` | `tp / (tp + fn + eps)` |

**Aggregation order (macro):** counts are pooled over all tiles of a region within a (region, seed, arm) cell; the region-level endpoint is computed from those pooled counts. The seed effect is the **unweighted mean over the three fixed target regions** of the paired region-level difference (pooled-source arm minus source-only control arm). All headline numbers follow this order; no per-tile averaging is used.

**Interval family A (seed-stratified t):** the three seed effects (n = 3) are treated as the sampling units; the reported interval is `mean +/- t(0.975, df=2) * sd/sqrt(3)`. Regions are fixed.

**Interval family B (connected-component bootstrap, seed-conditioned):** spatial units are connected components of the reference mask within each region; components and tiles are resampled within each seed (regions fixed), 10,000 draws; the interval is the 2.5th-97.5th percentile of the draw distribution.

**Decision rule for strength:** unless stated otherwise, a claim is treated as supported only when **both families exclude zero** and the sign is consistent across all three seeds.

---

## 2. E1 - full-tile evaluation and screening endpoints

**Unit change.** The target regions (Hokkaido Iburi-Tobu, Lombok, Palu) are re-tiled with exactly the same windowing rule used for the published benchmark, but **without** the "at least one reference foreground pixel" filter. The published unit is therefore a strict subset of the full-tile unit; the two are nested, not alternatives, and this will be stated in the main text.

**Models.** The two matched-exposure architectures (ResUNet, Bottleneck-LiteASK), both arms (source-only control, pooled source), three seeds (42, 2026, 777). No new training.

**Tile-level positive call.** A tile is called positive when the predicted foreground pixel fraction exceeds `tau`. `tau` is fixed at {0.001, 0.005, 0.01, 0.05} and **all four are reported**; no single value may be selected post hoc. The ranking score used for `precision@k` / `recall@k` is the predicted foreground pixel fraction itself.

**Endpoints.** Per region x architecture x seed: full-tile false-alarm rate (fraction of zero-foreground tiles called positive, at each tau); in-domain miss rate (fraction of foreground tiles called negative); `precision@k%`, `recall@k%` for k = 1, 5, 10, 20; review-budget curve and AUPRC.

**Baseline.** Random ranking on the same tile population (expected `precision@k` = the full-tile landslide-tile prevalence), reported per region; differences carry both interval families.

**Pass rule.** The statement "can support response-phase screening" is retained only if, in at least 2 of 3 regions and on both architectures, the `precision@k` / `recall@k` difference from the random baseline has a consistent sign across all three seeds **and** both interval families exclude zero.

**Fail rule.** Otherwise the verb is downgraded to tile-level priority ranking for expert review, and the full-tile false-alarm rate moves into the limitations subsection.

**Boundary retained.** Full-tile evaluation is not scene-level evaluation: areas not covered by any tile still cannot be counted. "Complete-map quality" and "operational readiness" remain not assessable, and the corresponding "Not assessable" row of the evidence-boundary table is retained unchanged.

---

## 3. E2 - calibration diagnostics across 3 seeds x 2 architectures

**Domains.** CAS source validation, Hokkaido Iburi-Tobu, Lombok, Palu.
**Models.** ResUNet and Bottleneck-LiteASK; seeds 42, 2026, 777; both arms.

**Endpoints.** Per-domain reliability curve with 15 equal-frequency bins; ECE; error rate and mean confidence among pixels with confidence >= 0.90 (the same convention as the current single-seed number); the analogous quantity for the pooled-source arm.

**Pass rule.** The unconditional statement is retained if the direction "in-domain high-confidence error << the three target regions" holds for **all** 3 seeds x 2 architectures and the in-domain interval does not overlap the target-region intervals.

**Partial rule.** If one domain is an exception, the wording is restricted to "on these test domains" and the exception is listed.

**Fail rule.** The absolute-increase sentence is removed from the abstract and replaced by interval reporting.

**Reporting caveat (mandatory).** The current 0.69% / 12.08% figures are pixel-pooled statistics from a single seed, a single architecture and a 128x128 evaluation of an earlier checkpoint. The provenance change must be stated in the new table caption so that the new numbers are not presented as contradicting the old ones.

---

## 4. E3 - matched-exposure contrast on two further backbones

**Backbones.** SegFormer-B0 and DeepLabV3+. They are chosen because both are already implemented in the four-architecture source-domain benchmark; any other backbone would additionally require re-running its source-domain baseline.

**Protocol (identical to the existing two-backbone contrast in every item).** 1,120 optimizer steps, batch size 32, 128x128 input, five source slots each at weight 0.20, selected augmentation configuration (none), three seeds, the same stepwise cosine schedule, checkpoint selection on source-domain validation only. Pooled arm = CAS + Jiuzhai Valley + Longxi River + Moxitaidi + Wenchuan; control arm = five CAS replay slots.

**Required prerequisite (corrected during set-up, disclosed here).** Each matched-exposure run must be initialised from the source-only checkpoint of the *same* backbone, trained on CAS under the selected no-augmentation configuration. For ResUNet and Bottleneck-LiteASK those checkpoints already exist; for SegFormer-B0 and DeepLabV3+ they do not, because the augmentation-selection grid was run on the original two backbones only. The two extra backbones therefore require **6 additional 50-epoch source-only runs** (2 backbones x 3 seeds) before the 12 contrast runs. E3 is consequently 18 runs, not 12. This correction was made before any contrast run was executed and is recorded in the deviation log below.

**Pass rule.** "cross-architecture" is retained if at least 3 of the 4 backbones show a same-sign MCC effect across all three seeds with both interval families excluding zero.

**Fallback.** If only two backbones qualify, the word is changed to "two tested backbones" and nothing else changes.

**Mandatory reporting.** If either new backbone reverses sign, this must be reported in the main text with a per-backbone conditional statement; it may not be confined to the supplementary material.

---

## 5. Multiplicity and inference policy

No p-values are introduced. Inference stays with the two interval families and the per-seed sign consistency already used in the manuscript. All configurations that are run are reported, including null and reversed ones; no configuration may be withheld.

---

## 6. Deviation log

| Date | Item | Change | Reason |
|---|---|---|---|
| 2026-10-15 | E3 run count | 12 -> 18 (adds 6 source-only runs) | Per-backbone source-only initialisation checkpoints did not exist for the two new backbones; disclosed before the first contrast run |
| 2026-10-15 | E1 cost branch | "zero new runs if cached" branch closed | The distributed target-region archives are already foreground-filtered (image counts equal the foreground-tile counts, with gaps in the tile numbering), so zero-foreground tiles exist nowhere in the available data; E1 requires re-tiling from unfiltered imagery plus 36 inference passes |

---

## 7. Fixed analysis artefacts

Endpoint code: `scripts/route1_tile_bootstrap.py` (`metrics`, lines 65-90) and `scripts/q2_x3_seed_stratified_reanalysis.py` (aggregation, interval family A).
Interval family B: `scripts/q2_x3_spatial_bootstrap.py`, `scripts/route1_spatial_cluster_bootstrap.py`.
The cloud environment is pinned to the same package versions as the environment that produced the existing results.
| 2026-10-15 | E2 binning rule | 4 equal-width bins (existing script) supplemented by 15 equal-frequency bins | The original `evaluate_confidence_calibration.py` implements 4 equal-width bins; Note S1 fixes 15 equal-frequency bins, so a separate implementation was written and run. Both are reported; the original script was not modified |
| 2026-10-15 | E2 arm scope | P0 section 3 did not state which arm the calibration claim applies to; both arms are now reported | The direction holds robustly in the source-only control arm and is diluted in the pooled arm, so the arm must be stated explicitly rather than left implicit |
| 2026-10-15 | E1 feasibility | E1 as specified cannot be executed with the published data | Verified: (i) the local region archives byte-match the official Zenodo distribution 10.5281/zenodo.10294997 (Hokkaido 745717976, Lombok 179943364, palu 408086146 bytes), so they are the complete published subset rather than a filtered copy; (ii) the dataset paper lists exactly 1484 / 436 / 817 tiles for these regions and every published mask contains landslide pixels; (iii) the official cropping code (github.com/Aizu0/CAS-Landslide-Dataset-production-code, Cropping.py) is an unfiltered 512x512 sliding window at stride 256, so the positive filter was applied afterwards and the reference masks for the empty windows were never published; (iv) the legacy DigitalGlobe Open Data portal that supplied Lombok and Palu no longer resolves and the Maxar Open Data bucket no longer hosts those events. E1 therefore depends on unpublished intermediate data held by the dataset authors, not on compute. |
