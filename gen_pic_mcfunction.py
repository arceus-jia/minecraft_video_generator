import os, sys, cv2
import argparse
import numpy as np
import time

from cfg import blocks, colors
colormap = np.load("colormap.npy")


def resize(img, w,h, pixelate=False):
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
    return np.sum(np.abs(np.array(a)-np.array(b)))

def get_block(c):
    mn_dis = 10000
    block_color_idx = None

    for i in range(len(colors)):
        dis = manhattan(c, colors[i])
        if dis < mn_dis:
            mn_dis = dis
            block_color_idx = i
    return block_color_idx

# get_block_vec = np.vectorize(get_block)

def gen_cmd(x, y, z, color_idx):
    block = blocks[color_idx]
    str = f"setblock {x} {y} {z} {block} \n"
    return str

def preview(result_map):
    preview_image =colors[result_map].astype(np.uint8)
    cv2.imwrite('preview.jpg',preview_image)


def gen_single_image(input,output,x,y,z,width,height,pix,direction):
    img = cv2.imread(input)
    img = resize(img, width, height, pix)
    cv2.imwrite("resized.jpg", img)

    st = time.time()
    result_map = np.apply_along_axis(get_block, 2, img)
    print("cost==", time.time() - st)
    preview(result_map)

    sx = x
    sy = y
    sz = z

    result_arr = []
    h, w = result_map.shape
    for idx in range(h * w):
        i = int(idx / w)  # (i行 j列)
        j = idx % w
        # print (x,z)
        if direction == 'v':
            cmdstr = gen_cmd(sx + j, sy + h - i, sz, result_map[i][j])
        else:
            cmdstr = gen_cmd(sx + j, sy, sz+i, result_map[i][j])
        result_arr.append(cmdstr)

    if direction == 'v':
        print(f"fill {sx} {sy} {sz} {sx + w+1} {sy + h+1} {sz} minecraft:air")
    else:
        print(f"fill {sx} {sy} {sz} {sx + w+1} {sy} {sz+h+1} minecraft:air")

    with open(output, "w") as f:
        f.writelines(result_arr)    



parser = argparse.ArgumentParser(description="gen pics")

parser.add_argument("--input", type=str, help="input")
parser.add_argument("--output", type=str, help="output")
parser.add_argument("--width", "-w", type=int, help="w", )
parser.add_argument("--height", type=int, help="height", default=64)
parser.add_argument("--x", "-x", type=int, help="x")
parser.add_argument("--y", "-y", type=int, help="y")
parser.add_argument("--z", "-z", type=int, help="z")
parser.add_argument("--pix", "-p", action="store_true", help="pixelate or just resize")
parser.add_argument("--direction", "-d", type=str, help="direction",default='v')

args = parser.parse_args()


if __name__ == "__main__":
    # block = get_block([29,123,122])
    # print (block)
    gen_single_image(args.input,args.output,args.x,args.y,args.z,args.width,args.height,args.pix,args.direction)


# python gen_pic_mcfunction.py -x 0 -y -60 -z 0 --input input/pikachu/1.png --output  /Users/arceus/Desktop/mc/paper_1120/world/datapacks/test1/data/test1/functions/pic1.mcfunction
# fill 49 -60 208 178 -60 389 minecraft:air