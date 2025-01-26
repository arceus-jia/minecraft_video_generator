import os, sys, cv2
import argparse
import numpy as np
import time
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
    images = sorted(glob.glob(os.path.join(args.input,'*.jpg')))
    for i in range(len(images)):
        output = os.path.join(args.output,'frame_%03d.mcfunction'%(i+1) )
        x = args.x + i * args.width
        gen_single_image(images[i],output,x,args.y,args.z,args.width,args.height,args.pix,args.direction )

# python gen_with_video.py -x 0 -y -60 -z 0 --output /Users/arceus/Library/Application\ Support/minecraft/saves/sao/datapacks/test1/data/sao1/functions/ --width 228 --input ../../input/sao1/