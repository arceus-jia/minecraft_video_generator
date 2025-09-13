import time
import math
import os
import sys
from typing import Tuple

import numpy as np

# import shared palette from cfg.py (repo root)
_ROOT = os.path.dirname(os.path.dirname(__file__))
if _ROOT not in sys.path:
    sys.path.append(_ROOT)
from cfg import blocks, colors  # noqa: E402


# --- sRGB -> CIE Lab helpers (D65) ---
def _srgb_to_linear(c: np.ndarray) -> np.ndarray:
    c = c / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def _rgb_to_xyz(r: np.ndarray, g: np.ndarray, b: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    rl, gl, bl = _srgb_to_linear(r), _srgb_to_linear(g), _srgb_to_linear(b)
    x = 0.4124564 * rl + 0.3575761 * gl + 0.1804375 * bl
    y = 0.2126729 * rl + 0.7151522 * gl + 0.0721750 * bl
    z = 0.0193339 * rl + 0.1191920 * gl + 0.9503041 * bl
    return x, y, z


def _f_lab(t: np.ndarray) -> np.ndarray:
    delta = 6 / 29
    return np.where(t > delta ** 3, np.cbrt(t), t / (3 * delta * delta) + 4 / 29)


def rgb_to_lab_array(r: np.ndarray, g: np.ndarray, b: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    x, y, z = _rgb_to_xyz(r, g, b)
    Xn, Yn, Zn = 0.95047, 1.00000, 1.08883
    fx, fy, fz = _f_lab(x / Xn), _f_lab(y / Yn), _f_lab(z / Zn)
    L = 116 * fy - 16
    a = 500 * (fx - fy)
    b2 = 200 * (fy - fz)
    return L, a, b2


def main(out_path: str = "colormap_lab.npy"):
    pal = np.asarray(colors[: -1], dtype=np.float32)  # exclude air sentinel
    pr, pg, pb = pal[:, 0], pal[:, 1], pal[:, 2]
    pL, pA, pB = rgb_to_lab_array(pr, pg, pb)
    palette_lab = np.stack([pL, pA, pB], axis=1).astype(np.float32)  # [P,3]

    # result shape: [256,256,256], value in [0..P] (air handled by caller via alpha)
    result = np.empty((256, 256, 256), dtype=np.uint16)

    g_grid, b_grid = np.mgrid[0:256, 0:256].astype(np.float32)  # shape [256,256]

    t0 = time.time()
    for r in range(256):
        if r % 8 == 0:
            dt = time.time() - t0
            print(f"slice {r}/255, elapsed={dt:.1f}s")
        r_plane = np.full_like(g_grid, float(r))
        L, A, B = rgb_to_lab_array(r_plane, g_grid, b_grid)  # each [256,256]
        lab = np.stack([L, A, B], axis=0).astype(np.float32)  # [3,256,256]
        # distances to each palette color: [P,256,256]
        diff = lab[None, ...] - palette_lab[:, :, None, None]
        dist2 = (diff ** 2).sum(axis=1)
        idx = dist2.argmin(axis=0).astype(np.uint16)  # [256,256]
        result[r, :, :] = idx

    np.save(out_path, result)
    print(f"saved mapping to {out_path}; total {time.time() - t0:.1f}s")


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Prepare Lab-based RGB->palette colormap (saves colormap_lab.npy)")
    p.add_argument("--output", "-o", type=str, default="colormap_lab.npy", help="output .npy path (default colormap_lab.npy)")
    args = p.parse_args()
    main(args.output)
