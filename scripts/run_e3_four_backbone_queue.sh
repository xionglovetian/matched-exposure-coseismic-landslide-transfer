#!/bin/bash
# Four-backbone matched-exposure queue (revision-phase E3).
#
# 18 runs in total:
#   phase p1 - 6 source-only source-domain runs (SegFormer-B0, DeepLabV3+) that
#              supply the no-augmentation initialisation the contrast needs;
#   phase p2 - 12 matched-exposure contrast runs (2 new backbones x 3 seeds x
#              pooled / cas-multistream).
# The two original backbones (ResUNet, Bottleneck-LiteASK) already have these
# runs, so they are not repeated here.
#
# Usage: LANDSLIDE_ROOT=/path/to/project ./run_e3_four_backbone_queue.sh [p1|p2|all]
set -u
PHASE=${1:-all}
ROOT=${LANDSLIDE_ROOT:-$PWD}
PY=${LANDSLIDE_PYTHON:-python}
LOG=$ROOT/logs_e3
mkdir -p "$LOG"
cd "$ROOT" || exit 2
echo "phase=$PHASE start $(date -Is)" | tee -a "$LOG/run_all.log"

launch () {
  local name=$1; shift
  if [ -f "$ROOT/outputs/$name/metrics.json" ]; then
    echo "SKIP $name" | tee -a "$LOG/run_all.log"; return
  fi
  if [ -f "$ROOT/outputs/$name/FAILED" ]; then
    echo "SKIP-FAILED $name" | tee -a "$LOG/run_all.log"; return
  fi
  mkdir -p "$ROOT/outputs/$name"
  echo "START $name $(date -Is)" | tee -a "$LOG/run_all.log"
  if $PY "$@" > "$LOG/$name.log" 2>&1; then
    echo "DONE $name $(date -Is)" | tee -a "$LOG/run_all.log"
  else
    echo "FAIL $name $(date -Is)" | tee -a "$LOG/run_all.log"
    touch "$ROOT/outputs/$name/FAILED"
  fi
}

phase1 () {
  for ARCH in SegFormerB0 DeepLabV3Plus; do
    TAG=$(echo "$ARCH" | tr 'A-Z' 'a-z')
    for SEED in 42 2026 777; do
      launch "q2_x2_aug_none_${TAG}_seed${SEED}" scripts/train_unified.py \
        --model "$ARCH" --augmentation none --seed "$SEED" --epochs 50 \
        --batch-size 32 --input-size 128 --lr 1e-4 --weight-decay 1e-4 \
        --val-interval 5 --checkpoint-interval 10 --num-workers 4 --amp \
        --skip-external-eval --output-dir "$ROOT/outputs/q2_x2_aug_none_${TAG}_seed${SEED}"
    done
  done
}

phase2 () {
  for ARCH in SegFormerB0 DeepLabV3Plus; do
    TAG=$(echo "$ARCH" | tr 'A-Z' 'a-z')
    for SEED in 42 2026 777; do
      for REGIME in pooled cas-multistream; do
        launch "q2_x3_${TAG}_${REGIME}_seed${SEED}" scripts/train_exposure_matched.py \
          --regime "$REGIME" --model "$ARCH" --seed "$SEED" \
          --steps 1120 --batch-size 32 --input-size 128 --lr 1e-4 --min-lr 1e-6 \
          --weight-decay 1e-4 --checkpoint-interval 280 --num-workers 4 --amp \
          --init-checkpoint "$ROOT/outputs/q2_x2_aug_none_${TAG}_seed${SEED}/best_model.pth" \
          --output-dir "$ROOT/outputs/q2_x3_${TAG}_${REGIME}_seed${SEED}"
      done
    done
  done
}

case $PHASE in
  p1) phase1 ;;
  p2) phase2 ;;
  all) phase1; phase2 ;;
  *) echo "unknown phase $PHASE"; exit 2 ;;
esac
echo "PHASE_${PHASE}_DONE $(date -Is)" | tee -a "$LOG/run_all.log"
