#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scan_files.py — 扫一个目录，产出候选清单，供人工/agent 归类后写进 map.json。

用法：
    python3 scan_files.py <目录> [-o candidates.json] [--include-thumbs]

它只做三件事，不做归类判断：
  1. 排除噪声（临时文件、构建产物、备份目录、隐藏文件）
  2. 算日期 / 体积 / 是否快照
  3. 按「去掉日期与版本号后的文件名」猜同族，同族的排在一起供你确认

输出 candidates.json，结构见 references/map-schema.md。
"""
import argparse
import json
import os
import re
import sys
from datetime import datetime

SKIP_DIRS = {
    ".git", ".workbuddy", "node_modules", "__pycache__", ".idea", ".vscode",
    "thumbs", "dist", "build", ".cache",
}
SKIP_FILES = {".DS_Store", "Thumbs.db", "desktop.ini", ".gitignore", ".gitattributes"}
TEMP_PREFIX = ("~$", ".~", "~WRL")

# 这些路径段视为「快照」，不进主图，只在 timeline 里聚合
SNAPSHOT_HINTS = ("迭代快照", "备份", "backup", "backups", "snapshots", "snapshot", "历史版本")

DATE8 = re.compile(r"(20\d{6})")
DATE_TAIL = re.compile(r"-(20\d{2})(\d{2})(\d{2})(?:-(\d{4}))?")
VER = re.compile(r"[-\s]?v(\d+(?:\.\d+)?)", re.I)
SNAP_TAIL = re.compile(r"[-\s]?(前|后|之前|之前版本)$")


def human(n):
    if n < 1024:
        return "%d B" % n
    if n < 1024 * 1024:
        return "%.1f KB" % (n / 1024)
    return "%.2f MB" % (n / 1048576)


def pick_date(name, mtime):
    m = DATE_TAIL.search(name)
    if m:
        return "%s-%s" % (m.group(2), m.group(3)), int(m.group(1) + m.group(2) + m.group(3))
    m = DATE8.search(name)
    if m:
        d = m.group(1)
        return "%s-%s" % (d[4:6], d[6:8]), int(d)
    return mtime.strftime("%m-%d"), int(mtime.strftime("%Y%m%d"))


def base_of(stem):
    """去掉日期、版本号、时间戳、'前/后' 尾巴，得到同族判据。"""
    s = stem
    s = DATE_TAIL.sub("", s)
    s = DATE8.sub("", s)
    s = VER.sub("", s)
    s = SNAP_TAIL.sub("", s)
    s = re.sub(r"[-_\s]+$", "", s)
    return s.lower()


def is_snapshot(rel):
    low = rel.lower()
    return any(h.lower() in low for h in SNAPSHOT_HINTS)


def walk(root, want_thumbs):
    files, skipped = [], []
    thumbs_dir = os.path.join(root, "thumbs")
    have_thumbs = set()
    if os.path.isdir(thumbs_dir):
        for f in os.listdir(thumbs_dir):
            if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                have_thumbs.add(os.path.splitext(f)[0])

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for fn in sorted(filenames):
            if fn in SKIP_FILES or fn.startswith(TEMP_PREFIX):
                skipped.append(os.path.relpath(os.path.join(dirpath, fn), root))
                continue
            if fn.startswith("."):
                skipped.append(os.path.relpath(os.path.join(dirpath, fn), root))
                continue
            if fn.lower().endswith((".zip", ".skill", ".genie")):
                skipped.append(os.path.relpath(os.path.join(dirpath, fn), root))
                continue

            ap = os.path.join(dirpath, fn)
            rel = os.path.relpath(ap, root)
            st = os.stat(ap)
            stem, ext = os.path.splitext(fn)
            date, key = pick_date(stem, datetime.fromtimestamp(st.st_mtime))
            item = {
                "rel": "./" + rel.replace(os.sep, "/"),
                "path": rel.replace(os.sep, "/"),
                "name": stem,
                "file": fn,
                "ext": ext.lstrip(".").upper() or "FILE",
                "bytes": st.st_size,
                "size": human(st.st_size),
                "date": date,
                "date_key": key,
                "mtime": datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M"),
                "snapshot": is_snapshot(rel),
                "base": base_of(stem),
            }
            if want_thumbs and stem in have_thumbs:
                item["thumb"] = stem
            files.append(item)
    return files, skipped


def families(files):
    out = {}
    for f in files:
        if f["snapshot"]:
            continue
        out.setdefault(f["base"], []).append(f)
    rows = []
    for base, group in sorted(out.items(), key=lambda kv: -len(kv[1])):
        group.sort(key=lambda x: (-x["date_key"], x["file"]))
        rows.append({"base": base, "count": len(group),
                     "files": [g["path"] for g in group]})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("-o", "--out", default="candidates.json")
    ap.add_argument("--include-thumbs", action="store_true",
                    help="把已存在的 thumbs/*.jpg 关联到同名文件")
    a = ap.parse_args()

    if not os.path.isdir(a.root):
        print("✗ 不是目录：%s" % a.root, file=sys.stderr)
        sys.exit(1)

    files, skipped = walk(os.path.abspath(a.root), a.include_thumbs)
    main_files = [f for f in files if not f["snapshot"]]
    snaps = [f for f in files if f["snapshot"]]

    data = {
        "root": os.path.abspath(a.root),
        "scanned_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "summary": {
            "files": len(files),
            "main": len(main_files),
            "snapshots": len(snaps),
            "bytes": sum(f["bytes"] for f in files),
            "size": human(sum(f["bytes"] for f in files)),
        },
        "families": families(files),
        "files": files,
        "skipped": skipped,
    }
    json.dump(data, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    print("✓ %s" % a.out)
    print("  %d 个文件（主图 %d · 快照 %d）· %s · 跳过 %d"
          % (len(files), len(main_files), len(snaps), data["summary"]["size"], len(skipped)))
    multi = [r for r in data["families"] if r["count"] > 1]
    if multi:
        print("  疑似同族 %d 组（需要你确认是否合成一张卡）：" % len(multi))
        for r in multi[:8]:
            print("    %-40s %d 个" % (r["base"][:40], r["count"]))


if __name__ == "__main__":
    main()
