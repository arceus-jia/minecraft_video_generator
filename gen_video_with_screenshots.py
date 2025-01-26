from mcrcon import MCRcon
import sys, os, time
import argparse
from mss import mss
from PIL import Image

HOST = "127.0.0.1"
PORT = 25575
PASSWD = "123456"
COMMAND = "status"

parser = argparse.ArgumentParser(description="gen video")
parser.add_argument("--func", type=str, default="sao10", help="funcname")
parser.add_argument("--output", type=str, help="output folder")
parser.add_argument("--frame-cnt", type=int, help="frame count")
parser.add_argument("--width", type=int,default=960, help="frame count")

args = parser.parse_args()

os.makedirs(args.output,exist_ok=True)

def screenshot(idx):
    with mss() as sct:
        # sct.shot(output=os.path.join(args.output, "%04d.jpg" % idx))
        sct_img = sct.shot()
        img = Image.open(sct_img)
        resized_img = img.resize((1080, int(img.height * 1080/img.width)))
        resized_img.save(os.path.join(args.output, "%04d.jpg" % idx))

if __name__ == "__main__":
    mcr = MCRcon(HOST, PASSWD)
    mcr.connect()
    time.sleep(5)
    screenshot(0)
    for i in range(1, args.frame_cnt + 1):
        print('handle===',i)
        cmd = "function %s:frame_%04d" % (args.func, i)
        resp = mcr.command(cmd)
        time.sleep(0.8)  # waiting for render
        screenshot(i)
        time.sleep(0.3)  # waiting for screenshots
