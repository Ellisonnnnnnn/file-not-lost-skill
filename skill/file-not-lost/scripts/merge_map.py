#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
merge_map.py — 增量维护：旧图 vs 磁盘现状，出差异报告。不自动改数据。

用法：
    python3 merge_map.py map.json candidates.json [-o report.md]

为什么要它：第二次更新最容易出事——重新生成会把人工写的一句话说明、
手动的归组、刻意删掉的卡全部冲掉。所以这里的规则是「只报告，人来定」：

    keep      旧图有、磁盘有、大小日期都没变      → 不用动
    changed   旧图有、磁盘有、但大小或日期变了    → 只改 size/date，不要动 note
    missing   旧图有、磁盘没有了                  → 别直接删卡，先看是不是改名或合并了
    new       磁盘有、旧图没有                    → 待归类
"""
import argparse
import fnmatch
import json
import os
import re
import sys
import urllib.parse

MARK = {"keep": "=", "changed": "~", "missing": "-", "new": "+"}

SIZE_RE = re.compile(r"([\d.]+)\s*(B|KB|MB|GB)", re.I)
UNIT = {"B": 1, "KB": 1024, "MB": 1048576, "GB": 1073741824}


def load(p):
    return json.load(open(p, encoding="utf-8"))


def norm(p):
    """统一路径：去 ./ 前缀、解百分号编码、正斜杠。href 里常带编码，磁盘路径没有。"""
    p = urllib.parse.unquote(p or "").replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    return p


def to_bytes(s):
    """把 "1093 KB" / "1.09 MB" / "670 B" 解析成字节数；解析不了返回 None。"""
    if isinstance(s, (int, float)):
        return float(s)
    m = SIZE_RE.search(str(s or ""))
    if not m:
        return None
    return float(m.group(1)) * UNIT[m.group(2).upper()]


def same_size(a, b):
    """体积比较带容差：页面记的是四舍五入后的展示值，不可能逐字节相同。"""
    x, y = to_bytes(a), to_bytes(b)
    if x is None or y is None:
        return str(a) == str(b)
    return abs(x - y) <= max(1024, x * 0.02)


def norm_date(d):
    """11-19 / 2026-11-19 / 11-19 10:22 都收敛成 MM-DD。"""
    m = re.search(r"(?:20\d{2}-)?(\d{2})-(\d{2})", str(d or ""))
    return "%s-%s" % (m.group(1), m.group(2)) if m else str(d or "")


def old_index(m):
    """path → (card_id, card_name, version)"""
    idx = {}
    def walk(c):
        for v in c.get("versions") or []:
            href = v.get("href", "")
            if href.startswith("./"):
                idx[norm(href)] = {"card": c.get("id"), "name": c.get("name"), "v": v}
    for s in m.get("sections") or []:
        if s.get("item"):
            walk(s["item"])
        for c in s.get("items") or []:
            walk(c)
        for g in s.get("groups") or []:
            for c in g.get("items") or []:
                walk(c)
    return idx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("map_json")
    ap.add_argument("candidates_json")
    ap.add_argument("-o", "--out", default="merge-report.md")
    ap.add_argument("--ignore", action="append", default=[],
                    help="忽略匹配的文件（fnmatch，按相对路径）。可重复，如 --ignore '*.png'")
    a = ap.parse_args()

    m = load(a.map_json)
    cand = load(a.candidates_json)
    idx = {norm(p): info for p, info in old_index(m).items()}
    disk = {norm(f["path"]): f for f in cand["files"] if not f["snapshot"]}

    ignored = [p for p in disk if any(fnmatch.fnmatch(p, pat) for pat in a.ignore)]
    for p in ignored:
        disk.pop(p, None)

    keep, changed, missing, new = [], [], [], []
    for p, info in idx.items():
        if p not in disk:
            missing.append((p, info))
            continue
        f = disk[p]
        ov = info["v"]
        dsame = same_size(ov.get("size"), f["size"])
        tsame = norm_date(ov.get("date")) == norm_date(f["date"])
        if dsame and tsame:
            keep.append((p, info))
        else:
            changed.append((p, info, f, ov.get("size"), ov.get("date"),
                            dsame, tsame))
    for p, f in disk.items():
        if p not in idx:
            new.append((p, f))

    lines = ["# 增量报告", "",
             "旧图 %d 个文件版本 · 磁盘 %d 个文件" % (len(idx), len(disk)), ""]
    for title, rows in (("新增（磁盘有、图里没有）", new),
                        ("变更（大小或日期变了）", changed),
                        ("消失（图里有、磁盘没有）", missing)):
        lines.append("## %s · %d" % (title, len(rows)))
        if not rows:
            lines.append("")
            continue
        for r in rows:
            if title.startswith("新增"):
                p, f = r
                lines.append("- `%s` — %s · %s · %s" % (p, f["name"], f["date"], f["size"]))
            elif title.startswith("变更"):
                p, info, f, os_, od, dsame, tsame = r
                bits = []
                if not tsame:
                    bits.append("日期 %s→%s" % (od or "—", f["date"]))
                if not dsame:
                    old = os_ if to_bytes(os_) is not None else "（非体积值：%s）" % (os_ or "空")
                    bits.append("体积 %s→%s" % (old, f["size"]))
                hint = "日期优先以文件名为准；若图里记的是人工标注日，可不改" if not tsame else "只改数字，别动 note"
                lines.append("- `%s` — 卡「%s」 %s（%s）"
                             % (p, info["name"], " · ".join(bits), hint))
            else:
                p, info = r
                lines.append("- `%s` — 卡「%s」，确认是改名还是真删；真删走页面软删语义" % (p, info["name"]))
        lines.append("")

    lines += ["## 建议动作", ""]
    if new:
        lines.append("1. 把 %d 个新文件归到合适的分区/卡片；同族的并进已有卡的 versions（放在最前）" % len(new))
    if changed:
        lines.append("1. 只更新 size / date 字段，保留 note 与 noteLocked")
    if missing:
        lines.append("1. 消失的文件先在页面上软删（保留 7 天语义），确认后再从数据里移除")
    if not (new or changed or missing):
        lines.append("磁盘与图完全一致，无需更新。")

    open(a.out, "w", encoding="utf-8").write("\n".join(lines))

    print("✓ %s" % a.out)
    print("  未变 %d · 变更 %d · 消失 %d · 新增 %d"
          % (len(keep), len(changed), len(missing), len(new)))
    if missing:
        print("  ! 消失 %d 个，先确认是改名/合并，不要直接删卡" % len(missing))
        for p, info in missing[:6]:
            print("    - %s" % p)


if __name__ == "__main__":
    main()
