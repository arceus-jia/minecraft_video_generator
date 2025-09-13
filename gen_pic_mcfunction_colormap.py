import os, sys, cv2
import argparse
import numpy as np
import time
import math

from cfg import blocks, colors

colormap = np.load("colormap.npy")


def resize(img, w, h, pixelate=False):
    height, width = img.shape[:2]
    if w and h is None:
        r = w / width
        h = round(height * r)
    elif h and w is None:
        r = h / height
        w = round(width * r)

    if pixelate:
        temp = cv2.resize(img, (w // 3, h // 3), interpolation=cv2.INTER_LINEAR)
        temp = cv2.resize(temp, (w, h), interpolation=cv2.INTER_NEAREST)
    else:
        temp = cv2.resize(img, (w, h), interpolation=cv2.INTER_LINEAR)
    return temp


def manhattan(a, b):
    return np.sum(np.abs(np.array(a) - np.array(b)))


def get_block(c):
    if len(c) == 4 and c[3] < 128:
        return len(blocks) - 1  # 最后一位给空气
    return colormap[c[0], c[1], c[2]]


def gen_cmd(x, y, z, color_idx):
    block = blocks[color_idx]
    str = f"setblock {x} {y} {z} {block} \n"
    return str


def gen_cmd2(x, y, z, color_idx, last_x=None, last_y=None, last_z=None):
    block = blocks[color_idx]
    if last_x is None or abs(x - last_x) + abs(y - last_y) + abs(z - last_z) == 0:
        str = f"setblock {x} {y} {z} {block} \n"
    else:
        str = f"fill {last_x} {last_y} {last_z} {x} {y} {z} {block} \n"
    return str


def preview(result_map):
    preview_image = colors[result_map].astype(np.uint8)
    cv2.imwrite("preview.jpg", preview_image)

def make_clear_commands(direction: str, sx: int, sy: int, sz: int, w: int, h: int, max_blocks: int = 32768) -> list:
    """
    Generate chunked clear commands for the rendered rectangle, depending on direction:
      - direction 'v': plane X×Y at fixed Z (thickness 1)
      - direction 'z': plane Z×Y at fixed X (thickness 1)
      - otherwise   : plane X×Z at fixed Y (thickness 1)
    """
    w = int(w); h = int(h)
    if w <= 0 or h <= 0:
        return []
    # 2D area with thickness 1
    max_area = max(1, max_blocks)  # thickness is 1 block
    base = max(1, int(math.isqrt(max_area)))
    tile_w = min(w, base)
    tile_h = min(h, max(1, max_area // tile_w))
    cmds = []
    for xi in range(0, w, tile_w):
        cur_w = min(tile_w, w - xi)
        cur_tile_h = min(tile_h, max(1, max_area // cur_w))
        for zi in range(0, h, cur_tile_h):
            cur_h = min(cur_tile_h, h - zi)
            if direction == "v":
                x0, x1 = sx + xi, sx + xi + cur_w - 1
                y0, y1 = sy + zi, sy + zi + cur_h - 1
                z0 = z1 = sz
            elif direction == "z":
                x0 = x1 = sx
                y0, y1 = sy + zi, sy + zi + cur_h - 1
                z0, z1 = sz + xi, sz + xi + cur_w - 1
            else:
                x0, x1 = sx + xi, sx + xi + cur_w - 1
                y0 = y1 = sy
                z0, z1 = sz + zi, sz + zi + cur_h - 1
            cmds.append(f"fill {x0} {y0} {z0} {x1} {y1} {z1} minecraft:air")
    return cmds


def write_clear(direction: str, output_path: str, sx: int, sy: int, sz: int, w: int, h: int, max_blocks: int = 32768):
    cmds = make_clear_commands(direction, sx, sy, sz, w, h, max_blocks)
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            f.write("\n".join(cmds))
    for c in cmds:
        print(c)


# 4x4 Bayer matrix for ordered dithering (values 0..15)
BAYER4 = np.array([
    [0, 8, 2, 10],
    [12, 4, 14, 6],
    [3, 11, 1, 9],
    [15, 7, 13, 5],
], dtype=np.float32)


def apply_ordered4_dither(img: np.ndarray, amount: float) -> np.ndarray:
    """Apply 4x4 ordered dithering on BGR(A) image. Alpha channel preserved.
    amount is roughly in 0..16 typical range.
    """
    if img.ndim != 3 or img.shape[2] < 3:
        return img
    h, w = img.shape[:2]
    # Build tiled threshold map in range [-0.5, 0.5)
    t = BAYER4 / 16.0 - 0.5
    tile = np.tile(t, (int(np.ceil(h / 4)), int(np.ceil(w / 4))))[:h, :w]
    off = (amount * tile).astype(np.float32)

    out = img.copy().astype(np.float32)
    # Add to B,G,R channels only
    out[:, :, 0] = np.clip(np.rint(out[:, :, 0] + off), 0, 255)
    out[:, :, 1] = np.clip(np.rint(out[:, :, 1] + off), 0, 255)
    out[:, :, 2] = np.clip(np.rint(out[:, :, 2] + off), 0, 255)
    return out.astype(np.uint8)


def gen_single_image(
    input_img,
    output,
    x,
    y,
    z,
    width,
    height,
    pix,
    direction,
    last_map=None,
    clear_output=None,
    dither: str = "none",
    dither_amount: float = 12.0,
):
    # img = cv2.imread(input_img)

    os.makedirs(os.path.dirname(output), exist_ok=True)

    img = cv2.imread(input_img, cv2.IMREAD_UNCHANGED)

    img = resize(img, width, height, pix)
    cv2.imwrite("resized.jpg", img)

    # Apply ordered dithering if requested (before lookup)
    if dither == "ordered4":
        img = apply_ordered4_dither(img, float(dither_amount))

    st = time.time()
    # Lazy-load default colormap if not preset by caller (prefer OKLab)
    if 'colormap' not in globals():
        try:
            globals()['colormap'] = np.load('colormap_oklab.npy')
            print('loaded colormap_oklab.npy (default)')
        except Exception:
            try:
                globals()['colormap'] = np.load('colormap.npy')
                print('loaded colormap.npy (fallback)')
            except Exception as e:
                raise RuntimeError(f'No colormap loaded and failed to load defaults: {e}')
    result_map = np.apply_along_axis(get_block, 2, img)

    visible_map = None
    if last_map is not None:
        visible_map = np.where(result_map == last_map, False, True)

    print("cost==", time.time() - st)
    preview(result_map)

    sx = x
    sy = y
    sz = z

    result_arr = []
    h, w = result_map.shape

    for idx in range(h * w + 1):
        if idx == 0:
            last_i, last_j, last_block = 0, 0, result_map[0][0]
            is_skipping = False
            continue

        i = int(idx / w)  # (i行 j列)
        j = idx % w

        # if i < h and visible_map is not None and visible_map[i][j] == False:
        #     last_i,last_j,last_block = i,j,result_map[i][j]
        #     continue

        if i == h:
            cur_block = None
        else:
            cur_block = result_map[i][j]

        skip = idx != h * w and visible_map is not None and visible_map[i][j] == False

        if i == last_i and cur_block == last_block:
            continue

        if skip:
            if is_skipping:
                continue
            is_skipping = True
        else:
            if is_skipping:
                is_skipping = False
                if idx == h * w:
                    continue
                last_i, last_j, last_block = i, j, result_map[i][j]
                continue

        # 优化，同一行相同的用fill
        if i != last_i:
            prev_i = i - 1
            prev_j = w - 1
        else:
            prev_i = i
            prev_j = j - 1

        if direction == "v":
            prev_x, prev_y, prev_z = sx + prev_j, sy + h - prev_i, sz
            if last_i is not None:
                last_x, last_y, last_z = sx + last_j, sy + h - last_i, sz
        elif direction == "z":
            prev_x, prev_y, prev_z = sx, sy + h - prev_i, sz + prev_j
            if last_i is not None:
                last_x, last_y, last_z = sx, sy + h - last_i, sz + last_j
        else:
            prev_x, prev_y, prev_z = sx + prev_j, sy, sz + prev_i
            if last_i is not None:
                last_x, last_y, last_z = sx + last_j, sy, sz + last_i
        cmdstr = gen_cmd2(prev_x, prev_y, prev_z, last_block, last_x, last_y, last_z)
        last_i, last_j, last_block = i, j, cur_block
        if is_skipping:
            last_block = -1

        result_arr.append(cmdstr)

    # 分段 clear（避免单条 fill 过大）
    if clear_output is not None:
        write_clear(direction, clear_output, sx, sy, sz, w, h, 32768)

    with open(output, "w") as f:
        f.writelines(result_arr)

    return result_map


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="gen pics")

    parser.add_argument("--input", type=str, help="input")
    parser.add_argument("--output", type=str, help="output (file or datapack data/ when -n is used)")
    parser.add_argument(
        "--width",
        "-w",
        type=int,
        help="w",
    )
    parser.add_argument("--height", type=int, help="height", default=64)
    parser.add_argument("--x", "-x", type=int, help="x")
    parser.add_argument("--y", "-y", type=int, help="y")
    parser.add_argument("--z", "-z", type=int, help="z")
    parser.add_argument(
        "--pix", "-p", action="store_true", help="pixelate or just resize"
    )
    parser.add_argument("--direction", "-d", type=str, help="direction", default="v")
    parser.add_argument("--mode", type=str, choices=["rgb", "lab", "lab2000","oklab"], default="oklab", help="colormap mode: rgb=colormap.npy, lab=colormap_lab.npy, lab2000=colormap_lab2000.npy")
    parser.add_argument("--namespace", "-n", type=str, default=None, help="datapack namespace; when set, write run.mcfunction and clear.mcfunction under <output>/<ns>/function/")
    parser.add_argument("--dither", type=str, choices=["none", "ordered4"], default="ordered4", help="dithering: none or ordered4 (Bayer 4x4)")
    parser.add_argument("--dither-amount", type=float, default=12.0, help="dither strength for ordered4 (typical 8-16)")
    parser.add_argument("--clear-output", type=str, default=None, help="single-file mode: optional path to write clear mcfunction")

    args = parser.parse_args()

    # Load colormap by mode
    try:
        colormap_path = {
            "rgb": "colormap.npy",
            "lab": "colormap_lab.npy",
            "lab2000": "colormap_lab2000.npy",
            "oklab": "colormap_oklab.npy",
        }[args.mode]
        globals()["colormap"] = np.load(colormap_path)
        print(f"loaded {colormap_path}")
    except Exception as e:
        raise RuntimeError(f"Failed to load colormap file for mode={args.mode}: {e}")

    # block = get_block([29,123,122])
    # print (block)
    ns = args.namespace
    if ns is None:
        # 单文件模式
        gen_single_image(
            args.input,
            args.output,
            args.x,
            args.y,
            args.z,
            args.width,
            args.height,
            args.pix,
            args.direction,
            clear_output=args.clear_output,
            dither=args.dither,
            dither_amount=args.dither_amount,
        )
    else:
        # 数据包模式：写入 <data>/<ns>/function/run.mcfunction 和 clear.mcfunction
        func_dir = os.path.join(args.output, ns, "function")
        os.makedirs(func_dir, exist_ok=True)
        run_path = os.path.join(func_dir, "run.mcfunction")
        clear_path = os.path.join(func_dir, "clear.mcfunction")
        gen_single_image(
            args.input,
            run_path,
            args.x,
            args.y,
            args.z,
            args.width,
            args.height,
            args.pix,
            args.direction,
            clear_output=clear_path,
            dither=args.dither,
            dither_amount=args.dither_amount,
        )
        print(f"wrote run.mcfunction: {run_path}")
        print(f"wrote clear.mcfunction: {clear_path}")

# python gen_pic_mcfunction_colormap.py -x 0 -y -60 -z 0 --input input/1.png --output  /Users/arceus/Desktop/mc/paper_1120/world/datapacks/test1/data/test1/function/pic1.mcfunction
# fill 0 -60 0 97 5 0 minecraft:air
# python gen_pic_mcfunction_colormap.py --output ~/Desktop/mc/paper_1121/world/datapacks/test2/data/ -n asuna -x 0 -y -60 -z 0 --width 256 --input input/asuna.jpg -d h --height 384
# mapref set 0,1,2,3,4,5 world 0 -60 0 255 -60 383 2 3 2 999