import cv2
import os, sys, argparse
import av
from moviepy.editor import VideoFileClip
import shutil
import glob
import numpy as np
import uuid

def create_hd_video(imgs, filename, fps=24, audio=None):
    h, w, l = imgs[0].shape
    print('lenimags', imgs[0].dtype, imgs[0].shape, len(imgs))

    container = av.open(filename, mode='w')
    stream = container.add_stream('h264', rate=fps)
    stream.width = w
    stream.height = h
    stream.pix_fmt = 'yuv420p'
    stream.bit_rate = 10000000   
    stream.options["crf"] = "18" 
    for img in imgs:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.uint8)
        frame = av.VideoFrame.from_ndarray(img, format='rgb24')
        container.mux(stream.encode(frame))
    container.mux(stream.encode())
    container.close()

    duration = len(imgs) / fps
    if audio:
        final_video = VideoFileClip(filename)            
        if duration and audio.duration > duration:            
            print ('clip audio',duration,audio.duration)    
            clip_audio = audio.subclip(0,duration)
            final_video = final_video.set_audio(clip_audio)                
        else:
            final_video = final_video.set_audio(audio)
        tmp_file = f'/tmp/{str( uuid.uuid4())}.mp4'
        final_video.write_videofile(tmp_file, audio_codec='aac')
        final_video.close()
        shutil.move(tmp_file, filename)
    return filename

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="gen pics")

    parser.add_argument("--input", type=str, help="input")
    parser.add_argument("--output", type=str, help="output")
    parser.add_argument("--fps", type=int, default=8, help="fps")
    # parser.add_argument("--max-cnt", type=int, default=24, help="max cnt")

    args = parser.parse_args()

    input = args.input
    output = args.output

    imgs = sorted(glob.glob(os.path.join(args.input,'*.jpg')))
    print('imgs...',len(imgs))
    imgs = [cv2.imread(i) for i in imgs]
    create_hd_video(imgs, args.output,args.fps)