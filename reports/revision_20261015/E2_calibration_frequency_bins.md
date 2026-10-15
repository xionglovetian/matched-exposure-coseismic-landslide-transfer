# E2 (frequency-bin variant): reliability and ECE

Equal-frequency 15 bins, as fixed in Supplementary Note S1. ECE = sum over bins of (bin pixel share) x |accuracy - mean confidence|.
High-confidence error rate (confidence >= 0.90) recomputed here as a consistency check against the original implementation.

| Backbone | Arm | Domain | ECE mean | ECE 95% CI | High-conf error mean (%) | High-conf error 95% CI (%) |
|---|---|---|---:|---|---:|---|
| ResUNet | pooled | CAS source validation | 0.0256 | [+0.0097, +0.0414] | 0.94 | [+0.65, +1.22] |
| ResUNet | pooled | Hokkaido Iburi-Tobu | 0.0188 | [-0.0090, +0.0465] | 2.65 | [+0.92, +4.38] |
| ResUNet | pooled | Lombok | 0.0450 | [-0.0081, +0.0981] | 2.87 | [+0.11, +5.63] |
| ResUNet | pooled | Palu | 0.0190 | [+0.0123, +0.0257] | 0.83 | [+0.59, +1.07] |
| ResUNet | cas-multistream | CAS source validation | 0.0166 | [+0.0105, +0.0227] | 0.69 | [+0.58, +0.81] |
| ResUNet | cas-multistream | Hokkaido Iburi-Tobu | 0.1202 | [+0.0740, +0.1664] | 12.56 | [+9.17, +15.94] |
| ResUNet | cas-multistream | Lombok | 0.0592 | [+0.0377, +0.0807] | 5.39 | [+4.26, +6.53] |
| ResUNet | cas-multistream | Palu | 0.0133 | [+0.0093, +0.0174] | 1.74 | [+1.58, +1.91] |
| Bottleneck-LiteASK | pooled | CAS source validation | 0.0286 | [+0.0202, +0.0370] | 0.72 | [+0.64, +0.81] |
| Bottleneck-LiteASK | pooled | Hokkaido Iburi-Tobu | 0.0156 | [-0.0108, +0.0420] | 2.64 | [-0.65, +5.93] |
| Bottleneck-LiteASK | pooled | Lombok | 0.0685 | [+0.0441, +0.0929] | 5.01 | [+3.23, +6.80] |
| Bottleneck-LiteASK | pooled | Palu | 0.0128 | [-0.0047, +0.0304] | 1.11 | [+1.07, +1.14] |
| Bottleneck-LiteASK | cas-multistream | CAS source validation | 0.0161 | [+0.0121, +0.0201] | 0.50 | [+0.42, +0.58] |
| Bottleneck-LiteASK | cas-multistream | Hokkaido Iburi-Tobu | 0.1170 | [+0.0768, +0.1573] | 11.93 | [+8.68, +15.18] |
| Bottleneck-LiteASK | cas-multistream | Lombok | 0.0640 | [+0.0477, +0.0803] | 5.61 | [+4.89, +6.33] |
| Bottleneck-LiteASK | cas-multistream | Palu | 0.0156 | [-0.0064, +0.0377] | 2.09 | [+1.04, +3.14] |

