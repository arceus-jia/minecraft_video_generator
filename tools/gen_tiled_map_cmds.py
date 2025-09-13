#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 /hexmap set 命令的小工具。

用法示例：

1) 256x256 从 (0,-60,0) 开始，2x2 拼图，地图ID从0开始顺序分配：
   python tools/gen_hexmap_commands.py \
     --world world --x0 0 --y0 -60 --z0 0 \
     --width 256 --height 256 \
     --start-id 0 --order row

2) 256x384 从 (0,-60,0) 开始，提供指定 ID 序列（6 张）：
   python tools/gen_hexmap_commands.py \
     --world world --x0 0 --y0 -60 --z0 0 \
     --width 256 --height 384 \
     --map-ids 0,1,2,3,4,5 --order row

参数说明：
- world/x0/y0/z0：区域起点；y0 是 6 层堆栈的基准 Y
- width/height：X/Z 的尺寸（单位：方块）
- tile：单张地图覆盖的尺寸（默认 128）
- map-ids：用逗号分隔的地图 ID 列表（与拼图块数一致）
- start-id：若不提供 map-ids，则按起始 ID 顺序分配（块数 = ceil(width/tile)*ceil(height/tile)）
- order：row（行优先：先 X 再 Z），或 col（列优先：先 Z 再 X）
- interval/radius：对应插件参数，默认 2/999

生成的每行形如：
  /hexmap set <id> <world> <x1> <y0> <z1> <x2> <z2> <interval> <radius>
注意 x2/z2 为“含端点”。
"""

import argparse
import math
from typing import List


def parse_ids(s: str) -> List[int]:
    return [int(x.strip()) for x in s.split(",") if x.strip()]


def gen_tiles(x0: int, z0: int, width: int, height: int, tile: int,
              order: str) -> List[tuple]:
    nx = math.ceil(width / tile)
    nz = math.ceil(height / tile)
    tiles = []
    if order == "row":
        # Z 行，从上到下；每行 X 从左到右
        for iz in range(nz):
            for ix in range(nx):
                x1 = x0 + ix * tile
                z1 = z0 + iz * tile
                x2 = min(x1 + tile - 1, x0 + width - 1)
                z2 = min(z1 + tile - 1, z0 + height - 1)
                tiles.append((x1, z1, x2, z2))
    else:  # col
        # X 列，从左到右；每列 Z 从上到下
        for ix in range(nx):
            for iz in range(nz):
                x1 = x0 + ix * tile
                z1 = z0 + iz * tile
                x2 = min(x1 + tile - 1, x0 + width - 1)
                z2 = min(z1 + tile - 1, z0 + height - 1)
                tiles.append((x1, z1, x2, z2))
    return tiles


def main():
    ap = argparse.ArgumentParser(description="Generate /hexmap set commands for tiling a region")
    ap.add_argument("--world", default="world")
    ap.add_argument("--x0", type=int, default=0)
    ap.add_argument("--y0", type=int, default=-60)
    ap.add_argument("--z0", type=int, default=0)
    ap.add_argument("--width", type=int, default=256)
    ap.add_argument("--height", type=int, default=256)
    ap.add_argument("--tile", type=int, default=128)
    ap.add_argument("--map-ids", type=str, default=None, help="comma-separated map ids, e.g. 0,1,3,4")
    ap.add_argument("--start-id", type=int, default=0, help="starting id if --map-ids not provided")
    ap.add_argument("--order", choices=["row", "col"], default="row")
    ap.add_argument("--interval", type=int, default=2)
    ap.add_argument("--radius", type=int, default=999)
    args = ap.parse_args()

    tiles = gen_tiles(args.x0, args.z0, args.width, args.height, args.tile, args.order)
    count = len(tiles)

    if args.map_ids:
        ids = parse_ids(args.map_ids)
        if len(ids) != count:
            raise SystemExit(f"map-ids 数量({len(ids)})与拼图块数({count})不一致")
    else:
        ids = list(range(args.start_id, args.start_id + count))

    for i, (x1, z1, x2, z2) in enumerate(tiles):
        mid = ids[i]
        cmd = f"/mapref set {mid} {args.world} {x1} {args.y0} {z1} {x2} {args.y0}  {z2} {args.interval} {args.radius}"
        print(cmd)


if __name__ == "__main__":
    main()

