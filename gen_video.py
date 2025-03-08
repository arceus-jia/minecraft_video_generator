import os, sys, cv2
import argparse
import numpy as np
import time

# from gen_pic_mcfunction import gen_single_image
from gen_pic_mcfunction_colormap import gen_single_image
import glob

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="gen pics")

    parser.add_argument("--input", type=str, help="input")
    parser.add_argument("--output", type=str, help="output")
    parser.add_argument("--datapack_name", "-n", type=str, help="datapackname")
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
    parser.add_argument("--ticks", "-t", type=int, help="ticks", default=4)

    args = parser.parse_args()

    output_dir = os.path.join(args.output, args.datapack_name, "functions")
    os.makedirs(output_dir, exist_ok=True)
    images = sorted(
        glob.glob(os.path.join(args.input, "*.jpg"))
        + glob.glob(os.path.join(args.input, "*.png"))
    )
    last_map = None

    run_cmd_arr = [f"function {args.datapack_name}:frame_0001\n"]
    run_func_path = os.path.join(output_dir, "run.mcfunction")
    for i in range(len(images)):
        print("generate frame::", i + 1)
        func_name = "frame_%04d" % (i + 1)
        if i >= 1:
            run_cmd_arr.append(
                f"schedule function {args.datapack_name}:{func_name} {i*args.ticks}t\n"
            )
        output = os.path.join(output_dir, func_name + ".mcfunction")
        x = args.x
        clear_output = (
            os.path.join(output_dir, "clear.mcfunction")
            if i == len(images) - 1
            else None
        )

        last_map = gen_single_image(
            images[i],
            output,
            x,
            args.y,
            args.z,
            args.width,
            args.height,
            args.pix,
            args.direction,
            last_map,
            clear_output,
        )

    run_cmd_arr.append(
        f"schedule function {args.datapack_name}:run {len(images) * args.ticks}t"
    )

    with open(run_func_path, "w") as f:
        f.writelines(run_cmd_arr)

# python gen_video.py -x 0 -y -60 -z 0 --output /Users/arceus/Desktop/mc/paper_1120/world/datapacks/test1/data/ -n sao0 --width 228 --input ../../input/sao1/

# python gen_video.py -x 0 -y -60 -z 0 --input input/pikachu/ --output  /Users/arceus/Desktop/mc/paper_1120/world/datapacks/test1/data/ -n pikachu -d h

# python gen_video.py -x 0 -y -60 -z 0 --input input/pikachu/ --output /Users/arceus/Library/Application\ Support/minecraft/saves/test001/datapacks/test1/data -n pikachu -d v

# tp 114 4 100
# schedule clear pikachu:run