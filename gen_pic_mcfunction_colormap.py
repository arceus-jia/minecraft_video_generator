import os, sys, cv2
import argparse
import numpy as np
import time

from cfg import blocks, colors
colormap = np.load("colormap.npy")

def resize(img, w, h, pixelate=False):
    height, width = img.shape[:2]
    if w:
        r = w / width
        h = round(height * r)
    if h:
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
        return len(blocks) - 1 #最后一位给空气
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


def gen_single_image(
    input_img, output, x, y, z, width, height, pix, direction, last_map=None
):
    # img = cv2.imread(input_img)

    img = cv2.imread(input_img,cv2.IMREAD_UNCHANGED)
    
    img = resize(img, width, height, pix)
    cv2.imwrite("resized.jpg", img)

    st = time.time()
    result_map = np.apply_along_axis(get_block, 2, img)

    visible_map = None
    if last_map is not None:
        visible_map = np.where(result_map == last_map, False, True)

    print("cost==", time.time() - st)
    # preview(result_map)

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
        elif direction == 'z':
            prev_x, prev_y, prev_z = sx, sy + h - prev_i, sz+prev_j
            if last_i is not None:
                last_x, last_y, last_z = sx, sy + h - last_i, sz+last_j       
        else:
            prev_x, prev_y, prev_z = sx + prev_j, sy, sz + prev_i
            if last_i is not None:
                last_x, last_y, last_z = sx + last_j, sy, sz + last_i
        cmdstr = gen_cmd2(prev_x, prev_y, prev_z, last_block, last_x, last_y, last_z)
        last_i, last_j, last_block = i, j, cur_block
        if is_skipping:
            last_block = -1

        result_arr.append(cmdstr)

    if direction == "v":
        print(f"fill {sx} {sy} {sz} {sx + w+1} {sy + h+1} {sz} minecraft:air")
    elif direction == 'z':
        print(f"fill {sx} {sy} {sz} {sx} {sy + h+1} {sz + w+1} minecraft:air")
    else:
        print(f"fill {sx} {sy} {sz} {sx + w+1} {sy} {sz+h+1} minecraft:air")

    with open(output, "w") as f:
        f.writelines(result_arr)

    return result_map


parser = argparse.ArgumentParser(description="gen pics")

parser.add_argument("--input", type=str, help="input")
parser.add_argument("--output", type=str, help="output")
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
parser.add_argument("--pix", "-p", action="store_true", help="pixelate or just resize")
parser.add_argument("--direction", "-d", type=str, help="direction", default="v")

args = parser.parse_args()


if __name__ == "__main__":
    # block = get_block([29,123,122])
    # print (block)
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
    )

# python gen_pic_mcfunction_colormap.py -x 0 -y -60 -z 0 --input input/1.png --output  /Users/arceus/Desktop/mc/paper_1120/world/datapacks/test1/data/test1/functions/pic1.mcfunction
# fill 0 -60 0 97 5 0 minecraft:air