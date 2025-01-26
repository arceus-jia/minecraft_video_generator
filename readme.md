mc video generator

## Overview
一个将视频搬进minecraft的脚本。 亦可以用于制作地图画，动态建筑物等
参考效果

https://github.com/user-attachments/assets/70876711-58ec-4d90-a9a9-1ea949773a22


https://github.com/user-attachments/assets/51e89451-bb36-4573-84a6-07e958b9ae9f


## 环境
```bash
conda create -n mvg python=3.10
pip install -r requirements.txt
```

## 单图转命令
```bash
python gen_pic_mcfunction_colormap.py \
-x 0 -y -60 -z 0 -d h \
--input input/1.png \
--output  /Users/arceus/Desktop/mc/paper_1120/world/datapacks/test1/data/test1/functions/pic1.mcfunction

```
### 参数说明
x y z: 起始坐标
d: 方向 (v 或者 h)

### 注
多图生成中，提前处理colormap的版本效率最高, 对于单图也可以使用gen_pic_mcfunction.py或者 gen_pic_mcfunction_kdtree.py

cfg.py可以配置方块对应颜色， gen_pic_mcfunction_colormap需要通过prepare_colormap重新生成colormap
对于 kdtree或者原生版本不需要


## 视频转命令
```bash
python gen_video.py \
-x 0 -y -60 -z 0 -d h \
--input input/pikachu/ \
--output  /Users/arceus/Desktop/mc/paper_1120/world/datapacks/test1/data/test1/functions/ 
```

## mc内播放视频
```bash
python play.py -f test1 -c 9 -i 0.1
```

## 合成视频
```bash
python gen_video_with_screenshots.py \
--func sao10 \
--output ./output/mc_sao10/ --frame-cnt 1429
```
