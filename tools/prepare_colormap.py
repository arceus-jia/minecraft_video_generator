import os, sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
import argparse
import numpy as np
import time

# from gen_pic_mcfunction import gen_single_image
import glob
from queue import Queue
from cfg import colors

result = np.zeros([256, 256, 256]).astype(np.uint8)

directions = [[0, 0, 1], [0, 0, -1], [0, 1, 0], [0, -1, 0], [1, 0, 0], [-1, 0, 0]]
cnt = 0

q = Queue()
for i in range(len(colors)):
    q.put(colors[i])
    result[colors[i][0], colors[i][1], colors[i][2]] = i + 1
    cnt += 1


def is_valid(pt):
    for x in pt:
        if x < 0 or x > 255:
            return False
    return True


st = time.time()
while cnt < 256 * 256 * 256:
    print("cnt..", cnt)
    temp_q = Queue()
    while not q.empty():
        pt = q.get()
        color_idx = result[pt[0], pt[1], pt[2]]
        for dir in directions:
            pt_new = pt + dir
            if not is_valid(pt_new):
                continue
            if result[pt_new[0], pt_new[1], pt_new[2]]:
                continue
            temp_q.put(pt_new)
            result[pt_new[0], pt_new[1], pt_new[2]] = color_idx
            cnt += 1
    q = temp_q
print("cost..", time.time() - st)

np.save("colormap.npy", result - 1)
