#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_page.py — 交付前自检。任何一项 fail 即退出码 1，不许交付。

用法：
    python3 check_page.py out.html

检查七项：
  1. 样式壳指纹未被改动（CSS 段 / 交互段 sha256 与模板声明一致）
  2. 没有预览面板注入的 data-page-node-id
  3. 能找到 var MAP 数据块且 JSON 合法
  4. 数据契约完整（卡片 id 唯一、版本非空、tone 合法）
  5. 所有相对链接（含缩略图）在磁盘上真实存在
  6. 章节编号连续、锚点唯一
  7. 页面标题与 meta 对得上
"""
import hashlib
import json
import os
import re
import sys
import urllib.parse

OK, FAIL, WARN = "✓", "✗", "!"


def load(html_path):
    return open(html_path, encoding="utf-8").read()


def extract_map(html):
    """模板头部注释里也会出现 `var MAP = ...` 字样，所以逐个尝试直到解析成功。"""
    for m in re.finditer(r"^var MAP = (\{.*?\});\s*$", html, re.S | re.M):
        raw = m.group(1).replace("<\\/", "</")
        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            last = e
    # 退一步：不限定行首，宽松匹配
    for m in re.finditer(r"var MAP = (\{\s*\n\s*\"meta\")", html):
        start = m.start(1)
        depth = 0
        for i in range(start, len(html)):
            ch = html[i]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(html[start:i + 1].replace("<\\/", "</"))
                    except json.JSONDecodeError as e:
                        last = e
                    break
    print("  JSON 解析失败：%s" % locals().get("last", "找不到数据块"))
    return None


def shell_sha(html):
    css = re.search(r"<style>.*?</style>", html, re.S)
    js = re.search(r"/\* ==INTERACT-BEGIN== \*/(.*?)/\* ==INTERACT-END== \*/", html, re.S)
    if not css or not js:
        return None, None
    return (hashlib.sha256(css.group(0).encode()).hexdigest()[:16],
            hashlib.sha256(js.group(1).strip("\n").encode()).hexdigest()[:16])


def collect_hrefs(html, data):
    hrefs = set()
    if data:
        def walk(c):
            for v in c.get("versions") or []:
                if v.get("href"):
                    hrefs.add(v["href"])
                if v.get("thumb"):
                    hrefs.add("./thumbs/%s.jpg" % urllib.parse.quote(v["thumb"]))
        for s in data.get("sections") or []:
            if s.get("item"):
                walk(s["item"])
            for c in s.get("items") or []:
                walk(c)
            for g in s.get("groups") or []:
                for c in g.get("items") or []:
                    walk(c)
            for d in s.get("days") or []:
                for sn in d.get("snaps") or []:
                    if sn.get("href"):
                        hrefs.add(sn["href"])
        for q in (data.get("meta") or {}).get("quick") or []:
            if q.get("href"):
                hrefs.add(q["href"])
    for h in re.findall(r'(?:href|src)="([^"]+)"', html):
        if h.startswith("./"):
            hrefs.add(h)
    return hrefs


def main():
    if len(sys.argv) < 2:
        print("用法：python3 check_page.py out.html")
        sys.exit(2)
    path = sys.argv[1]
    if not os.path.exists(path):
        print("%s 文件不存在：%s" % (FAIL, path))
        sys.exit(1)

    html = load(path)
    base = os.path.dirname(os.path.abspath(path))
    problems, warnings = [], []

    # 1 指纹
    d_css = re.search(r"css-sha256:\s*([0-9a-f]{16})", html)
    d_js = re.search(r"js-sha256:\s*([0-9a-f]{16})", html)
    a_css, a_js = shell_sha(html)
    if not a_css:
        problems.append("找不到 <style> 或交互段标记，壳结构异常")
    else:
        if d_css and d_css.group(1) != a_css:
            problems.append("CSS 段被改动（%s ≠ %s）" % (a_css, d_css.group(1)))
        if d_js and d_js.group(1) != a_js:
            problems.append("交互段被改动（%s ≠ %s）" % (a_js, d_js.group(1)))
    print("  %s 样式壳指纹 %s / %s" % (OK if a_css else FAIL, a_css, a_js))

    # 2 注入属性
    inj = re.findall(r"data-(?:page-node-id|pnid-children)=", html)
    if inj:
        problems.append("含 %d 处预览面板注入属性" % len(inj))
    print("  %s 无注入属性" % (OK if not inj else FAIL))

    # 3 / 4 数据块
    data = extract_map(html)
    if not data:
        problems.append("找不到合法的 var MAP 数据块")
        print("  %s MAP 数据块" % FAIL)
    else:
        ids, tones = set(), {"blue", "green", "gray", "orange", "red"}
        cards = files = 0
        dup = []

        def walk(c, where):
            nonlocal cards, files
            cards += 1
            cid = c.get("id")
            if not cid:
                problems.append("%s 缺 id" % where)
            elif cid in ids:
                dup.append(cid)
            ids.add(cid)
            if c.get("tone") and c["tone"] not in tones:
                problems.append("%s 的 tone 非法：%s" % (where, c["tone"]))
            vs = c.get("versions") or []
            if not vs:
                problems.append("%s 无 versions" % where)
            files += len(vs)
            for v in vs:
                if not v.get("href") or not v.get("title"):
                    problems.append("%s 有版本缺 href/title" % where)
        for s in data.get("sections") or []:
            if s.get("item"):
                walk(s["item"], "lead")
            for c in s.get("items") or []:
                walk(c, "grid")
            for g in s.get("groups") or []:
                for c in g.get("items") or []:
                    walk(c, "subgroup/" + str(g.get("id")))
        if dup:
            problems.append("卡片 id 重复：%s" % ", ".join(sorted(set(dup))))
        print("  %s 数据块：%d 张卡 · %d 个版本" % (OK, cards, files))

        # 6 章节编号
        nos = [s.get("no") for s in data.get("sections") or []]
        if nos != ["%02d" % (i + 1) for i in range(len(nos))]:
            warnings.append("章节编号不连续：%s" % nos)
        sids = [s.get("id") for s in data.get("sections") or []]
        if len(set(sids)) != len(sids):
            problems.append("section id 重复")

        # 7 标题
        t = re.search(r"<title>(.*?)</title>", html, re.S)
        meta = data.get("meta") or {}
        if t and meta.get("project") and meta["project"] not in t.group(1):
            warnings.append("页面标题里没有项目名「%s」" % meta["project"])
        for k in ("product", "project", "sub"):
            if not meta.get(k):
                problems.append("meta.%s 为空" % k)
        print("  %s 标题 / 元信息" % (OK if not problems else WARN))

    # 5 链接
    hrefs = collect_hrefs(html, data)
    local = [h for h in hrefs if not re.match(r"^(https?:|mailto:|#|javascript:|data:)", h)]
    missing = []
    for h in sorted(local):
        rel = urllib.parse.unquote(h[2:] if h.startswith("./") else h)
        rel = rel.split("#")[0].split("?")[0]
        if not os.path.exists(os.path.join(base, rel)):
            missing.append(h)
    if missing:
        problems.append("%d 个链接指向不存在的文件：\n      %s"
                        % (len(missing), "\n      ".join(missing[:12])))
    print("  %s 链接 %d 个（本地 %d），缺失 %d"
          % (OK if not missing else FAIL, len(hrefs), len(local), len(missing)))

    print("  %s 文件体积 %.0f KB" % (OK, os.path.getsize(path) / 1024))

    for w in warnings:
        print("  %s %s" % (WARN, w))
    if problems:
        print("\n%s 自检未通过（%d 项）：" % (FAIL, len(problems)))
        for p in problems:
            print("  - %s" % p)
        sys.exit(1)

    print("\n%s 自检全部通过，可交付。" % OK)


if __name__ == "__main__":
    main()
