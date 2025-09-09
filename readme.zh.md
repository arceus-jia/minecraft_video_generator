### README_zh.md (中文版本)

# MC 视频生成器

[English Version](readme.md)

## 概述
一个将视频搬进 Minecraft 的脚本。亦可以用于制作地图画、动态建筑物等。

### 效果参考
https://github.com/user-attachments/assets/70876711-58ec-4d90-a9a9-1ea949773a22

https://github.com/user-attachments/assets/51e89451-bb36-4573-84a6-07e958b9ae9f

---

## 环境
```bash
conda create -n mvg python=3.10
conda activate mvg
pip install -r requirements.txt

#或者
python3 -m venv mvg
source ./mvg/bin/activate
pip install -r requirements.txt
```

---

## 单图转命令
```bash
python gen_pic_mcfunction_colormap.py \
-x 0 -y -60 -z 0 -d v --height 64 \
--input input/pikachu/1.png \
--output ~/Library/Application\ Support/minecraft/saves/test001/datapacks/mvg/data/test1/function/pic1.mcfunction
#注意1.21之前是路径中是functions不是function 
```

### 参数说明
- `x`, `y`, `z`: 起始坐标
- `d`: 方向 (`v` 或者 `h`)
- `--width`, `--height`, : 宽高(会自动缩放，设置一个就够了)

### 注意
- 多图生成中，提前处理 colormap 的版本效率最高。对于单图，也可以使用 `gen_pic_mcfunction.py` 或者 `gen_pic_mcfunction_kdtree.py`。
- 可以使用 `cfg.py` 配置方块对应颜色。`gen_pic_mcfunction_colormap` 需要通过 `prepare_colormap` 重新生成 colormap。
- `kdtree` 或者原生版本不需要提前处理 colormap。

---

## 视频转命令
```bash
python gen_video.py \
-x 0 -y -60 -z 0 -d v --height 64\
--input input/pikachu/ \
--output /Users/arceus/Desktop/mc/paper_1120/world/datapacks/test1/data
-n pikachu
-t 4
```
### 参数说明
- `x`, `y`, `z`: 起始坐标
- `d`: 方向 (`v` for vertical, `h` for horizontal)
- `n`: package name
- `t`: ticks (1s = 20 ticks)
- `--width`, `--height`, : 宽高(会自动缩放，设置一个就够了)


---

## mc 内播放视频
### 单机
```mcfunction
function pikachu:run
```

### 服务器
```bash
python play.py -f test1 -c 9 -i 0.1
```


---

## 合成视频
```bash
python gen_video_with_screenshots.py \
--func sao10 \
--output ./output/mc_sao10/ --frame-cnt 1429
```

---