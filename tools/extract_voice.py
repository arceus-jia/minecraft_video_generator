#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
extract_voice.py

功能：
- 从 --input（mp3/mp4/mov 等）中抽取音频，转为 OGG(Vorbis)；
- 生成或合并资源包（resource pack）：
    <mcroot>/resourcepacks/<pack-name>/assets/minecraft/sounds/<namespace>/<event>.ogg
    <mcroot>/resourcepacks/<pack-name>/assets/minecraft/sounds.json
- （可选）生成最小化数据包（datapack），便于用 /function 测试：
    <mcroot>/saves/<world>/datapacks/<pack-name>_dp/
    data/<namespace>/functions/play.mcfunction （调用 /playsound）
- pack.mcmeta：若资源包/datapack缺失，则自动生成最小可用版本（1.21/1.20 用 pack_format=15）

用法示例：
python3 extract_voice.py \
  --input "/path/to/input.mov" \
  --mcroot "~/Library/Application Support/minecraft" \
  --namespace "pokemon" \
  --pack-name "MySounds" \
  --event "default" \
  --world "MyWorld"
"""

import argparse
import json
import os
from pathlib import Path
from typing import Optional
import shlex
import subprocess
import sys
import datetime

PACK_FORMAT_DEFAULT = 15  # 1.20/1.21 可用

def which(cmd: str) -> Optional[str]:
    from shutil import which as _which
    return _which(cmd)

def run_ffmpeg_to_ogg(src: Path, dst_ogg: Path, bitrate: str = "192k") -> None:
    dst_ogg.parent.mkdir(parents=True, exist_ok=True)
    # 显式使用 libvorbis，确保是 Ogg Vorbis（Minecraft 支持 Vorbis，不支持 Opus）
    cmd = [
        "ffmpeg", "-y",
        "-i", str(src),
        "-vn",
        "-ac", "2",
        "-ar", "48000",
        "-c:a", "libvorbis",
        "-b:a", bitrate,
        str(dst_ogg),
    ]
    print("[ffmpeg]", " ".join(shlex.quote(c) for c in cmd))
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0:
        sys.stderr.write(res.stderr.decode(errors="ignore"))
        raise RuntimeError("ffmpeg 转码失败")

def load_json(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            backup = path.with_suffix(".bak.json")
            path.replace(backup)
            print(f"[warn] 解析 {path.name} 失败，已备份为 {backup.name}，将重建")
    return {}

def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def ensure_resource_pack_mcmeta(path: Path, description: str) -> None:
    if path.exists():
        return
    data = {
        "pack": {
            "pack_format": PACK_FORMAT_DEFAULT,
            "description": description
        }
    }
    save_json(path, data)
    print(f"[ok] 创建资源包 pack.mcmeta：{path}")

def ensure_datapack_mcmeta(path: Path, description: str) -> None:
    if path.exists():
        return
    data = {
        "pack": {
            "pack_format": PACK_FORMAT_DEFAULT,
            "description": description
        }
    }
    save_json(path, data)
    print(f"[ok] 创建数据包 pack.mcmeta：{path}")

def ensure_sounds_event(sounds_json: dict, event_key: str, name_rel: str, stream: bool) -> dict:
    entry = sounds_json.get(event_key, {})
    sounds_list = entry.get("sounds", [])
    # 查重
    found = False
    for it in sounds_list:
        if isinstance(it, str) and it == name_rel:
            found = True
            break
        if isinstance(it, dict) and it.get("name") == name_rel:
            # 同步 stream
            if stream:
                it["stream"] = True
            else:
                it.pop("stream", None)
            found = True
            break
    if not found:
        sounds_list.append({"name": name_rel, **({"stream": True} if stream else {})})
    entry["sounds"] = sounds_list
    sounds_json[event_key] = entry
    return sounds_json

def create_datapack_files(dp_root: Path, namespace: str, event_key_for_cmd: str) -> None:
    """
    生成：
    - data/<namespace>/functions/play.mcfunction
    - data/minecraft/tags/functions/load.json（小提示用，不强制播放）
    """
    # pack.mcmeta 由外层确保
    # 函数：/function <namespace>:play
    func_dir = dp_root / "data" / namespace / "functions"
    func_dir.mkdir(parents=True, exist_ok=True)
    play_fn = func_dir / "play.mcfunction"
    play_fn.write_text(
        f"# 播放测试声音，确保资源包已在客户端启用后再调用\n"
        f"/stopsound @a\n"
        f"/playsound {event_key_for_cmd} master @a ~ ~ ~ 1 1 0\n",
        encoding="utf-8"
    )
    print(f"[ok] 写入函数：{play_fn}")

    # 提示性 load 函数（不直接播放，免得进世界就响）
    init_fn = func_dir / "init.mcfunction"
    init_fn.write_text(
        f'# 世界加载时提示（不自动播放），你可以手动运行：/function {namespace}:play\n'
        f'/tellraw @a ["§a[Datapack] §r已加载。要测试声音，执行：",{{"text":"/function {namespace}:play","color":"yellow"}}]\n',
        encoding="utf-8"
    )
    tag_dir = dp_root / "data" / "minecraft" / "tags" / "functions"
    tag_dir.mkdir(parents=True, exist_ok=True)
    load_tag = tag_dir / "load.json"
    save_json(load_tag, {"values": [f"{namespace}:init"]})
    print(f"[ok] 写入 load 标签：{load_tag}")

def main():
    ap = argparse.ArgumentParser(description="Build resource pack (and optional datapack) for Minecraft sound, from a media file.")
    ap.add_argument("--input", required=True, help="输入媒体文件 (mp3/mp4/mov...)")
    ap.add_argument("--mcroot", required=True, help="Minecraft 根目录（例：~/Library/Application Support/minecraft）")
    ap.add_argument("--namespace", required=True, help="事件前缀/目录名（例：pokemon）")
    ap.add_argument("--event", default="default", help="事件名（默认 default），最终事件为 <namespace>.<event>")
    ap.add_argument("--pack-name", default="MySounds", help="资源包名称（会创建在 <mcroot>/resourcepacks/<pack-name>）")
    ap.add_argument("--world", default=None, help="（可选）要生成数据包的世界名（例：MyWorld）")
    ap.add_argument("--datapack-name", default=None, help="（可选）数据包文件夹名（默认 <pack-name>_dp）")
    ap.add_argument("--no-stream", action="store_true", help="不使用 stream=true（默认开启）")
    ap.add_argument("--bitrate", default="192k", help="OGG 比特率，默认 192k")
    args = ap.parse_args()

    if not which("ffmpeg"):
        print("错误：未找到 ffmpeg，请先安装并加入 PATH。", file=sys.stderr)
        sys.exit(1)

    src = Path(os.path.expanduser(args.input)).resolve()
    if not src.exists():
        print(f"错误：输入文件不存在：{src}", file=sys.stderr)
        sys.exit(1)

    mcroot = Path(os.path.expanduser(args.mcroot)).resolve()
    rp_root = mcroot / "resourcepacks" / args.pack_name
    assets_root = rp_root / "assets" / "minecraft"
    sounds_dir = assets_root / "sounds" / args.namespace
    sounds_json_path = assets_root / "sounds.json"
    ogg_path = sounds_dir / f"{args.event}.ogg"
    ogg_rel_for_json = f"{args.namespace}/{args.event}"
    event_key = f"{args.namespace}.{args.event}"  # 放在 minecraft 命名空间下的事件 key
    use_stream = not args.no_stream

    # 资源包 pack.mcmeta（若不存在则创建）
    ensure_resource_pack_mcmeta(rp_root / "pack.mcmeta", f"{args.pack_name} (auto-generated {datetime.date.today().isoformat()})")

    # 转 OGG
    try:
        run_ffmpeg_to_ogg(src, ogg_path, bitrate=args.bitrate)
        print(f"[ok] 生成 OGG：{ogg_path}")
    except Exception as e:
        print(f"ffmpeg 失败：{e}", file=sys.stderr)
        sys.exit(2)

    # 合并/写入 sounds.json
    sounds_data = load_json(sounds_json_path)
    sounds_data = ensure_sounds_event(sounds_data, event_key, ogg_rel_for_json, stream=use_stream)
    save_json(sounds_json_path, sounds_data)
    print(f"[ok] 更新 sounds.json：{sounds_json_path}")

    # 可选：生成数据包
    if args.world:
        dp_name = args.datapack_name or f"{args.pack_name}_dp"
        dp_root = mcroot / "saves" / args.world / "datapacks" / dp_name
        dp_root.mkdir(parents=True, exist_ok=True)
        ensure_datapack_mcmeta(dp_root / "pack.mcmeta", f"{dp_name} (auto-generated)")

        # event_key 位于 minecraft 命名空间，完整 id 是 minecraft:<namespace>.<event>
        event_id_for_cmd = f"minecraft:{event_key}"
        create_datapack_files(dp_root, args.namespace, event_id_for_cmd)
        print(f"[ok] 数据包已生成：{dp_root}")

    print("\n=== 下一步 ===")
    print(f"1) 在 Minecraft 客户端里启用资源包：{rp_root}")
    print("   （设置 → 资源包 → 移到右侧 → F3+T 重新加载）")
    if args.world:
        print(f"2) 进入世界 {args.world} 后执行：/function {args.namespace}:play 进行测试")
    print(f"   或直接命令：/playsound minecraft:{event_key} master @a ~ ~ ~ 1 1 0")
    print("3) 若仍无声：确认资源包已启用、音量未静音、字幕开着观察是否触发事件；如需可再显式重转为 Vorbis（脚本已用 libvorbis）。")

if __name__ == "__main__":
    main()


# ffmpeg -i input/pokemon2.mp4 -r 20 -c:v libx264 -crf 23 -preset fast -c:a aac -b:a 128k input/pokemon.mp4


# python tools/extract_voice.py --input input/pokemon.mp4 --mcroot ~/Library/Application\ Support/minecraft/ --namespace pokemon
# playsound minecraft:pokemon.default master @a