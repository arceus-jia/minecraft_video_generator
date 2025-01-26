## 1. 生成图片
```
python extract_video.py --input ../../input/sao10.mp4 --output ../../output/sao10 --skip 1 --max-cnt 4800
```

## 2. 生成functions
```
 python gen_video.py -x 0 -y -60 -z 0 --output /Users/arceus/Desktop/mc/paper_1120/world/datapacks/test1/data/sao10/functions/  --width 320 --input ../../output/sao10/
```
### z轴
```
python gen_video.py -x -3320 -y 86 -z 236 --output /Users/arceus/Desktop/mc/paper_1120/world/datapacks/test1/data/chouchou/functions --width 60 --input ../../input/chouchou --direction z

```

## 3 生成画廊
python gen_gallery.py -x 0 -y -60 -z 0 --output ~/Desktop/mc/paper_1120/world/datapacks/test1/data/sao1/functions --width 320 --input ../../input/sao10/


## 4. rconfill
```
time set day
gamerule sendCommandFeedback false
gamerule doDaylightCycle false
weather clear 100000d
tp @s 160 23 126 180 0
tp wangguanguan 160 23 126 180 0
```

```
python run_rcon.py
```

## get video screenshot

```shell
python gen_video_with_screenshots.py --func sao10 --output ../../output/mc_sao10/ --frame-cnt 1429
```

## merge
```shell
python merge_video.py --input ../../output/mc_sao10/ --fps 12 --output ../../output/mc_sao10.mp4


```

<!-- fill 0 -60 0 321 121 0 minecraft:air -->