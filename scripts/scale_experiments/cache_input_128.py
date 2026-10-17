# -*- coding: utf-8 -*-
"""Pre-resize the coarsened source domains to the network input size so that the
training loop does no file-level resizing. The transform is the same deterministic
resize the loader would apply, so the model sees an identical input distribution."""

import os
import sys
from concurrent.futures import ProcessPoolExecutor

from PIL import Image

BASE = r"D:\landslide_unet_project\repos\AS-UNet\inputs"
SIZE = 128


def one(args):
    src, dst, is_mask = args
    try:
        with Image.open(src) as im:
            if is_mask:
                out = im.convert("L").resize((SIZE, SIZE), Image.NEAREST)
            else:
                out = im.convert("RGB").resize((SIZE, SIZE), Image.BILINEAR)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            out.save(dst, optimize=False, compress_level=1)
        return 1
    except Exception as e:
        print("FAIL", src, e)
        return 0


def main():
    jobs = []
    for k in (4, 16):
        src_root = f"{BASE}/data_sum_moxizhen+bijie_k{k}"
        dst_root = f"{BASE}/data_sum_moxizhen+bijie_k{k}_128"
        for split in ("train", "val"):
            for kind, is_mask in (("images", False), ("masks", True)):
                d = os.path.join(src_root, split, kind)
                for f in os.listdir(d):
                    jobs.append((os.path.join(d, f), os.path.join(dst_root, split, kind, f), is_mask))
    print(f"{len(jobs)} files")
    ok = 0
    with ProcessPoolExecutor(max_workers=16) as ex:
        for r in ex.map(one, jobs, chunksize=64):
            ok += r
    print(f"done {ok}/{len(jobs)}")
    for k in (4, 16):
        p = f"{BASE}/data_sum_moxizhen+bijie_k{k}_128"
        n = sum(len(os.listdir(os.path.join(p, s, t))) for s in ("train", "val") for t in ("images", "masks"))
        sz = sum(os.path.getsize(os.path.join(p, s, t, f))
                 for s in ("train", "val") for t in ("images", "masks") for f in os.listdir(os.path.join(p, s, t)))
        print(f"  {os.path.basename(p)}: {n} files, {sz/1048576:.1f} MB")


if __name__ == "__main__":
    main()
