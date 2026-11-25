#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rehash_shell.py — 重算样式壳指纹，写回模板头部注释。

只在「有意升级壳」时使用：改完 assets/index-template.html 的样式或交互段后，
跑一次这个脚本，把头部声明的 css-sha256 / js-sha256 更新为实际值。
平时构建（build_map.py）不调用它，指纹不符会被拒绝。

用法：
    python3 rehash_shell.py                 # 重算并写回
    python3 rehash_shell.py --check         # 只比对，不写回；不符退出码 1
"""
import argparse
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.normpath(os.path.join(HERE, "..", "assets", "index-template.html"))


def parts(tpl):
    css = re.search(r"<style>.*?</style>", tpl, re.S)
    js = re.search(r"/\* ==INTERACT-BEGIN== \*/(.*?)/\* ==INTERACT-END== \*/", tpl, re.S)
    if not css or not js:
        print("✗ 找不到 <style> 或交互段标记", file=sys.stderr)
        sys.exit(1)
    return css.group(0), js.group(1).strip("\n")


def shas(tpl):
    css, js = parts(tpl)
    return (hashlib.sha256(css.encode()).hexdigest()[:16],
            hashlib.sha256(js.encode()).hexdigest()[:16])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", default=TPL)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()

    tpl = open(a.template, encoding="utf-8").read()
    css, js = shas(tpl)
    d_css = re.search(r"css-sha256:\s*([0-9a-f]{16})", tpl)
    d_js = re.search(r"js-sha256:\s*([0-9a-f]{16})", tpl)
    ok = d_css and d_js and d_css.group(1) == css and d_js.group(1) == js

    if ok:
        print("✓ 指纹一致  css %s  js %s" % (css, js))
        return

    if a.check:
        print("✗ 指纹不符：css 实际 %s / 声明 %s；js 实际 %s / 声明 %s"
              % (css, d_css.group(1) if d_css else "-", js, d_js.group(1) if d_js else "-"),
              file=sys.stderr)
        sys.exit(1)

    out = tpl
    out = re.sub(r"css-sha256:\s*[0-9a-f]{16}", "css-sha256: " + css, out, count=1)
    if d_js:
        out = re.sub(r"js-sha256:\s*[0-9a-f]{16}", "js-sha256: " + js, out, count=1)
    else:
        out = out.replace("css-sha256: " + css, "css-sha256: " + css + "\n     js-sha256: " + js, 1)
    open(a.template, "w", encoding="utf-8").write(out)
    print("✓ 已写回指纹  css %s  js %s" % (css, js))


if __name__ == "__main__":
    main()
