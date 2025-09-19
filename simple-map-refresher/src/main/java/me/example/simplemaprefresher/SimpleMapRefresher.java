package me.example.simplemaprefresher;

import org.bukkit.*;
import org.bukkit.block.Block;
import org.bukkit.command.*;
import org.bukkit.entity.Player;
import org.bukkit.map.*;
import org.bukkit.plugin.java.JavaPlugin;

import java.io.File;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.util.*;

import java.io.*;
import java.awt.Color;
import java.lang.reflect.Field;

public class SimpleMapRefresher extends JavaPlugin {

    // 全局 tick 计数，用于渲染端节流（与全局调度同步递增）
    static long TICK = 0L;

    private final BindManager binds = new BindManager(this);

    @Override
    public void onEnable() {
        getLogger().info("SimpleMapRefresher 1.2.0 enabled.");
    }

    @Override
    public void onDisable() {
        binds.stopAll();
    }

    // =============== Commands ===============
    @Override
    public boolean onCommand(CommandSender sender, Command cmd, String label, String[] a) {
        if (!sender.hasPermission("mapref.use")) {
            sender.sendMessage(c("&cNo permission."));
            return true;
        }
        if (a.length == 0) {
            help(sender);
            return true;
        }

        switch (a[0].toLowerCase(Locale.ROOT)) {
            case "set": {
                try {
                    // 必填：ids, world, x1, y, z1
                    if (a.length < 6) {
                        help(sender);
                        return true;
                    }

                    String[] idStrs = a[1].split(",");
                    int[] ids = new int[idStrs.length];
                    for (int i = 0; i < idStrs.length; i++)
                        ids[i] = Integer.parseInt(idStrs[i].trim());

                    String worldName = a[2];
                    int x1 = Integer.parseInt(a[3]);
                    int y = Integer.parseInt(a[4]);
                    int z1 = Integer.parseInt(a[5]);

                    int iArg = 6;

                    // 可选：x2, y(忽略), z2
                    Integer x2 = null, z2 = null;
                    if (a.length - iArg >= 3) {
                        x2 = Integer.parseInt(a[iArg]);
                        iArg++;
                        /* int y2 = */ /* 忽略 */ iArg++;
                        z2 = Integer.parseInt(a[iArg]);
                        iArg++;
                    }

                    // 可选：cols, rows
                    int cols = 1, rows = 1;
                    if (a.length - iArg >= 2) {
                        cols = Integer.parseInt(a[iArg++]);
                        rows = Integer.parseInt(a[iArg++]);
                    }

                    // 可选：interval, radius
                    int interval = 2, radius = 64;
                    if (a.length - iArg >= 2) {
                        interval = Integer.parseInt(a[iArg++]);
                        radius = Integer.parseInt(a[iArg++]);
                    }

                    // 如果还有多余参数，判定为用法错误
                    if (iArg != a.length) {
                        help(sender);
                        return true;
                    }

                    // 默认 128×128（当 x2/z2 省略）
                    if (x2 == null)
                        x2 = x1 + 127;
                    if (z2 == null)
                        z2 = z1 + 127;

                    // 基本校验
                    if (cols <= 0 || rows <= 0) {
                        sender.sendMessage(c("&ccols/rows 必须 > 0"));
                        return true;
                    }
                    int total = cols * rows;
                    if (ids.length != total) {
                        sender.sendMessage(c("&cmapId 数量与 cols*rows 不一致：" + ids.length + " != " + total));
                        return true;
                    }

                    // 计算铺图分块
                    int xMin = Math.min(x1, x2), xMax = Math.max(x1, x2);
                    int zMin = Math.min(z1, z2), zMax = Math.max(z1, z2);
                    int w = xMax - xMin + 1, h = zMax - zMin + 1;

                    int idx = 0;
                    // 创建组
                    BindManager.TileGroup g = binds.createGroup(worldName, interval);

                    for (int r = 0; r < rows; r++) {
                        int zStartOff = (int) Math.floor((long) r * h / (double) rows);
                        int zEndOff = (int) Math.floor((long) (r + 1) * h / (double) rows) - 1;
                        int z1t = zMin + zStartOff;
                        int z2t = zMin + zEndOff;
                        for (int ccol = 0; ccol < cols; ccol++) {
                            int xStartOff = (int) Math.floor((long) ccol * w / (double) cols);
                            int xEndOff = (int) Math.floor((long) (ccol + 1) * w / (double) cols) - 1;
                            int x1t = xMin + xStartOff;
                            int x2t = xMin + xEndOff;

                            int mapId = ids[idx++];
                            Binding b = binds.addOrReplaceGetBinding(mapId, worldName, x1t, y, z1t, x2t, y, z2t,
                                    interval, radius);
                            if (b == null) {
                                sender.sendMessage(c("&c绑定失败 map#" + mapId + "：检查 world 是否存在、map 是否已展开。"));
                                return true;
                            }
                            binds.putIntoGroup(mapId, b, g);
                        }
                    }
                    sender.sendMessage(c("&a已绑定 " + ids.length + " 张地图，布局=" + cols + "×" + rows +
                            "，区域=(" + xMin + "," + y + "," + zMin + ")~(" + xMax + "," + y + "," + zMax + ") " +
                            " interval=" + interval + " radius=" + radius));
                    return true;

                } catch (NumberFormatException e) {
                    sender.sendMessage(c("&c参数必须是整数。"));
                    return true;
                }
            }

            case "remove": {
                if (a.length != 2) {
                    sender.sendMessage(c("&e用法: /mapref remove <mapId>"));
                    return true;
                }
                try {
                    int mapId = Integer.parseInt(a[1]);
                    if (binds.remove(mapId))
                        sender.sendMessage(c("&a已移除绑定 map#" + mapId));
                    else
                        sender.sendMessage(c("&e未找到 map#" + mapId + " 的绑定"));
                } catch (NumberFormatException e) {
                    sender.sendMessage(c("&cmapId 必须是整数。"));
                }
                return true;
            }
            case "list": {
                List<String> lines = binds.listAll();
                if (lines.isEmpty())
                    sender.sendMessage(c("&e当前没有绑定。"));
                else
                    for (String s : lines)
                        sender.sendMessage(c("&a• &f" + s));
                return true;
            }
            case "stop": {
                binds.stopAll();
                sender.sendMessage(c("&a已停止所有绑定。"));
                return true;
            }
            case "dump": {
                String filename = (a.length >= 2) ? a[1] : "palette.csv";
                File outFile = new File(getDataFolder(), filename);
                try {
                    outFile.getParentFile().mkdirs();

                    Field f = MapPalette.class.getDeclaredField("colors");
                    f.setAccessible(true);
                    Color[] colors = (Color[]) f.get(null);

                    try (PrintWriter pw = new PrintWriter(new FileWriter(outFile))) {
                        for (int i = 0; i < colors.length; i++) {
                            Color c = colors[i];
                            pw.printf("%d,%d,%d,%d%n", i, c.getRed(), c.getGreen(), c.getBlue());
                        }
                    }

                    sender.sendMessage(c("&a调色板已导出到: &f" + outFile.getAbsolutePath()));
                } catch (Exception e) {
                    e.printStackTrace();
                    sender.sendMessage(c("&c导出失败: " + e.getMessage()));
                }
                return true;
            }

            default:
                help(sender);
                return true;
        }
    }

    private void help(CommandSender s) {
        s.sendMessage(c("&e用法(统一)："));
        s.sendMessage(
                c("&f/mapref set <id[,id2,...]> <world> <x1> <y> <z1> [<x2> <y> <z2>] [cols rows] [interval radius]"));
        s.sendMessage(c("&7默认: x2=x1+127, z2=z1+127, cols=1, rows=1, interval=2, radius=64"));
        s.sendMessage(c("&f/mapref remove <mapId>"));
        s.sendMessage(c("&f/mapref list"));
        s.sendMessage(c("&f/mapref stop"));
        s.sendMessage(c("&f/mapref dump"));
    }

    private static String c(String s) {
        return ChatColor.translateAlternateColorCodes('&', s);
    }

    // =============== Bind Manager (multi) ===============
    static class BindManager {
        private final JavaPlugin plugin;
        // mapId -> binding (使用 TreeMap 保证按 mapId 排序)
        private final Map<Integer, Binding> all = new TreeMap<>();
        // 全局单任务调度，1t 执行一次，统一对齐发送
        private int globalTaskId = -1;

        // 轻量分组：每张地图归属的组，以及所有组列表
        private final Map<Integer, TileGroup> groupOfMap = new HashMap<>();
        private final List<TileGroup> groups = new ArrayList<>();

        static class TileGroup {
            final String worldName;
            final List<Binding> members = new ArrayList<>();
            int interval; // 组内统一 interval（按 /set 传入值）

            TileGroup(String worldName, int interval) {
                this.worldName = worldName;
                this.interval = Math.max(1, interval);
            }
        }

        BindManager(JavaPlugin p) {
            this.plugin = p;
        }

        boolean addOrReplace(int mapId, String worldName,
                int x1, int y1, int z1, Integer x2, Integer y2, Integer z2,
                int interval, int radius) {
            World world = Bukkit.getWorld(worldName);
            if (world == null)
                return false;
            MapView view = Bukkit.getMap(mapId);
            if (view == null)
                return false;

            // 如果已存在，先清理
            remove(mapId);

            RegionRenderer renderer = new RegionRenderer(world, x1, y1, z1, x2, y2, z2, radius);
            // 配置 MapView
            view.setScale(MapView.Scale.NORMAL);
            view.setTrackingPosition(false);
            view.setUnlimitedTracking(false);
            for (MapRenderer r : new ArrayList<>(view.getRenderers()))
                view.removeRenderer(r);
            view.addRenderer(renderer);

            // 记录绑定
            all.put(mapId, new Binding(mapId, world, view, renderer, interval, radius));

            ensureGlobalTask();
            return true;
        }

        Binding addOrReplaceGetBinding(int mapId, String worldName,
                int x1, int y1, int z1, Integer x2, Integer y2, Integer z2,
                int interval, int radius) {
            World world = Bukkit.getWorld(worldName);
            if (world == null)
                return null;
            MapView view = Bukkit.getMap(mapId);
            if (view == null)
                return null;

            // 如果已存在，先清理
            remove(mapId);

            RegionRenderer renderer = new RegionRenderer(world, x1, y1, z1, x2, y2, z2, radius);
            // 配置 MapView
            view.setScale(MapView.Scale.NORMAL);
            view.setTrackingPosition(false);
            view.setUnlimitedTracking(false);
            for (MapRenderer r : new ArrayList<>(view.getRenderers()))
                view.removeRenderer(r);
            view.addRenderer(renderer);

            Binding b = new Binding(mapId, world, view, renderer, Math.max(1, interval), Math.max(1, radius));
            all.put(mapId, b);

            ensureGlobalTask();
            return b;
        }

        boolean remove(int mapId) {
            Binding b = all.remove(mapId);
            if (b == null)
                return false;

            if (b.view != null && b.renderer != null)
                b.view.removeRenderer(b.renderer);

            // 从组里移除
            TileGroup g = groupOfMap.remove(mapId);
            if (g != null) {
                g.members.remove(b);
                if (g.members.isEmpty()) {
                    groups.remove(g);
                }
            }

            if (all.isEmpty())
                cancelGlobalTask();
            return true;
        }

        void stopAll() {
            for (Binding b : all.values()) {
                if (b.view != null && b.renderer != null)
                    b.view.removeRenderer(b.renderer);
            }
            all.clear();
            cancelGlobalTask();
            groupOfMap.clear();
            groups.clear();

        }

        List<String> listAll() {
            List<String> ls = new ArrayList<>();
            for (Binding b : all.values())
                ls.add(infoString(b));
            return ls;
        }

        String infoOf(int mapId) {
            Binding b = all.get(mapId);
            return (b == null) ? "未绑定" : infoString(b);
        }

        private String infoString(Binding b) {
            return "map#" + b.mapId + " world=" + b.world.getName() + " interval=" + b.interval + "tick radius="
                    + b.radius +
                    " region=" + b.renderer.regionString();
        }

        private TileGroup createGroup(String worldName, int interval) {
            TileGroup g = new TileGroup(worldName, Math.max(1, interval));
            groups.add(g);
            return g;
        }

        private void putIntoGroup(int mapId, Binding b, TileGroup g) {
            // 防御：如果这个 mapId 曾经在别的组，先移除旧映射
            TileGroup old = groupOfMap.remove(mapId);
            if (old != null)
                old.members.remove(b);

            groupOfMap.put(mapId, g);
            g.members.add(b);
        }

        private void ensureGlobalTask() {
            if (globalTaskId != -1)
                return;

            globalTaskId = Bukkit.getScheduler().scheduleSyncRepeatingTask(plugin, () -> {
                TICK++;

                boolean anyChanged = false;

                // ===== 阶段A：采样（仍按各自 interval 节流）=====
                for (Map.Entry<Integer, Binding> entry : all.entrySet()) {
                    Binding b = entry.getValue();
                    if (b.world == null || b.view == null || b.renderer == null)
                        continue;

                    if (b.interval > 1 && (TICK % b.interval) != 0)
                        continue;

                    if (b.renderer.sampleWorldIntoDesired()) {
                        anyChanged = true;
                    }
                }

                // 关键点：只要有任意一张有变化，安排“下一 tick 广播发送给所有绑定”
                if (anyChanged) {
                    for (Binding b : all.values()) {
                        b.hasPendingFrame = true;
                        b.scheduledSendTick = TICK + 1; // 统一延迟 1 tick
                    }
                }

                // ===== 阶段B：发送（仅发送上一 tick 采到变化的 binding）=====
                // 先按世界缓存在线玩家列表（同一世界复用同一份列表）
                Map<World, List<Player>> worldPlayers = new IdentityHashMap<>();
                for (Player p : Bukkit.getOnlinePlayers()) {
                    worldPlayers.computeIfAbsent(p.getWorld(), w -> new ArrayList<>()).add(p);
                }

                for (Binding b : all.values()) {
                    if (!b.hasPendingFrame)
                        continue;
                    if (b.scheduledSendTick != TICK)
                        continue;

                    List<Player> players = worldPlayers.get(b.world);
                    if (players != null && !players.isEmpty()) {
                        for (Player p : players) {
                            if (b.renderer.playerInRange(p)) {
                                p.sendMap(b.view);
                            }
                        }
                    }
                    b.hasPendingFrame = false;
                    b.scheduledSendTick = -1L;
                }
            }, 1L, 1L);
        }

        private void cancelGlobalTask() {
            if (globalTaskId != -1) {
                Bukkit.getScheduler().cancelTask(globalTaskId);
                globalTaskId = -1;
            }
        }
    }

    static class Binding {
        final int mapId, interval, radius;
        final World world;
        final MapView view;
        final RegionRenderer renderer;

        // 新增：延迟发送的调度
        long scheduledSendTick = -1L; // 何时发送（= 采样 tick + 1）
        boolean hasPendingFrame = false; // 是否有待发送帧

        Binding(int mapId, World w, MapView v, RegionRenderer r, int interval, int radius) {
            this.mapId = mapId;
            this.world = w;
            this.view = v;
            this.renderer = r;
            this.interval = interval;
            this.radius = radius;
        }
    }

    // =============== Renderer（支持任意两点、XYZ 顺序；只在变化时发送；预映射；多实例） ===============
    static class RegionRenderer extends MapRenderer {
        final World world;
        final int xMin, yFix, zMin, xMax, zMax; // 水平矩形 + 固定 Y
        final boolean useResample;
        final int radius;

        private final Map<Material, Byte> lut = new EnumMap<>(Material.class);
        private final int[] mapWX = new int[128], mapWZ = new int[128]; // 预映射
        // 画布已应用像素与期望像素（由全局任务采样得到）
        private final byte[] applied = new byte[128 * 128];
        private final byte[] desired = new byte[128 * 128];
        private volatile boolean pending = true; // 是否有待应用的新帧

        RegionRenderer(World w, int x1, int y1, int z1, Integer x2Maybe, Integer y2Maybe, Integer z2Maybe, int radius) {
            super(true);
            this.world = w;
            this.yFix = y1; // 采样固定 Y（你动画所在层）
            int xx2 = (x2Maybe != null) ? x2Maybe : x1 + 127;
            int zz2 = (z2Maybe != null) ? z2Maybe : z1 + 127;
            this.xMin = Math.min(x1, xx2);
            this.zMin = Math.min(z1, zz2);
            this.xMax = Math.max(x1, xx2);
            this.zMax = Math.max(z1, zz2);
            int wdt = xMax - xMin + 1, hgt = zMax - zMin + 1;
            this.useResample = (wdt != 128 || hgt != 128);
            this.radius = radius;

            initPalette();
            precomputeMapping();
        }

        String regionString() {
            String base = "(" + xMin + "," + yFix + "," + zMin + ") ~ (" + xMax + "," + yFix + "," + zMax + ")";
            return useResample ? base + " (缩放至128×128)" : base + " (1:1)";
        }

        @Override
        public void render(MapView map, MapCanvas canvas, Player player) {
            // 不再在 render 中做节流，完全依赖全局调度
            // 因为 render() 可能被 Bukkit 以不同频率调用
            if (!pending)
                return;

            // 应用所有变化
            int idx = 0;
            boolean hasChanges = false;
            for (int px = 0; px < 128; px++) {
                for (int pz = 0; pz < 128; pz++) {
                    byte c = desired[idx];
                    if (c != applied[idx]) {
                        canvas.setPixel(px, pz, c);
                        applied[idx] = c;
                        hasChanges = true;
                    }
                    idx++;
                }
            }

            // 只有真正有变化时才清除 pending
            if (hasChanges) {
                pending = false;
            }
        }

        // 由全局任务在合适 tick 调用：采样世界像素，更新 desired，并返回是否有变化需要发送
        boolean sampleWorldIntoDesired() {
            return sampleWorldIntoDesired(false);
        }

        // 支持使用快照模式的采样方法
        boolean sampleWorldIntoDesired(boolean useSnapshot) {
            boolean changed = false;
            int idx = 0;
            for (int px = 0; px < 128; px++) {
                int wx = mapWX[px];
                for (int pz = 0; pz < 128; pz++) {
                    int wz = mapWZ[pz];
                    // 直接采样，不使用快照（因为4个地图覆盖不同区域）
                    Material m = world.getBlockAt(wx, yFix, wz).getType();
                    byte c = colorOf(m);
                    if (c != desired[idx])
                        desired[idx] = c;
                    if (c != applied[idx])
                        changed = true;
                    idx++;
                }
            }
            if (changed) {
                pending = true;
            }
            return changed;
        }

        // 兼容旧调用名：全局调度/旧路径统一调用本方法判断是否有变化
        boolean flushDirtyAndHasChanges() {
            return sampleWorldIntoDesired();
        }

        boolean playerInRange(Player p) {
            if (p.getWorld() != world)
                return false;
            double cx = (xMin + xMax) / 2.0, cz = (zMin + zMax) / 2.0;
            Location L = p.getLocation();
            double dx = L.getX() - cx, dz = L.getZ() - cz;
            return (dx * dx + dz * dz) <= (radius * radius);
        }

        private void precomputeMapping() {
            int wdt = xMax - xMin + 1, hgt = zMax - zMin + 1;
            if (!useResample) {
                for (int i = 0; i < 128; i++) {
                    mapWX[i] = xMin + i;
                    mapWZ[i] = zMin + i;
                }
            } else {
                for (int px = 0; px < 128; px++) {
                    int wx = xMin + (int) Math.floor((px + 0.5) * wdt / 128.0);
                    if (wx > xMax)
                        wx = xMax;
                    mapWX[px] = wx;
                }
                for (int pz = 0; pz < 128; pz++) {
                    int wz = zMin + (int) Math.floor((pz + 0.5) * hgt / 128.0);
                    if (wz > zMax)
                        wz = zMax;
                    mapWZ[pz] = wz;
                }
            }
        }

        private void initPalette() {
            // ===== 羊毛 Wool (16) =====
            put("WHITE_WOOL", 207, 213, 214);
            put("LIGHT_GRAY_WOOL", 125, 125, 115);
            put("GRAY_WOOL", 54, 57, 61);
            put("BLACK_WOOL", 8, 10, 15);
            put("BROWN_WOOL", 96, 60, 32);
            put("RED_WOOL", 142, 32, 31);
            put("ORANGE_WOOL", 224, 97, 0);
            put("YELLOW_WOOL", 240, 175, 21);
            put("LIME_WOOL", 94, 168, 23);
            put("GREEN_WOOL", 73, 91, 36);
            put("CYAN_WOOL", 21, 120, 136);
            put("LIGHT_BLUE_WOOL", 36, 137, 199);
            put("BLUE_WOOL", 44, 46, 143);
            put("PURPLE_WOOL", 99, 31, 137);
            put("MAGENTA_WOOL", 169, 48, 159);
            put("PINK_WOOL", 214, 101, 143);

            // ===== 陶瓦 Terracotta (16) =====
            put("WHITE_TERRACOTTA", 209, 178, 161);
            put("LIGHT_GRAY_TERRACOTTA", 135, 106, 97);
            put("GRAY_TERRACOTTA", 83, 68, 66);
            put("BLACK_TERRACOTTA", 37, 22, 16);
            put("BROWN_TERRACOTTA", 77, 51, 36);
            put("RED_TERRACOTTA", 142, 60, 46);
            put("ORANGE_TERRACOTTA", 161, 83, 37);
            put("YELLOW_TERRACOTTA", 186, 133, 35);
            put("LIME_TERRACOTTA", 103, 118, 53);
            put("GREEN_TERRACOTTA", 76, 83, 42);
            put("CYAN_TERRACOTTA", 87, 92, 92);
            put("LIGHT_BLUE_TERRACOTTA", 114, 109, 138);
            put("BLUE_TERRACOTTA", 74, 58, 91);
            put("PURPLE_TERRACOTTA", 118, 70, 86);
            put("MAGENTA_TERRACOTTA", 168, 88, 109);
            put("PINK_TERRACOTTA", 208, 132, 153);

            // ===== 木板 Planks (11) —— 树木家族，六面一致 =====
            put("OAK_PLANKS", 162, 130, 79);
            put("SPRUCE_PLANKS", 102, 77, 46);
            put("BIRCH_PLANKS", 205, 201, 145);
            put("JUNGLE_PLANKS", 160, 114, 86);
            put("ACACIA_PLANKS", 169, 87, 50);
            put("DARK_OAK_PLANKS", 66, 43, 21);
            put("MANGROVE_PLANKS", 117, 54, 48);
            put("CHERRY_PLANKS", 233, 154, 170);
            put("BAMBOO_PLANKS", 199, 175, 106);
            put("CRIMSON_PLANKS", 129, 51, 84);
            put("WARPED_PLANKS", 43, 121, 108);

            // ===== 石系 Stone (8) =====
            put("STONE", 125, 125, 125);
            put("SMOOTH_STONE", 196, 196, 196);
            put("GRANITE", 156, 107, 90);
            put("POLISHED_GRANITE", 159, 84, 68);
            put("DIORITE", 188, 188, 188);
            put("POLISHED_DIORITE", 197, 197, 197);
            put("ANDESITE", 136, 136, 136);
            put("POLISHED_ANDESITE", 146, 146, 146);

            // ===== 深色石系 (2) =====
            put("POLISHED_DEEPSLATE", 73, 73, 78);
            put("POLISHED_BLACKSTONE", 51, 47, 59);

            // ===== 光滑白/沙色 (3) =====
            put("SMOOTH_QUARTZ", 235, 229, 222);
            put("SMOOTH_SANDSTONE", 220, 207, 157);
            put("SMOOTH_RED_SANDSTONE", 181, 97, 54);

            // ===== 铜系 Copper (4) =====
            put("COPPER_BLOCK", 198, 116, 74);
            put("EXPOSED_COPPER", 173, 130, 93);
            put("WEATHERED_COPPER", 98, 155, 138);
            put("OXIDIZED_COPPER", 82, 170, 140);

            // ===== 海晶 Prismarine (3) =====
            put("PRISMARINE", 100, 169, 154);
            put("PRISMARINE_BRICKS", 99, 198, 164);
            put("DARK_PRISMARINE", 43, 94, 83);

            // ===== 砖 Brick (3) =====
            put("BRICKS", 149, 85, 70);
            put("NETHER_BRICKS", 45, 23, 31);
            put("RED_NETHER_BRICKS", 84, 28, 32);

            // ===== 透明：AIR =====
            lut.put(Material.AIR, MapPalette.TRANSPARENT);
        }

        private void put(String name, int r, int g, int b) {
            Material m = Material.getMaterial(name);
            if (m != null)
                lut.put(m, MapPalette.matchColor(r, g, b));
        }

        private byte colorOf(Material m) {
            Byte b = lut.get(m);
            return (b != null) ? b : MapPalette.matchColor(120, 120, 120);
        }

    }
}

// /data get entity @p SelectedItem
