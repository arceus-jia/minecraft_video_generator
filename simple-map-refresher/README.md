# SimpleMapRefresher 使用说明（精简版）

一个把“世界中某一层的方块区域”实时映射到地图物品的 Paper/Spigot 插件：固定在某个 Y 高度，采样一块水平 XZ 矩形，渲染到 128×128 地图像素；仅当检测到像素变化时刷新并发送给附近玩家，轻量高效。内置羊毛/陶瓦/木板/石材/铜/海晶/砖等材质的配色表（AIR 透明）。

## 环境与安装
- 服务器：Paper/Spigot 1.21.x（源码依赖 Paper API 1.21.1）。
- Java：JDK 21。
- 安装：在 `simple-map-refresher` 执行 `mvn package`，把生成的 jar 放入服务器 `plugins/`，重启。
- 权限：`mapref.use`（默认仅 OP）。

## 核心指令
- 单地图绑定（区域可 1:1 或缩放到 128×128）
  - `/mapref set <mapId> <world> <x1> <y> <z1> [<x2> <y> <z2>] [intervalTicks] [playerRadius]`
- 多地图平铺绑定（一次把大矩形按列×行切成多块，分别绑定多张地图；行优先：一行内左→右，再上→下）
  - `/mapref set <id1,id2,...> <world> <x1> <y> <z1> <x2> <y> <z2> <cols> <rows> [interval] [radius]`
- 管理
  - `/mapref remove <mapId>`
  - `/mapref list`
  - `/mapref stop`

说明与建议：
- `mapId` 必须是已“展开”的地图（手持看过一次）。
- `[interval]` 默认 2 tick；动图播放建议满足 `interval ≤ 帧间隔`（例如 `--ticks 4` 时用 `interval=2`）。
- 只给同世界且处于 `playerRadius` 内的玩家发送刷新。

## 单图上地图（配合 gen_pic_mcfunction_colormap.py）
把图片转换成一层方块（生成 mcfunction）再绑定地图即可。

步骤：
1) 确定铺图层 `(x,y,z)` 与目标尺寸（建议接近 128×128）。
2) 运行脚本生成 mcfunction（建议水平模式 `-d h`，在固定 y 的水平 XZ 面铺图）。
   - 单文件模式：
     - `python gen_pic_mcfunction_colormap.py --input input/your.png --output /绝对路径/到/world/datapacks/yourpack/data/yourpack/function/run.mcfunction --x 0 --y 100 --z 0 --width 128 --height 128 -d h --mode oklab`
     - 可选清理脚本：`--clear-output /.../clear.mcfunction`
   - 数据包模式（自动写 run/clear）：
     - `python gen_pic_mcfunction_colormap.py --input input/your.png --output /绝对路径/到/world/datapacks/ --namespace pic --x 0 --y 100 --z 0 --width 256 --height 128 -d h --mode oklab`
3) 在游戏中绑定：
   - 恰好 128×128：`/mapref set <mapId> <world> x y z`
   - 任意矩形（如 256×128）：`/mapref set <mapId> <world> x y z x2 y z2`（插件会缩放采样到 128×128）
4) 手持对应地图靠近区域即可看到刷新；再次执行 `run.mcfunction` 或修改方块会自动更新。

提示：`--mode oklab` 往往更贴近人眼；`--dither ordered4`（Bayer 4×4）可减少色带。

## 动图/视频逐帧（gen_video.py）
把一个目录的图片序列转为多帧函数 `frame_0001.mcfunction`…，并生成 `run.mcfunction` 通过 schedule 逐帧播放（默认循环）。

常用参数：
- `--input` 帧目录（.png/.jpg）
- `--output` 数据包 `data/` 目录
- `-n/--datapack_name` 命名空间
- `--x --y --z --width --height --direction/-d --pix` 同单图；推荐 `-d h`
- `--ticks/-t` 每帧间隔（默认 4）
- `--mode --dither --dither-amount` 颜色/抖动（默认 OKLab + ordered4）

示例：
- 生成并循环播放（y=-60，4 tick/帧）：
  - `python gen_video.py --input input/pikachu/ --output /绝对路径/到/world/datapacks/test1/data/ -n pikachu -x 0 -y -60 -z 0 --width 128 --height 128 -d h -t 4`
  - 游戏内：`/function pikachu:run` 播放，`/function pikachu:clear` 清理

建议：满足 `interval ≤ --ticks`（如 `--ticks 4` 配 `interval=2`）；需要“相位一致”时，先 `/mapref stop` → 同 tick 批量绑定 → 再播放。

## 多地图拼接墙屏
适用于大区域（如 256×256、384×256）。有两种方式：

- 方式 A：脚本生成多条绑定命令（tools/gen_tiled_map_cmds.py）
  - `python tools/gen_tiled_map_cmds.py --world world --x0 0 --y0 100 --z0 0 --width 256 --height 256 --tile 128 --start-id 30 --order row --interval 2 --radius 128`
  - 将输出的若干条 `/mapref set ...` 依次在控制台或通过 RCON 执行。

- 方式 B：插件一条命令平铺绑定（无需脚本）
  - 语法（行优先：一行内左→右，再上→下）：
    - `/mapref set <id1,id2,...> <world> <x1> <y> <z1> <x2> <y> <z2> <cols> <rows> [interval] [radius]`
  - 示例（把 (0,-60,0)~(127,-60,127) 切成 2×2 绑定到 0,1,2,3；2 tick 刷新，半径 999）：
    - `/mapref set 0,1,2,3 world 0 -60 0 127 -60 127 2 2 2 999`
  - 说明：`id` 数量必须等于 `cols*rows`；分片等分，边缘自动补齐；所有 tile 参数统一使用相同 `interval/radius`。

  - 示例（3×2 墙屏推荐）
    - 生成帧序列（固定 y=-60，水平铺帧，目标宽 384×高 256）：
      - `python gen_video.py -x 0 -y -60 -z 0 --input output/mickey/ --output ~/Desktop/mc/paper_1121/world/datapacks/test2/data/ -n cat -d h --width 384 --height 256`
    - 绑定 3 列 × 2 行（第一行地图 0,1,2；第二行 3,4,5），建议 `interval=2` 与 `--ticks 4` 搭配：
      - `/mapref set 0,1,2,3,4,5 world 0 -60 0 383 -60 255 3 2 2 999`
    - 摆放顺序：第一行从左到右放 0,1,2；第二行从左到右放 3,4,5。

摆放与同步：
- 按顺序摆好四张（或多张）不同 `mapId` 的地图（行优先=左到右、上到下）。
- 为避免不同步：尽量“同一 tick”批量下发绑定（控制台粘贴或 RCON 批发）；并保证 `interval ≤ --ticks`。
- 注意：mcfunction 不能执行插件命令（`/mapref ...`），请用控制台/RCON/命令方块链来下发。

## 同步与刷新机制（v1.2+）
- 全局调度：插件使用“全局 1t 调度”统一对齐所有绑定的采样与发送，短 `interval` 下也能保持多地图同步。
- 统一采样：每到达某绑定的 `interval` 节拍，统一采样世界像素，只有检测到像素变化才会发送。
- 渲染应用：`render()` 只在允许节拍把已采样帧写入画布，避免 Bukkit 高频渲染造成的相位差。

升级注意
- 若替换 jar 后加载异常，清理 `plugins/.paper-remapped` 下本插件的 remap 缓存，或直接把新文件改用全新文件名（例如 `simple-map-refresher-1.2.0.jar`）。

## 常见问题（FAQ）
- 绑定失败：`world` 不存在或 `mapId` 未展开（先手持看一次）。
- 不刷新：玩家不在同世界/半径内；区域无变化；`interval` 过大；拿的不是对应 `mapId`。
- 缩放锯齿：提高源分辨率并启用脚本抖动；或让实际铺图尺寸更接近 128×128。

## 兼容性
- 基于 Paper API 1.21.1。其他版本大概率可用，建议与 1.21.x 搭配。
- 不跨世界广播、不会向超出半径的玩家发送，避免无谓负载。
