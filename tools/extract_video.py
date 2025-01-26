import cv2
import os, sys, argparse
import subprocess
from PIL import Image
import numpy as np

parser = argparse.ArgumentParser(description="gen pics")

parser.add_argument("--input", type=str, help="input")
parser.add_argument("--output", type=str, help="output")
parser.add_argument("--skip", type=int, default=0, help="skip")
parser.add_argument("--max-cnt", type=int, default=24, help="max cnt")

args = parser.parse_args()

input = args.input
output = args.output
skip = args.skip
max_cnt = args.max_cnt

def get_video_rotation(file_path):
    cmd = f"ffprobe -v error -select_streams v:0 -show_entries stream_tags=rotate -of default=noprint_wrappers=1:nokey=1 {file_path}"
    try:
        rotation = subprocess.check_output(cmd, shell=True).decode().strip()
        print('rotation',rotation)
        rotation = int(rotation)
    except:
        rotation = 0
    return rotation

def rotate_image(image, angle):
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h))
    return rotated

def rotate_image_pil(image, angle):
    """
    使用 PIL 旋转图像。
    """
    pil_image = Image.fromarray(image)
    rotated_image = pil_image.rotate(angle, expand=True)
    return np.array(rotated_image)

if __name__ == "__main__":
    os.makedirs(output, exist_ok=True)

    cap = cv2.VideoCapture(input)
    rotation_angle = get_video_rotation(input)

    result_imgs = []
    idx = 1
    while True:
        print("idx...", idx)
        if idx > max_cnt:
            break
        success, img = cap.read()
        if not success:
            break
        if img is None:
            continue
        if skip > 0 and idx % (skip + 1) != 1:
            idx += 1
            continue
        if rotation_angle:
            img = rotate_image_pil(img, -rotation_angle)        
        cv2.imwrite(os.path.join(output, "%05d.jpg" % idx), img)
        idx += 1

#  python tools/extract_video.py --input input/sao10.mp4 --output output/sao10 --skip 2 --max-cnt 240