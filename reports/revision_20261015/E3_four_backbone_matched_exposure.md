# E3 result: matched-exposure contrast across four backbones

Regions fixed to Hokkaido Iburi-Tobu, Lombok, Palu. Seeds 42/2026/777. Delta = pooled source minus source-only control arm.
Family A = seed-stratified Student t (df=2). Family B = connected-component bootstrap (component / merged30), 10000 draws, seed-conditioned.
Reproducibility: the ResUNet and Bottleneck-LiteASK rows reproduce the published table values exactly.

| Backbone | Endpoint | Delta | Family A 95% CI | Family B component | Family B merged30 | Both families exclude 0 | Seeds 42/2026/777 |
|---|---|---:|---|---|---|---|---|
| ResUNet | iou | +0.0773 | [+0.0514, +0.1031] | [+0.0345, +0.0849] | [+0.0639, +0.0912] | YES | +0.0883 / +0.0759 / +0.0676 |
| ResUNet | balanced_iou | +0.0603 | [+0.0354, +0.0852] | [+0.0415, +0.0683] | [+0.0489, +0.0728] | YES | +0.0719 / +0.0548 / +0.0542 |
| ResUNet | mcc | +0.1573 | [+0.1406, +0.1739] | [+0.0718, +0.1663] | [+0.1397, +0.1750] | YES | +0.1650 / +0.1533 / +0.1534 |
| ResUNet | precision | +0.1784 | [+0.1590, +0.1977] | [+0.0475, +0.1842] | [+0.1637, +0.1923] | YES | +0.1723 / +0.1756 / +0.1871 |
| ResUNet | recall | +0.1075 | [+0.0939, +0.1211] | [+0.0315, +0.1328] | [+0.0850, +0.1351] | YES | +0.1054 / +0.1138 / +0.1034 |
| Bottleneck-LiteASK | iou | +0.0456 | [-0.0056, +0.0968] | [+0.0097, +0.0620] | [+0.0250, +0.0713] | no | +0.0298 / +0.0689 / +0.0380 |
| Bottleneck-LiteASK | balanced_iou | +0.0383 | [+0.0087, +0.0678] | [+0.0160, +0.0533] | [+0.0217, +0.0586] | YES | +0.0329 / +0.0519 / +0.0300 |
| Bottleneck-LiteASK | mcc | +0.0990 | [+0.0240, +0.1740] | [+0.0228, +0.1254] | [+0.0657, +0.1379] | YES | +0.0775 / +0.1335 / +0.0859 |
| Bottleneck-LiteASK | precision | +0.1182 | [+0.0174, +0.2190] | [+0.0126, +0.1496] | [+0.0776, +0.1647] | YES | +0.0825 / +0.1623 / +0.1097 |
| Bottleneck-LiteASK | recall | +0.0549 | [+0.0016, +0.1082] | [-0.0281, +0.0946] | [+0.0207, +0.0907] | no | +0.0388 / +0.0793 / +0.0465 |
| SegFormer-B0 | iou | +0.0591 | [+0.0437, +0.0745] | [+0.0197, +0.0622] | [+0.0519, +0.0681] | YES | +0.0661 / +0.0568 / +0.0544 |
| SegFormer-B0 | balanced_iou | +0.0360 | [+0.0291, +0.0429] | [+0.0151, +0.0390] | [+0.0302, +0.0423] | YES | +0.0390 / +0.0356 / +0.0334 |
| SegFormer-B0 | mcc | +0.1047 | [+0.0821, +0.1274] | [+0.0371, +0.1085] | [+0.0933, +0.1181] | YES | +0.1152 / +0.1001 / +0.0988 |
| SegFormer-B0 | precision | +0.1318 | [+0.1232, +0.1405] | [+0.0328, +0.1355] | [+0.1182, +0.1478] | YES | +0.1353 / +0.1284 / +0.1318 |
| SegFormer-B0 | recall | +0.0757 | [+0.0336, +0.1179] | [+0.0190, +0.0838] | [+0.0599, +0.0909] | YES | +0.0953 / +0.0666 / +0.0653 |
| DeepLabV3+ | iou | +0.0610 | [+0.0295, +0.0926] | [+0.0288, +0.0673] | [+0.0509, +0.0722] | YES | +0.0487 / +0.0740 / +0.0605 |
| DeepLabV3+ | balanced_iou | +0.0471 | [+0.0249, +0.0694] | [+0.0338, +0.0523] | [+0.0391, +0.0552] | YES | +0.0369 / +0.0536 / +0.0508 |
| DeepLabV3+ | mcc | +0.1333 | [+0.0829, +0.1836] | [+0.0644, +0.1420] | [+0.1174, +0.1477] | YES | +0.1111 / +0.1508 / +0.1379 |
| DeepLabV3+ | precision | +0.1511 | [+0.1226, +0.1796] | [+0.0393, +0.1582] | [+0.1370, +0.1636] | YES | +0.1429 / +0.1462 / +0.1642 |
| DeepLabV3+ | recall | +0.0982 | [+0.0103, +0.1860] | [+0.0369, +0.1336] | [+0.0704, +0.1288] | YES | +0.0688 / +0.1374 / +0.0883 |

## Pre-registered E3 decision

- MCC passes in **4 of 4** backbones: ResUNet, Bottleneck-LiteASK, SegFormer-B0, DeepLabV3+.
- Pre-registered rule requires >= 3 of 4 -> **PASS**: the term "cross-architecture" is retained.
- IoU passes in **3 of 4** backbones: ResUNet, SegFormer-B0, DeepLabV3+. Bottleneck-LiteASK remains the sole exception, exactly as the published text already states.
- No backbone reverses sign on MCC; every per-seed effect is positive for all four backbones.
