# E2 result: calibration diagnostics across 3 seeds x 2 architectures

Endpoint: error rate among pixel predictions with confidence >= 0.90 (same convention as the existing single-seed report).
Domains: CAS source validation plus the three fixed target regions. Arms: pooled source and CAS replay control.
Interval: seed-stratified Student t across the three training seeds (df = 2).

## ResUNet / pooled

| Domain | Seeds 42 / 2026 / 777 (%) | Mean (%) | SD | 95% CI (%) |
|---|---|---:|---:|---|
| CAS source validation | 1.07 / 0.88 / 0.86 | 0.94 | 0.12 | [+0.65, +1.22] |
| Hokkaido Iburi-Tobu | 2.04 / 2.50 / 3.41 | 2.65 | 0.70 | [+0.92, +4.38] |
| Lombok | 1.96 / 2.53 / 4.11 | 2.87 | 1.11 | [+0.11, +5.63] |
| Palu | 0.93 / 0.81 / 0.74 | 0.83 | 0.10 | [+0.59, +1.07] |

## ResUNet / cas-multistream

| Domain | Seeds 42 / 2026 / 777 (%) | Mean (%) | SD | 95% CI (%) |
|---|---|---:|---:|---|
| CAS source validation | 0.65 / 0.74 / 0.69 | 0.69 | 0.05 | [+0.58, +0.81] |
| Hokkaido Iburi-Tobu | 13.95 / 11.23 / 12.49 | 12.56 | 1.36 | [+9.17, +15.94] |
| Lombok | 4.87 / 5.69 / 5.74 | 5.43 | 0.49 | [+4.22, +6.65] |
| Palu | 1.81 / 1.68 / 1.73 | 1.74 | 0.07 | [+1.58, +1.91] |

## Bottleneck-LiteASK / pooled

| Domain | Seeds 42 / 2026 / 777 (%) | Mean (%) | SD | 95% CI (%) |
|---|---|---:|---:|---|
| CAS source validation | 0.71 / 0.70 / 0.77 | 0.72 | 0.04 | [+0.64, +0.81] |
| Hokkaido Iburi-Tobu | 3.37 / 1.11 / 3.43 | 2.64 | 1.32 | [-0.65, +5.93] |
| Lombok | 5.32 / 5.53 / 4.19 | 5.01 | 0.72 | [+3.23, +6.80] |
| Palu | 1.10 / 1.09 / 1.12 | 1.11 | 0.01 | [+1.07, +1.14] |

## Bottleneck-LiteASK / cas-multistream

| Domain | Seeds 42 / 2026 / 777 (%) | Mean (%) | SD | 95% CI (%) |
|---|---|---:|---:|---|
| CAS source validation | 0.54 / 0.47 / 0.53 | 0.51 | 0.04 | [+0.42, +0.61] |
| Hokkaido Iburi-Tobu | 13.23 / 12.18 / 10.52 | 11.97 | 1.37 | [+8.57, +15.37] |
| Lombok | 5.45 / 5.46 / 5.94 | 5.62 | 0.28 | [+4.92, +6.32] |
| Palu | 2.60 / 1.83 / 1.87 | 2.10 | 0.44 | [+1.02, +3.18] |

## Pre-registered E2 decision

- ResUNet / pooled: direction (source < all three targets for every seed) = False; source interval strictly below target intervals for = no (hokkaido_iburi_tobu, lombok, palu overlap) (source mean 0.94% vs Hokkaido 2.65%, Lombok 2.87%, Palu 0.83%)
- ResUNet / cas-multistream: direction (source < all three targets for every seed) = True; source interval strictly below target intervals for = all three target regions (source mean 0.69% vs Hokkaido 12.56%, Lombok 5.43%, Palu 1.74%)
- Bottleneck-LiteASK / pooled: direction (source < all three targets for every seed) = True; source interval strictly below target intervals for = no (hokkaido_iburi_tobu overlap) (source mean 0.72% vs Hokkaido 2.64%, Lombok 5.01%, Palu 1.11%)
- Bottleneck-LiteASK / cas-multistream: direction (source < all three targets for every seed) = True; source interval strictly below target intervals for = all three target regions (source mean 0.51% vs Hokkaido 11.97%, Lombok 5.62%, Palu 2.10%)

- Every one of the 3 seeds x 2 architectures x 2 arms combinations shows a lower source-domain high-confidence error rate than each target region: **False**.
- Source-domain interval strictly below all three target-region intervals in every combination: **False**.
- Pre-registered rule (direction holds for all 3 seeds x 2 architectures and intervals do not overlap): **FAIL**.
