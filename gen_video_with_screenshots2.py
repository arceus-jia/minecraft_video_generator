#配合位移

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

# tp wangguanguan 160 -59 206 180 0
# tp wangguanguan 160 23 126 180 0


sleep1 = 0.6
sleep2 = 0.3

if __name__ == "__main__":
    mcr = MCRcon(HOST, PASSWD)
    mcr.connect()
    time.sleep(5)
    screenshot(0)

    y = -59
    z = 203

    cur = 1
    step1 = 42
    #step1
    for i in range(cur, cur + step1 + 1):
        print('handle===',i)
        cmd = "function %s:frame_%04d" % (args.func, i)
        resp = mcr.command(cmd)
        cmd = 'tp wangguanguan 160 %d 206 180 0' % y
        resp = mcr.command(cmd)
        time.sleep(sleep1)  # waiting for render
        screenshot(i)
        time.sleep(sleep2)  # waiting for screenshots
        y = y + 2
    cur = cur + step1 + 1

    step2 = 40
    #step2
    for i in range(cur, cur + step2 + 1):
        print('handle===',i)
        cmd = "function %s:frame_%04d" % (args.func, i)
        resp = mcr.command(cmd)
        cmd = 'tp wangguanguan 160 23 %d 180 0' % z
        resp = mcr.command(cmd)
        time.sleep(sleep1)  # waiting for render
        screenshot(i)
        time.sleep(sleep2)  # waiting for screenshots
        z = z - 2
    
    cur = cur + step2 + 1

    for i in range(cur, args.frame_cnt + 1):
        print('handle===',i)
        cmd = "function %s:frame_%04d" % (args.func, i)
        resp = mcr.command(cmd)
        time.sleep(sleep1)  # waiting for render
        screenshot(i)
        time.sleep(sleep2)  # waiting for screenshots
