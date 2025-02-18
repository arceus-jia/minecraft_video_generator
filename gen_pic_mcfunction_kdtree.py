import os, sys, cv2
import argparse
import numpy as np
import time

from cfg import blocks, colors
colormap = np.load("colormap.npy")


def partition(arr, l=0, r=None, cmp=None):
    if not cmp:
        cmp = lambda x, y: x - y
    r = r or len(arr) - 1
    pivot_idx = l
    left = l + 1
    right = r
    while True:
        while left <= right and cmp(arr[pivot_idx], arr[left]) > 0:
            left += 1
        while left <= right and cmp(arr[pivot_idx], arr[right]) <= 0:
            right -= 1
        if right < left:
            break
        arr[left], arr[right] = arr[right], arr[left]

    arr[l], arr[right] = arr[right], arr[l]
    return right


def nth_element(arr, nth, l=0, r=None, cmp=None):
    pivot_idx = partition(arr, l, r, cmp)
    if pivot_idx == nth:
        return
    if pivot_idx > nth:
        return nth_element(arr, nth, l, pivot_idx, cmp)
    return nth_element(arr, nth, pivot_idx + 1, r, cmp)


class Node(object):
    def __init__(self, coord, idx=None) -> None:
        self.coord = coord
        self.idx = idx


class KDTree(object):
    def __init__(self, mat):
        n, k = mat.shape

        self.nodes = []
        self.n = n
        self.k = k
        for i in range(n):
            self.nodes.append(Node(mat[i], i))

        self.dims = [0] * n  # dims[i] i点由第几维划分
        self.result = {"dis": 1e5, "node": Node([0, 0, 0])}

    def compare_dim(self, dim):
        return lambda a, b: a.coord[dim] - b.coord[dim]

    def build(self, l, r, depth):  # l:0, r:n-1 左闭右闭
        if l > r:
            return
        mid = (l + r) >> 1
        dim = depth % self.k
        self.dims[mid] = dim
        nth_element(self.nodes, mid, l, r, self.compare_dim(dim))
        self.build(l, mid - 1, depth + 1)
        self.build(mid + 1, r, depth + 1)

    def manhattan(self, a: Node, b: Node):
        return np.sum(np.abs(a.coord - b.coord))

    def query(self, l, r, t: Node = None):
        if l > r:
            return
        mid = l + r >> 1
        mid_dim = self.dims[mid]
        mid_node = self.nodes[mid]
        dis = self.manhattan(t, mid_node)
        if self.result["dis"] > dis:
            self.result = {"dis": dis, "node": mid_node}
        d_to_mid = t.coord[mid_dim] - mid_node.coord[mid_dim]
        l1, r1, l2, r2 = l, mid - 1, mid + 1, r
        if d_to_mid > 0:
            l1, r1, l2, r2 = l2, r2, l1, r1
        self.query(l1, r1, t)  # t所在的一半查询
        if d_to_mid < self.result["dis"]:
            self.query(l2, r2, t)

    def get_block(self, t):
        self.result = {"dis": 1e5, "node": Node([0, 0, 0])}
        t = Node(t)
        self.query(0, self.n - 1, t)
        return self.result["node"].idx

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
    return np.sum(np.abs(np.array(a) - np.array(b)))


def gen_cmd(x, y, z, color_idx):
    block = blocks[color_idx]
    str = f"setblock {x} {y} {z} {block} \n"
    return str


def preview(result_map):
    preview_image = colors[result_map].astype(np.uint8)
    cv2.imwrite("preview.jpg", preview_image)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="gen pics")

    parser.add_argument("--input", type=str, help="input")
    parser.add_argument("--output", type=str, help="output")
    parser.add_argument("--width", "-w", type=int, help="w")
    parser.add_argument("--height", type=int, help="h", default=64)
    parser.add_argument("--x", "-x", type=int, help="x")
    parser.add_argument("--y", "-y", type=int, help="y")
    parser.add_argument("--z", "-z", type=int, help="z")
    parser.add_argument("--pix", "-p", action="store_true", help="pixelate or just resize")
    parser.add_argument("--direction", "-d", type=str, help="direction", default="v")

    args = parser.parse_args()    
    # a = np.array([0, 4, 3, 2, 1, 1, 5])
    # nth_element(a, 5, 2, 6)
    # print(a)
    n = len(colors)
    kdtree = KDTree(colors)
    st = time.time()
    kdtree.build(0, len(colors) - 1, 0)
    print('build...',time.time()-st)

    img = cv2.imread(args.input)
    img = resize(img, args.width, args.height, args.pix)

    cv2.imwrite("resized.jpg", img)

    st = time.time()
    result_map = np.apply_along_axis(kdtree.get_block, 2, img)
    print("cost==", time.time() - st)
    preview(result_map)

    sx = args.x
    sy = args.y
    sz = args.z

    result_arr = []
    h, w = result_map.shape
    for idx in range(h * w):
        i = int(idx / w)  # (i行 j列)
        j = idx % w
        # print (x,z)
        if args.direction == 'v':
            cmdstr = gen_cmd(sx + j, sy + h - i, sz, result_map[i][j])
        else:
            cmdstr = gen_cmd(sx + j, sy, sz+h-i, result_map[i][j])
        result_arr.append(cmdstr)

    if args.direction == 'v':
        print(f"fill {sx} {sy} {sz} {sx + w+1} {sy + h+1} {sz} minecraft:air")
    else:
        print(f"fill {sx} {sy} {sz} {sx + w+1} {sy} {sz+h+1} minecraft:air")

    with open(args.output, "w") as f:
        f.writelines(result_arr)