import numpy as np

# blocks = [
#     "minecraft:white_wool",  # 	White
#     "minecraft:light_gray_wool",  # 	Light Gray
#     "minecraft:gray_wool",  # 	Gray
#     "minecraft:black_wool",  # 	Black
#     "minecraft:brown_wool",  # 	Brown
#     "minecraft:red_wool",  # 	Red
#     "minecraft:orange_wool",  # 	Orange
#     "minecraft:yellow_wool",  # 	Yellow
#     "minecraft:lime_wool",  # 	Lime
#     "minecraft:green_wool",  # 	Green
#     "minecraft:cyan_wool",  # 	Cyan
#     "minecraft:light_blue_wool",  # 	Light Blue
#     "minecraft:blue_wool",  # 	Blue
#     "minecraft:purple_wool",  # 	Purple
#     "minecraft:magenta_wool",  # 	Magenta
#     "minecraft:pink_wool",  # 	Pink
#     # terracotta
#     "minecraft:white_terracotta",  # 	White
#     "minecraft:light_gray_terracotta",  # 	Light Gray
#     "minecraft:gray_terracotta",  # 	Gray
#     "minecraft:black_terracotta",  # 	Black
#     "minecraft:brown_terracotta",  # 	Brown
#     "minecraft:red_terracotta",  # 	Red
#     "minecraft:orange_terracotta",  # 	Orange
#     "minecraft:yellow_terracotta",  # 	Yellow
#     "minecraft:lime_terracotta",  # 	Lime
#     "minecraft:green_terracotta",  # 	Green
#     "minecraft:cyan_terracotta",  # 	Cyan
#     "minecraft:light_blue_terracotta",  # 	Light Blue
#     "minecraft:blue_terracotta",  # 	Blue
#     "minecraft:purple_terracotta",  # 	Purple
#     "minecraft:magenta_terracotta",  # 	Magenta
#     "minecraft:pink_terracotta",  # 	Pink
#     # concrete
#     "minecraft:white_concrete",  # 	White
#     "minecraft:light_gray_concrete",  # 	Light Gray
#     "minecraft:gray_concrete",  # 	Gray
#     "minecraft:black_concrete",  # 	Black
#     "minecraft:brown_concrete",  # 	Brown
#     "minecraft:red_concrete",  # 	Red
#     "minecraft:orange_concrete",  # 	Orange
#     "minecraft:yellow_concrete",  # 	Yellow
#     "minecraft:lime_concrete",  # 	Lime
#     "minecraft:green_concrete",  # 	Green
#     "minecraft:cyan_concrete",  # 	Cyan
#     "minecraft:light_blue_concrete",  # 	Light Blue
#     "minecraft:blue_concrete",  # 	Blue
#     "minecraft:purple_concrete",  # 	Purple
#     "minecraft:magenta_concrete",  # 	Magenta
#     "minecraft:pink_concrete",  # 	Pink
#     # -1,
#     "minecraft:air",
# ]
# colors = [
#     # Wool
#     [233, 236, 236],  # 	White
#     [142, 142, 134],  # 	Light Gray
#     [62, 68, 71],  # 	Gray
#     [20, 21, 25],  # 	Black
#     [114, 71, 40],  # 	Brown
#     [160, 39, 34],  # 	Red
#     [240, 118, 19],  # 	Orange
#     [248, 197, 39],  # 	Yellow
#     [112, 185, 25],  # 	Lime
#     [84, 109, 27],  # 	Green
#     [21, 137, 145],  # 	Cyan
#     [58, 175, 217],  # 	Light Blue
#     [53, 57, 157],  # 	Blue
#     [121, 42, 172],  # 	Purple
#     [189, 68, 179],  # 	Magenta
#     [237, 141, 172],  # 	Pink
#     # Terracotta
#     [210, 177, 161],  # 	White 	—
#     [135, 107, 98],  # 	Light Gray 	—
#     [58, 43, 36],  # 	Gray 	—
#     [37, 23, 16],  # 	Black
#     [79, 53, 36],  # 	Brown 	—
#     [141, 58, 45],  # 	Red 	—
#     [157, 81, 35],  # 	Orange 	—
#     [184, 130, 33],  # 	Yellow 	—
#     [103, 117, 53],  # 	Lime 	—
#     [78, 85, 44],  # 	Green 	—
#     [86, 92, 92],  # 	Cyan 	—
#     [118, 111, 140],  # 	Light Blue 	—
#     [74, 59, 91],  # 	Blue 	—
#     [123, 74, 89],  # 	Purple 	—
#     [148, 86, 108],  # 	Magenta 	—
#     [166, 81, 81],  # 	Pink 	—
#     # Concrete
#     [207, 213, 214],  # 	White 	—
#     [125, 125, 115],  # 	Light Gray 	—
#     [55, 58, 62],  # 	Gray 	—
#     [8, 10, 15],  # 	Black
#     [96, 60, 32],  # 	Brown 	—
#     [142, 33, 33],  # 	Red 	—
#     [224, 97, 1],  # 	Orange 	—
#     [241, 175, 21],  # 	Yellow 	—
#     [94, 169, 24],  # 	Lime 	—
#     [73, 91, 36],  # 	Green 	—
#     [21, 119, 136],  # 	Cyan 	—
#     [36, 137, 199],  # 	Light Blue 	—
#     [45, 47, 143],  # 	Blue 	—
#     [100, 32, 156],  # 	Purple 	—
#     [169, 48, 159],  # 	Magenta 	—
#     [213, 101, 143],  # 	Pink 	—
#     [-1, -1, -1],  # 给空气
# ]


blocks = [
    # wool
    "minecraft:white_wool",  # 	White
    "minecraft:light_gray_wool",  # 	Light Gray
    "minecraft:gray_wool",  # 	Gray
    "minecraft:black_wool",  # 	Black
    "minecraft:brown_wool",  # 	Brown
    "minecraft:red_wool",  # 	Red
    "minecraft:orange_wool",  # 	Orange
    "minecraft:yellow_wool",  # 	Yellow
    "minecraft:lime_wool",  # 	Lime
    "minecraft:green_wool",  # 	Green
    "minecraft:cyan_wool",  # 	Cyan
    "minecraft:light_blue_wool",  # 	Light Blue
    "minecraft:blue_wool",  # 	Blue
    "minecraft:purple_wool",  # 	Purple
    "minecraft:magenta_wool",  # 	Magenta
    "minecraft:pink_wool",  # 	Pink
    # terracotta
    "minecraft:white_terracotta",  # 	White
    "minecraft:light_gray_terracotta",  # 	Light Gray
    "minecraft:gray_terracotta",  # 	Gray
    "minecraft:black_terracotta",  # 	Black
    "minecraft:brown_terracotta",  # 	Brown
    "minecraft:red_terracotta",  # 	Red
    "minecraft:orange_terracotta",  # 	Orange
    "minecraft:yellow_terracotta",  # 	Yellow
    "minecraft:lime_terracotta",  # 	Lime
    "minecraft:green_terracotta",  # 	Green
    "minecraft:cyan_terracotta",  # 	Cyan
    "minecraft:light_blue_terracotta",  # 	Light Blue
    "minecraft:blue_terracotta",  # 	Blue
    "minecraft:purple_terracotta",  # 	Purple
    "minecraft:magenta_terracotta",  # 	Magenta
    "minecraft:pink_terracotta",  # 	Pink
    # ==== planks（树木家族，颜色跨度大，六面统一） ====
    "minecraft:oak_planks",
    "minecraft:spruce_planks",
    "minecraft:birch_planks",
    "minecraft:jungle_planks",
    "minecraft:acacia_planks",
    "minecraft:dark_oak_planks",
    "minecraft:mangrove_planks",
    "minecraft:cherry_planks",
    "minecraft:bamboo_planks",
    "minecraft:crimson_planks",
    "minecraft:warped_planks",
    # ==== stone 系（中性色/皮肤色常用，六面统一） ====
    "minecraft:stone",
    "minecraft:smooth_stone",
    "minecraft:granite",
    "minecraft:polished_granite",
    "minecraft:diorite",
    "minecraft:polished_diorite",
    "minecraft:andesite",
    "minecraft:polished_andesite",
    # ==== 深色石系 ====
    "minecraft:polished_deepslate",
    "minecraft:polished_blackstone",
    # ==== 光滑白/沙色（大面积干净底色） ====
    "minecraft:smooth_quartz",
    "minecraft:smooth_sandstone",
    "minecraft:smooth_red_sandstone",
    # ==== 铜（从橙到青绿，一条完整渐变） ====
    "minecraft:copper_block",
    "minecraft:exposed_copper",
    "minecraft:weathered_copper",
    "minecraft:oxidized_copper",
    # ==== 海晶（冷色系） ====
    "minecraft:prismarine",
    "minecraft:prismarine_bricks",
    "minecraft:dark_prismarine",
    # ==== 砖（红砖&地狱砖，深红系） ====
    "minecraft:bricks",
    "minecraft:nether_bricks",
    "minecraft:red_nether_bricks",
    # -1,
    "minecraft:air",
]

colors = [
    # wool
    [207, 213, 214],  # White
    [125, 125, 115],  # Light Gray
    [54, 57, 61],  # Gray
    [8, 10, 15],  # Black
    [96, 60, 32],  # Brown
    [142, 32, 31],  # Red
    [224, 97, 0],  # Orange
    [240, 175, 21],  # Yellow
    [94, 168, 23],  # Lime
    [73, 91, 36],  # Green
    [21, 120, 136],  # Cyan
    [36, 137, 199],  # Light Blue
    [44, 46, 143],  # Blue
    [99, 31, 137],  # Purple
    [169, 48, 159],  # Magenta
    [214, 101, 143],  # Pink
    # tecracotta
    [209, 178, 161],  # White
    [135, 106, 97],  # Light Gray
    [83, 68, 66],  # Gray
    [37, 22, 16],  # Black
    [77, 51, 36],  # Brown
    [142, 60, 46],  # Red
    [161, 83, 37],  # Orange
    [186, 133, 35],  # Yellow
    [103, 118, 53],  # Lime
    [76, 83, 42],  # Green
    [87, 92, 92],  # Cyan
    [114, 109, 138],  # Light Blue
    [74, 58, 91],  # Blue
    [118, 70, 86],  # Purple
    [168, 88, 109],  # Magenta
    [208, 132, 153],  # Pink
    # planks
    [162, 130, 79],  # oak_planks
    [102, 77, 46],  # spruce_planks
    [205, 201, 145],  # birch_planks
    [160, 114, 86],  # jungle_planks
    [169, 87, 50],  # acacia_planks
    [66, 43, 21],  # dark_oak_planks
    [117, 54, 48],  # mangrove_planks
    [233, 154, 170],  # cherry_planks
    [199, 175, 106],  # bamboo_planks
    [129, 51, 84],  # crimson_planks
    [43, 121, 108],  # warped_planks
    # stone 系
    [125, 125, 125],  # stone
    [196, 196, 196],  # smooth_stone
    [156, 107, 90],  # granite
    [159, 84, 68],  # polished_granite
    [188, 188, 188],  # diorite
    [197, 197, 197],  # polished_diorite
    [136, 136, 136],  # andesite
    [146, 146, 146],  # polished_andesite
    # 深色石系
    [73, 73, 78],  # polished_deepslate
    [51, 47, 59],  # polished_blackstone
    # 光滑白/沙色
    [235, 229, 222],  # smooth_quartz
    [220, 207, 157],  # smooth_sandstone
    [181, 97, 54],  # smooth_red_sandstone
    # 铜系列
    [198, 116, 74],  # copper_block
    [173, 130, 93],  # exposed_copper
    [98, 155, 138],  # weathered_copper
    [82, 170, 140],  # oxidized_copper
    # 海晶
    [100, 169, 154],  # prismarine
    [99, 198, 164],  # prismarine_bricks
    [43, 94, 83],  # dark_prismarine
    # 砖
    [149, 85, 70],  # bricks
    [45, 23, 31],  # nether_bricks
    [84, 28, 32],  # red_nether_bricks
    # air
    [-1, -1, -1],  # 给空气
]


colors = np.array(colors)
colors[:, [2, 0]] = colors[:, [0, 2]]
