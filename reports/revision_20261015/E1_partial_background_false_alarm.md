# E1 partial: pixel-level background false-alarm rate from existing tile outputs

This is NOT the pre-registered E1. The pre-registered E1 needs tiles with zero reference foreground, which do not exist
in the distributed dataset. What can be computed from outputs already on disk is the false-positive share of
background pixels inside the evaluated (positive-containing) tiles: FP / (FP + TN).

| Backbone | Arm | Region | Background FP rate (%) | Seeds 42 / 2026 / 777 |
|---|---|---|---:|---|
| ResUNet | pooled | hokkaido_iburi_tobu | 2.442 | 3.075 / 2.386 / 1.864 |
| ResUNet | pooled | lombok | 13.207 | 11.091 / 13.413 / 15.118 |
| ResUNet | pooled | palu | 4.679 | 5.538 / 4.264 / 4.236 |
| ResUNet | pooled | **three-region mean** | **6.776** | |
| ResUNet | cas-multistream | hokkaido_iburi_tobu | 16.489 | 20.317 / 13.417 / 15.734 |
| ResUNet | cas-multistream | lombok | 9.445 | 8.937 / 9.356 / 10.043 |
| ResUNet | cas-multistream | palu | 6.691 | 6.373 / 6.346 / 7.353 |
| ResUNet | cas-multistream | **three-region mean** | **10.875** | |
| Bottleneck-LiteASK | pooled | hokkaido_iburi_tobu | 3.412 | 4.504 / 2.531 / 3.200 |
| Bottleneck-LiteASK | pooled | lombok | 15.365 | 15.807 / 16.403 / 13.885 |
| Bottleneck-LiteASK | pooled | palu | 5.326 | 5.010 / 6.143 / 4.825 |
| Bottleneck-LiteASK | pooled | **three-region mean** | **8.034** | |
| Bottleneck-LiteASK | cas-multistream | hokkaido_iburi_tobu | 16.467 | 17.940 / 20.003 / 11.457 |
| Bottleneck-LiteASK | cas-multistream | lombok | 9.207 | 8.212 / 9.471 / 9.938 |
| Bottleneck-LiteASK | cas-multistream | palu | 7.775 | 10.639 / 5.911 / 6.775 |
| Bottleneck-LiteASK | cas-multistream | **three-region mean** | **11.150** | |
| SegFormer-B0 | pooled | hokkaido_iburi_tobu | 2.094 | 2.341 / 1.969 / 1.971 |
| SegFormer-B0 | pooled | lombok | 12.092 | 12.984 / 11.818 / 11.474 |
| SegFormer-B0 | pooled | palu | 2.779 | 2.996 / 2.751 / 2.592 |
| SegFormer-B0 | pooled | **three-region mean** | **5.655** | |
| SegFormer-B0 | cas-multistream | hokkaido_iburi_tobu | 4.048 | 4.404 / 3.577 / 4.164 |
| SegFormer-B0 | cas-multistream | lombok | 10.597 | 11.030 / 10.705 / 10.057 |
| SegFormer-B0 | cas-multistream | palu | 4.645 | 4.580 / 5.114 / 4.242 |
| SegFormer-B0 | cas-multistream | **three-region mean** | **6.430** | |
| DeepLabV3+ | pooled | hokkaido_iburi_tobu | 2.895 | 2.532 / 3.808 / 2.344 |
| DeepLabV3+ | pooled | lombok | 15.726 | 16.485 / 17.033 / 13.661 |
| DeepLabV3+ | pooled | palu | 4.016 | 4.006 / 4.174 / 3.869 |
| DeepLabV3+ | pooled | **three-region mean** | **7.546** | |
| DeepLabV3+ | cas-multistream | hokkaido_iburi_tobu | 16.313 | 15.272 / 16.865 / 16.802 |
| DeepLabV3+ | cas-multistream | lombok | 10.944 | 10.768 / 11.679 / 10.383 |
| DeepLabV3+ | cas-multistream | palu | 4.966 | 4.515 / 5.348 / 5.036 |
| DeepLabV3+ | cas-multistream | **three-region mean** | **10.741** | |

## Reading

The direction is region-dependent, not uniform:

- **Hokkaido Iburi-Tobu**: the pooled arm cuts the background false-positive share sharply in all four backbones (ResUNet 16.49% -> 2.44%; DeepLabV3+ 16.31% -> 2.90%; Bottleneck-LiteASK 16.47% -> 3.41%; SegFormer-B0 4.05% -> 2.09%).
- **Palu**: a smaller reduction in all four backbones (ResUNet 6.69% -> 4.68%; Bottleneck-LiteASK 7.78% -> 5.33%; SegFormer-B0 4.65% -> 2.78%; DeepLabV3+ 4.97% -> 4.02%).
- **Lombok**: the pooled arm *raises* the background false-positive share in all four backbones (ResUNet 9.45% -> 13.21%; Bottleneck-LiteASK 9.21% -> 15.37%; SegFormer-B0 10.60% -> 12.09%; DeepLabV3+ 10.94% -> 15.73%).

So the false-alarm side of the ledger follows the same region dependence as the headline effect, and Lombok moves in the opposite direction on this endpoint.

**Scope.** This is a pixel-level measure inside tiles that contain at least one reference landslide pixel. It does **not** measure tile-level false alarms on tiles that contain no reference landslide, which is what the pre-registered E1 requires. It can be reported as a supporting diagnostic, never as a substitute for E1.
