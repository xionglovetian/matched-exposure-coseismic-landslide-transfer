# Revision-phase experiments (2026-10-15)

Everything in this directory belongs to the revision phase that added the
four-backbone replication, the multi-seed calibration diagnostics and the
tile-level false-alarm diagnostic.

| File | Content |
|---|---|
| `PRE_REGISTRATION_S1.md` | Supplementary Note S1: endpoints, units, interval families and pass/fail rules, frozen before any of the three experiments was run, with the deviation log recorded afterwards |
| `E3_four_backbone_matched_exposure.md` | Four-backbone matched-exposure contrast and the pre-registered PASS decision |
| `E2_calibration_multiseed.md` | High-confidence error across 3 seeds x 2 architectures x 2 arms, and the pre-registered verdict |
| `E2_calibration_frequency_bins.md` | Reliability curves and ECE under the equal-frequency 15-bin rule |
| `E1_partial_background_false_alarm.md` | The partial diagnostic that was possible after the pre-registered E1 turned out to be blocked |

## Status summary

- **E3: PASS.** MCC holds in four of four backbones with both interval families
  excluding zero and all three seeds sharing a sign; the pre-registered rule
  required three of four. Macro IoU holds in three of four.
- **E2: the source-only statement passes, the pooled statement does not.** Under
  the source-only control arm every seed shows a lower high-confidence error
  rate on the source domain than on any target region, with non-overlapping
  intervals. Under the pooled arm the rule fails on Palu for ResUNet and on the
  Hokkaido interval for Bottleneck-LiteASK.
- **E1: not executed.** The pre-registered E1 requires tiles with zero reference
  foreground. The released region archives are already foreground-filtered, so
  no such tiles were ever distributed and the tile-level screening endpoints
  cannot be computed from the public data without re-tiling the original
  imagery.

## Deviations from the pre-registration

- E3 was planned as twelve runs and executed as eighteen. The matched-exposure
  contrast has to start from each backbone's own source-only
  no-augmentation weights, and those did not exist for SegFormer-B0 or
  DeepLabV3+, so six 50-epoch source-domain runs were added first. Their CAS
  validation IoU values (DeepLabV3+ 0.6763 / 0.6786 / 0.6809, SegFormer-B0
  0.6226 / 0.6971 / 0.6587) fall inside the range already reported for the two
  original backbones.
- E1 could not be executed at all, for the data reason above. Only a
  pixel-level background false-positive share inside positive-containing tiles
  is reported, and the report states explicitly that it is not a substitute for
  E1.

## Reproduction

The interval and report outputs in this directory are regenerated from the
packaged metrics alone, with no imagery and no checkpoints:

```powershell
python scripts/q2_x3_target_macro_component_bootstrap.py --output metrics/q2_x3_bootstrap/x3_target_macro_component.csv --draws 10000
python scripts/report_e3_four_backbone.py
python scripts/report_e2_calibration.py
python scripts/report_e2_frequency_bins.py
python scripts/e1_partial_background_false_alarm.py
```
