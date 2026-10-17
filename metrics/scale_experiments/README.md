# Scale experiments

Two supplementary experiments reported in Supplementary Note S2, Table S19 and
Table S20 of the GNHR submission. Neither requires retraining of the
matched-exposure arms.

## `source_coarsening.csv` (Table S19)

ResUNet source-only models trained on the CAS source domain after downsampling by
factor `k` and upsampling back to the original size, evaluated zero-shot on the
three primary targets. Three seeds per factor; `k = 1` uses the selected
no-augmentation source-only checkpoints (`q2_x2_aug_none_resunet_seed*`).

Columns: `k`, `seed`, per-region IoU, `macro_iou`.

## `evaluation_scale_sweep.csv` (Table S20)

Every checkpoint left unchanged; only the amount of detail in the target input is
varied, by downsampling the 128-pixel input tensor to `1/s` and upsampling back
before inference. Reference masks and geometry are untouched, so IoU is computed on
an unchanged label field.

Columns: `model` (`source-only` or `pooled`), `seed`, `s`, per-region IoU,
`macro_iou`, and whether the Hokkaido IoU exceeds the constant all-landslide mask
score of 0.1025.

## Scripts

`scripts/scale_experiments/` holds the driver scripts. They were run against the
project tree at `D:\landslide_unet_project`; the absolute paths at the top of each
file must be pointed at a local checkout before use. Training used the existing
`scripts/train_unified.py` with `--model ResUNet --epochs 50 --batch-size 32
--input-size 128 --lr 1e-4 --augmentation none --skip-external-eval`.

On Windows, `--num-workers 0` was about four times faster than `--num-workers 4`
because the DataLoader respawns workers each epoch; this affects wall-clock only,
not the results.

## Result

Neither experiment found a smoothing setting that raised the three-region macro IoU.
Coarsening the source monotonically reduced transfer (macro IoU 0.0638 at k = 1,
0.0464 at k = 4, 0.0081 at k = 16), and the Hokkaido gain of the pooled models is
detail-conditional. Lombok improved slightly at a two-fold smoothing in both model
families.
