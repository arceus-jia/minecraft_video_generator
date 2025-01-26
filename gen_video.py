import os, sys, cv2
import argparse
import numpy as np
import time
# from gen_pic_mcfunction import gen_single_image
from gen_pic_mcfunction_colormap import gen_single_image
import glob

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


if __name__ == '__main__':
    os.makedirs(args.output, exist_ok=True)
    images = sorted(glob.glob(os.path.join(args.input,'*.jpg')) + glob.glob(os.path.join(args.input,'*.png')))
    last_map = None
    for i in range(len(images)):
        print('generate frame::',i+1)
        output = os.path.join(args.output,'frame_%04d.mcfunction'%(i+1) )
        x = args.x
        last_map = gen_single_image(images[i],output,x,args.y,args.z,args.width,args.height,args.pix,args.direction,last_map)

# python gen_video.py -x 0 -y -60 -z 0 --output /Users/arceus/Desktop/mc/paper_1120/world/datapacks/test1/data/sao0/functions/  --width 228 --input ../../input/sao1/

# python gen_video.py -x 0 -y -60 -z 0 --input input/pikachu/ --output  /Users/arceus/Desktop/mc/paper_1120/world/datapacks/test1/data/test1/functions/ -d h

#tp 114 4 100