import numpy as np

blocks = [
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
    # concrete
    "minecraft:white_concrete",  # 	White
    "minecraft:light_gray_concrete",  # 	Light Gray
    "minecraft:gray_concrete",  # 	Gray
    "minecraft:black_concrete",  # 	Black
    "minecraft:brown_concrete",  # 	Brown
    "minecraft:red_concrete",  # 	Red
    "minecraft:orange_concrete",  # 	Orange
    "minecraft:yellow_concrete",  # 	Yellow
    "minecraft:lime_concrete",  # 	Lime
    "minecraft:green_concrete",  # 	Green
    "minecraft:cyan_concrete",  # 	Cyan
    "minecraft:light_blue_concrete",  # 	Light Blue
    "minecraft:blue_concrete",  # 	Blue
    "minecraft:purple_concrete",  # 	Purple
    "minecraft:magenta_concrete",  # 	Magenta
    "minecraft:pink_concrete",  # 	Pink

    #-1,
    "minecraft:air"
]
colors = [
    # Wool
    [233, 236, 236],  # 	White
    [142, 142, 134],  # 	Light Gray
    [62, 68, 71],  # 	Gray
    [20, 21, 25],  # 	Black
    [114, 71, 40],  # 	Brown
    [160, 39, 34],  # 	Red
    [240, 118, 19],  # 	Orange
    [248, 197, 39],  # 	Yellow
    [112, 185, 25],  # 	Lime
    [84, 109, 27],  # 	Green
    [21, 137, 145],  # 	Cyan
    [58, 175, 217],  # 	Light Blue
    [53, 57, 157],  # 	Blue
    [121, 42, 172],  # 	Purple
    [189, 68, 179],  # 	Magenta
    [237, 141, 172],  # 	Pink
    # Terracotta
    [210, 177, 161],  # 	White 	—
    [135, 107, 98],  # 	Light Gray 	—
    [58, 43, 36],  # 	Gray 	—
    [37, 23, 16],  # 	Black
    [79, 53, 36],  # 	Brown 	—
    [141, 58, 45],  # 	Red 	—
    [157, 81, 35],  # 	Orange 	—
    [184, 130, 33],  # 	Yellow 	—
    [103, 117, 53],  # 	Lime 	—
    [78, 85, 44],  # 	Green 	—
    [86, 92, 92],  # 	Cyan 	—
    [118, 111, 140],  # 	Light Blue 	—
    [74, 59, 91],  # 	Blue 	—
    [123, 74, 89],  # 	Purple 	—
    [148, 86, 108],  # 	Magenta 	—
    [166, 81, 81],  # 	Pink 	—
    # Concrete
    [207, 213, 214],  # 	White 	—
    [125, 125, 115],  # 	Light Gray 	—
    [55, 58, 62],  # 	Gray 	—
    [8, 10, 15],  # 	Black
    [96, 60, 32],  # 	Brown 	—
    [142, 33, 33],  # 	Red 	—
    [224, 97, 1],  # 	Orange 	—
    [241, 175, 21],  # 	Yellow 	—
    [94, 169, 24],  # 	Lime 	—
    [73, 91, 36],  # 	Green 	—
    [21, 119, 136],  # 	Cyan 	—
    [36, 137, 199],  # 	Light Blue 	—
    [45, 47, 143],  # 	Blue 	—
    [100, 32, 156],  # 	Purple 	—
    [169, 48, 159],  # 	Magenta 	—
    [213, 101, 143],  # 	Pink 	—

    [-1,-1,-1] # 给空气
]
colors = np.array(colors)
colors[:, [2, 0]] = colors[:, [0, 2]]