import os
import sys
import time
from typing import Tuple

import numpy as np

# Import shared palette from cfg.py at repo root
_ROOT = os.path.dirname(os.path.dirname(__file__))
if _ROOT not in sys.path:
    sys.path.append(_ROOT)
from cfg import colors  # noqa: E402


# ---- sRGB -> OKLab helpers ----
# Reference: https://bottosson.github.io/posts/oklab/
def _srgb_to_linear(c: np.ndarray) -> np.ndarray:
    c = c / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def rgb_to_oklab_array(r: np.ndarray, g: np.ndarray, b: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    r = _srgb_to_linear(r)
    g = _srgb_to_linear(g)
    b = _srgb_to_linear(b)

    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b

    l_ = np.cbrt(l)
    m_ = np.cbrt(m)
    s_ = np.cbrt(s)

    L = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
    a = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    b2 = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    return L, a, b2


def main(out_path: str = "colormap_oklab.npy"):
    pal = np.asarray(colors[:-1], dtype=np.float32)  # exclude air
    pr, pg, pb = pal[:, 0], pal[:, 1], pal[:, 2]
    pL, pA, pB = rgb_to_oklab_array(pr, pg, pb)
    palette_oklab = np.stack([pL, pA, pB], axis=1).astype(np.float32)  # [P,3]

    result = np.empty((256, 256, 256), dtype=np.uint16)

    g_grid, b_grid = np.mgrid[0:256, 0:256].astype(np.float32)

    t0 = time.time()
    for r in range(256):
        if r % 8 == 0:
            print(f"slice {r}/255 elapsed={time.time() - t0:.1f}s")
        r_plane = np.full_like(g_grid, float(r))
        L, A, B = rgb_to_oklab_array(r_plane, g_grid, b_grid)
        img = np.stack([L, A, B], axis=0).astype(np.float32)  # [3,256,256]
        diff = img[None, ...] - palette_oklab[:, :, None, None]  # [P,3,H,W]
        dist2 = (diff ** 2).sum(axis=1)  # [P,H,W]
        idx = dist2.argmin(axis=0).astype(np.uint16)
        result[r, :, :] = idx

    np.save(out_path, result)
    print(f"saved mapping to {out_path}; total {time.time() - t0:.1f}s")


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Prepare OKLab-based RGB->palette colormap (saves colormap_oklab.npy)")
    p.add_argument("--output", "-o", type=str, default="colormap_oklab.npy", help="output .npy path (default colormap_oklab.npy)")
    args = p.parse_args()
    main(args.output)

