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


# ---- sRGB -> CIE Lab helpers (D65) ----
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


# ---- CIEDE2000 ΔE implementation (vectorized) ----
def _ciede2000(lab_img: np.ndarray, lab_pal: np.ndarray) -> np.ndarray:
    """
    lab_img: [3, H, W]
    lab_pal: [P, 3]
    returns: ΔE00 for each palette color: [P, H, W]
    """
    L1, a1, b1 = lab_img[0], lab_img[1], lab_img[2]  # [H,W]
    L2 = lab_pal[:, 0][:, None, None]
    a2 = lab_pal[:, 1][:, None, None]
    b2 = lab_pal[:, 2][:, None, None]

    C1 = np.sqrt(a1**2 + b1**2)
    C2 = np.sqrt(a2**2 + b2**2)
    C_bar = (C1 + C2) / 2.0
    C_bar7 = C_bar**7
    G = 0.5 * (1.0 - np.sqrt(C_bar7 / (C_bar7 + 25.0**7)))

    a1p = (1 + G) * a1
    a2p = (1 + G) * a2
    C1p = np.sqrt(a1p**2 + b1**2)
    C2p = np.sqrt(a2p**2 + b2**2)

    h1p = np.degrees(np.arctan2(b1, a1p)) % 360.0
    h2p = np.degrees(np.arctan2(b2, a2p)) % 360.0

    dLp = L2 - L1
    dCp = C2p - C1p

    dhp = h2p - h1p
    dhp = np.where((C1p == 0) | (C2p == 0), 0.0, dhp)
    dhp = np.where(dhp > 180.0, dhp - 360.0, dhp)
    dhp = np.where(dhp < -180.0, dhp + 360.0, dhp)
    dHp = 2.0 * np.sqrt(C1p * C2p) * np.sin(np.radians(dhp) / 2.0)

    L_bar_p = (L1 + L2) / 2.0
    C_bar_p = (C1p + C2p) / 2.0

    # mean hue
    h_sum = h1p + h2p
    h_bar_p = np.where(
        (C1p == 0) | (C2p == 0),
        h_sum,  # value doesn't matter when chroma zero
        np.where(np.abs(h1p - h2p) > 180.0, (h_sum + 360.0) / 2.0, h_sum / 2.0),
    ) % 360.0

    T = (
        1
        - 0.17 * np.cos(np.radians(h_bar_p - 30.0))
        + 0.24 * np.cos(np.radians(2.0 * h_bar_p))
        + 0.32 * np.cos(np.radians(3.0 * h_bar_p + 6.0))
        - 0.20 * np.cos(np.radians(4.0 * h_bar_p - 63.0))
    )

    Sl = 1.0 + (0.015 * (L_bar_p - 50.0) ** 2) / np.sqrt(20.0 + (L_bar_p - 50.0) ** 2)
    Sc = 1.0 + 0.045 * C_bar_p
    Sh = 1.0 + 0.015 * C_bar_p * T

    delta_theta = 30.0 * np.exp(-(((h_bar_p - 275.0) / 25.0) ** 2))
    Rc = 2.0 * np.sqrt((C_bar_p ** 7) / (C_bar_p ** 7 + 25.0 ** 7))
    Rt = -Rc * np.sin(np.radians(2.0 * delta_theta))

    kL = kC = kH = 1.0
    termL = dLp / (kL * Sl)
    termC = dCp / (kC * Sc)
    termH = dHp / (kH * Sh)

    dE = np.sqrt(termL**2 + termC**2 + termH**2 + Rt * termC * termH)
    return dE


def main(out_path: str = "colormap_lab2000.npy"):
    pal = np.asarray(colors[:-1], dtype=np.float32)  # exclude air
    pr, pg, pb = pal[:, 0], pal[:, 1], pal[:, 2]
    pL, pA, pB = rgb_to_lab_array(pr, pg, pb)
    palette_lab = np.stack([pL, pA, pB], axis=1).astype(np.float32)

    result = np.empty((256, 256, 256), dtype=np.uint16)

    g_grid, b_grid = np.mgrid[0:256, 0:256].astype(np.float32)

    t0 = time.time()
    for r in range(256):
        if r % 8 == 0:
            print(f"slice {r}/255 elapsed={time.time() - t0:.1f}s")
        r_plane = np.full_like(g_grid, float(r))
        L, A, B = rgb_to_lab_array(r_plane, g_grid, b_grid)
        lab_img = np.stack([L, A, B], axis=0).astype(np.float32)
        dist = _ciede2000(lab_img, palette_lab)  # [P,256,256]
        idx = dist.argmin(axis=0).astype(np.uint16)
        result[r, :, :] = idx

    np.save(out_path, result)
    print(f"saved mapping to {out_path}; total {time.time() - t0:.1f}s")


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Prepare CIEDE2000-based RGB->palette colormap (saves colormap_lab2000.npy)")
    p.add_argument("--output", "-o", type=str, default="colormap_lab2000.npy", help="output .npy path (default colormap_lab2000.npy)")
    args = p.parse_args()
    main(args.output)

