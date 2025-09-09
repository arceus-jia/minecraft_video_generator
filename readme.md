### README.md (English Version)

# MC Video Generator

[中文版本](readme.zh.md)

## Overview
A script for transferring videos into Minecraft. It can also be used to create map art, dynamic structures, and more.

### Example Effects
https://github.com/user-attachments/assets/70876711-58ec-4d90-a9a9-1ea949773a22

https://github.com/user-attachments/assets/51e89451-bb36-4573-84a6-07e958b9ae9f

---

## Environment Setup
```bash
conda create -n mvg python=3.10
conda activate mvg
pip install -r requirements.txt

#or
python3 -m venv mvg
source ./mvg/bin/activate
pip install -r requirements.txt
```

---

## Single Image to Minecraft Commands
```bash
python gen_pic_mcfunction_colormap.py \
-x 0 -y -60 -z 0 -d v --height 64\
--input input/pikachu/1.png \
--output ~/Library/Application\ Support/minecraft/saves/test001/datapacks/mvg/data/test1/function/pic1.mcfunction \
##Note that before 1.21, the path was functions instead of function.
```

### Parameter Description
- `x`, `y`, `z`: Starting coordinates
- `d`: Direction (`v` for vertical, `h` for horizontal)
- `--width`, `--height`, : width or heigth (will scale proportionally. Setting one is enough.)

### Notes
- For multi-image generation, the version that preprocesses the colormap is the most efficient. For single images, you can also use `gen_pic_mcfunction.py` or `gen_pic_mcfunction_kdtree.py`.
- Use `cfg.py` to configure the block-to-color mappings. The `gen_pic_mcfunction_colormap` script requires running `prepare_colormap` to regenerate the colormap.
- `kdtree` and native versions do not require colormap preparation.

---

## Video to Minecraft Commands
```bash
python gen_video.py \
-x 0 -y -60 -z 0 -d v --height 64 \
--input input/pikachu/ \
--output /Users/arceus/Desktop/mc/paper_1120/world/datapacks/test1/data \
-n pikachu \
-t 4
```

### Parameter Description
- `x`, `y`, `z`: Starting coordinates
- `d`: Direction (`v` for vertical, `h` for horizontal)
- `n`: Package Name
- `t`: ticks (1s = 20 ticks)
- `--width`, `--height`, : width or heigth (will scale proportionally. Setting one is enough.)

---

## Playing Videos in Minecraft
### local game (run in mc console)
```mcfunction
function pikachu:run
```

### server 
```bash
python play.py -f test1 -c 9 -i 0.1
```

---

## Video Synthesis
```bash
python gen_video_with_screenshots.py \
--func sao10 \
--output ./output/mc_sao10/ --frame-cnt 1429
```

---
