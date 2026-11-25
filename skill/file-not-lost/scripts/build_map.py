#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_map.py — 把 map.json 注入样式壳，产出「文件不迷路」索引页。

用法：
    python3 build_map.py map.json out.html
    python3 build_map.py map.json out.html --force

硬规则：
  1. 只替换 <title> 和 var MAP = ...; 两处，其余字节不动。
  2. 模板声明的 css/js 指纹与实际不符 → 拒绝构建（说明壳被手改过）。
  3. 构建前校验数据契约，字段缺失或类型不对 → 报错退出，不产出半个页面。
"""
import argparse
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.normpath(os.path.join(HERE, "..", "assets", "index-template.html"))

TONES = {"blue", "green", "gray", "orange", "red"}
TYPES = {"lead", "grid", "timeline", "subgroups"}


# ---------------------------------------------------------------- 模板指纹
def shell_parts(tpl: str):
    """返回 (style 段, 交互段) 原文，用于指纹比对。"""
    css = re.search(r"<style>.*?</style>", tpl, re.S)
    js = re.search(r"/\* ==INTERACT-BEGIN== \*/(.*?)/\* ==INTERACT-END== \*/", tpl, re.S)
    return (css.group(0) if css else None), (js.group(1).strip("\n") if js else None)


def declared_sha(tpl: str):
    css = re.search(r"css-sha256:\s*([0-9a-f]{16})", tpl)
    js = re.search(r"js-sha256:\s*([0-9a-f]{16})", tpl)
    return (css.group(1) if css else None), (js.group(1) if js else None)


def verify_shell(tpl: str):
    css, js = shell_parts(tpl)
    if not css or not js:
        die("模板结构异常：找不到 <style> 或 交互段标记")
    css_sha = hashlib.sha256(css.encode()).hexdigest()[:16]
    js_sha = hashlib.sha256(js.encode()).hexdigest()[:16]
    d_css, d_js = declared_sha(tpl)
    bad = []
    if d_css and d_css != css_sha:
        bad.append("CSS 段实际 %s ≠ 声明 %s" % (css_sha, d_css))
    if d_js and d_js != js_sha:
        bad.append("交互段实际 %s ≠ 声明 %s" % (js_sha, d_js))
    if bad:
        die("样式壳被改动过，构建已中止：\n  " + "\n  ".join(bad)
            + "\n如确属有意升级壳，请同步更新模板头部指纹后重试。")
    return css_sha, js_sha


def die(msg):
    print("✗ " + msg, file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------- 数据校验
def need(obj, key, where, typ=None):
    if key not in obj or obj[key] in (None, ""):
        die("%s 缺少字段 `%s`" % (where, key))
    if typ and not isinstance(obj[key], typ):
        die("%s 的 `%s` 类型应为 %s" % (where, key, typ.__name__))
    return obj[key]


def check_version(v, where):
    need(v, "title", where)
    need(v, "href", where)
    if "date" not in v:
        v["date"] = ""
    if "size" not in v:
        v["size"] = ""
    if v.get("tone") and v["tone"] not in TONES:
        die("%s 的 tone=%s 不在允许值 %s" % (where, v["tone"], sorted(TONES)))


def check_card(c, where, ids):
    need(c, "id", where)
    need(c, "name", where)
    if c["id"] in ids:
        die("卡片 id 重复：%s" % c["id"])
    ids.add(c["id"])
    if c.get("tone") and c["tone"] not in TONES:
        die("%s 的 tone=%s 不在允许值 %s" % (where, c["tone"], sorted(TONES)))
    vs = need(c, "versions", where, list)
    if not vs:
        die("%s 的 versions 为空" % where)
    for i, v in enumerate(vs):
        check_version(v, "%s.versions[%d]" % (where, i))


def check_map(m):
    meta = need(m, "meta", "root", dict)
    for k in ("product", "project", "sub"):
        need(meta, k, "meta")
    if not isinstance(meta.get("breadcrumb"), list) or not meta["breadcrumb"]:
        die("meta.breadcrumb 必须是非空数组")
    for i, q in enumerate(meta.get("quick") or []):
        need(q, "label", "meta.quick[%d]" % i)
        need(q, "href", "meta.quick[%d]" % i)

    secs = need(m, "sections", "root", list)
    if not secs:
        die("sections 为空")
    ids, sec_ids = set(), set()
    for si, s in enumerate(secs):
        w = "sections[%d]" % si
        need(s, "id", w)
        need(s, "no", w)
        need(s, "title", w)
        need(s, "type", w)
        if s["type"] not in TYPES:
            die("%s 的 type=%s 不在允许值 %s" % (w, s["type"], sorted(TYPES)))
        if s["id"] in sec_ids:
            die("section id 重复：%s" % s["id"])
        sec_ids.add(s["id"])

        t = s["type"]
        if t == "lead":
            check_card(need(s, "item", w, dict), w + ".item", ids)
            side = need(s, "side", w, dict)
            need(side, "title", w + ".side")
        elif t == "grid":
            for i, c in enumerate(need(s, "items", w, list)):
                check_card(c, "%s.items[%d]" % (w, i), ids)
        elif t == "timeline":
            for i, d in enumerate(need(s, "days", w, list)):
                need(d, "date", "%s.days[%d]" % (w, i))
                for j, sn in enumerate(d.get("snaps") or []):
                    need(sn, "title", "%s.days[%d].snaps[%d]" % (w, i, j))
                    need(sn, "href", "%s.days[%d].snaps[%d]" % (w, i, j))
        elif t == "subgroups":
            gid = set()
            for i, g in enumerate(need(s, "groups", w, list)):
                gw = "%s.groups[%d]" % (w, i)
                need(g, "id", gw)
                need(g, "title", gw)
                if g["id"] in gid:
                    die("子分组 id 重复：%s" % g["id"])
                gid.add(g["id"])
                for j, c in enumerate(g.get("items") or []):
                    check_card(c, "%s.items[%d]" % (gw, j), ids)
    return ids


# ---------------------------------------------------------------- 注入
def inject(tpl: str, m: dict, title: str) -> str:
    data = json.dumps(m, ensure_ascii=False, indent=2)
    # 防止数据里的 </script> 提前闭合脚本块
    data = data.replace("</", "<\\/")

    if tpl.count("__MAP_JSON__") != 1:
        die("模板里 __MAP_JSON__ 占位符数量异常")
    if tpl.count("__PAGE_TITLE__") < 1:
        die("模板里缺少 __PAGE_TITLE__ 占位符")

    out = tpl.replace("__MAP_JSON__", data)
    # 只替换 <title> 内的占位，头部注释里的说明保留
    out = out.replace("<title>__PAGE_TITLE__</title>", "<title>%s</title>" % escape_html(title))
    return out


def escape_html(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def strip_injected(html: str) -> str:
    """预览面板会给 DOM 注入属性，落盘前清掉。"""
    return re.sub(r'\s*data-(page-node-id|pnid-children)="[^"]*"', "", html)


def stats(m: dict):
    cards = files = 0
    def walk(c):
        nonlocal cards, files
        cards += 1
        files += len(c.get("versions") or [])
    for s in m["sections"]:
        if s.get("item"): walk(s["item"])
        for c in s.get("items") or []: walk(c)
        for g in s.get("groups") or []:
            for c in g.get("items") or []: walk(c)
    snaps = sum(len(d.get("snaps") or []) for s in m["sections"] for d in s.get("days") or [])
    return cards, files, snaps


def main():
    ap = argparse.ArgumentParser(description="把 map.json 注入样式壳，生成索引页")
    ap.add_argument("map_json")
    ap.add_argument("out_html")
    ap.add_argument("--template", default=TPL)
    ap.add_argument("--force", action="store_true", help="壳指纹不符也强行构建（不推荐）")
    a = ap.parse_args()

    if not os.path.exists(a.template):
        die("找不到模板：%s" % a.template)
    tpl = open(a.template, encoding="utf-8").read()

    try:
        verify_shell(tpl)
    except SystemExit:
        if not a.force:
            raise
        print("! 已按 --force 跳过指纹校验")

    try:
        m = json.load(open(a.map_json, encoding="utf-8"))
    except json.JSONDecodeError as e:
        die("map.json 不是合法 JSON：%s" % e)

    check_map(m)
    title = m["meta"].get("title") or "%s（%s）· 文件地图" % (m["meta"]["product"], m["meta"]["project"])
    html = strip_injected(inject(tpl, m, title))

    os.makedirs(os.path.dirname(os.path.abspath(a.out_html)) or ".", exist_ok=True)
    open(a.out_html, "w", encoding="utf-8").write(html)

    cards, files, snaps = stats(m)
    print("✓ 已生成 %s" % a.out_html)
    print("  %d 张卡片 · %d 个文件版本 · %d 份快照 · %.0f KB"
          % (cards, files, snaps, len(html.encode()) / 1024))


if __name__ == "__main__":
    main()
