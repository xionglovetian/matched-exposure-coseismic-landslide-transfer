# -*- coding: utf-8 -*-
"""Build scale-coarsened copies of the CAS source domain.

For each factor k the image is downsampled to 1/k and upsampled back to its original
size, which removes high-frequency detail in the same way a k-times coarser sensor
would, without changing the crop geometry or the rest of the pipeline.
Masks use nearest-neighbour so the labels stay binary.
"""

import os
import shutil
import sys
from concurrent.futures import ProcessPoolExecutor

from PIL import Image

SRC = r"D:\landslide_unet_project\repos\AS-UNet\inputs\data_sum_moxizhen+bijie"
FACTORS = [4, 16]


def coarsen_one(args):
    src, dst, k, is_mask = args
    try:
        with Image.open(src) as im:
            w, h = im.size
            nw, nh = max(1, w // k), max(1, h // k)
            if is_mask:
                small = im.convert("L").resize((nw, nh), Image.NEAREST)
                out = small.resize((w, h), Image.NEAREST)
            else:
                small = im.convert("RGB").resize((nw, nh), Image.BOX)
                out = small.resize((w, h), Image.BICUBIC)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            out.save(dst)
        return True
    except Exception as e:
        print("FAIL", src, e)
        return False


def main():
    jobs = []
    for k in FACTORS:
        root = f"{SRC}_k{k}"
        if os.path.isdir(root):
            shutil.rmtree(root)
        for split in ("train", "val"):
            for kind, is_mask in (("images", False), ("masks", True)):
                d = os.path.join(SRC, split, kind)
                for f in os.listdir(d):
                    jobs.append((os.path.join(d, f), os.path.join(root, split, kind, f), k, is_mask))
    print(f"{len(jobs)} files to write")
    ok = 0
    with ProcessPoolExecutor(max_workers=min(16, os.cpu_count() or 4)) as ex:
        for r in ex.map(coarsen_one, jobs, chunksize=32):
            ok += int(r)
    print(f"done: {ok}/{len(jobs)}")
    for k in FACTORS:
        root = f"{SRC}_k{k}"
        n = sum(len(os.listdir(os.path.join(root, s, t))) for s in ("train", "val") for t in ("images", "masks"))
        print(f"  {os.path.basename(root)}: {n} files")


if __name__ == "__main__":
    main()
