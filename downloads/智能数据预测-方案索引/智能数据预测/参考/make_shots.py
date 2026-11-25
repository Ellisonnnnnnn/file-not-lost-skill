#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_shots.py — 索引页预览图生成器（hash 增量）

用法：
    python3 make_shots.py [--node /path/to/node]

机制：
    1. 扫描本目录的 智能数据预测-*.html 方案稿 + 主稿（不含迭代快照/备份目录）
    2. 每个文件算 sha1，与 shots.json 记录对比：
       - hash 未变且截图存在 -> 跳过
       - hash 变化或截图缺失 -> 调用 shot.js 重新截图
    3. thumbs-manual/ 里有同名 png/jpg 时优先使用（手动覆盖，处理交互态截图）
    4. 输出到 thumbs/<源文件基名>.jpg（宽 800，质量 82）

依赖：node + playwright（在本目录的 ../tools/shots 下安装）
"""
import os, sys, json, hashlib, subprocess, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                      # 智能数据预测/
# tools/shots 在工作区（downloads 的上一级）下的 tools/shots；优先用环境变量覆盖
_default_tools = os.path.normpath(os.path.join(ROOT, '..', '..', '..', 'tools', 'shots'))
TOOLS = os.environ.get('SHOTS_TOOLS', _default_tools)
MANIFEST = os.path.join(HERE, 'shots.json')
THUMBS = os.path.join(ROOT, 'thumbs')
MANUAL = os.path.join(ROOT, 'thumbs-manual')


def sha1(path):
    h = hashlib.sha1()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def targets():
    out = []
    for name in sorted(os.listdir(ROOT)):
        if not name.endswith('.html'):
            continue
        if '索引' in name:
            continue
        out.append(name)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--node', default=os.environ.get('NODE', 'node'))
    args = ap.parse_args()

    os.makedirs(THUMBS, exist_ok=True)
    manifest = {}
    if os.path.exists(MANIFEST):
        manifest = json.load(open(MANIFEST, encoding='utf-8'))

    changed, skipped, manual = [], [], []
    for name in targets():
        src = os.path.join(ROOT, name)
        base = os.path.splitext(name)[0]
        out_jpg = os.path.join(THUMBS, base + '.jpg')
        # 手动覆盖
        manual_file = None
        for ext in ('.png', '.jpg'):
            p = os.path.join(MANUAL, base + ext)
            if os.path.exists(p):
                manual_file = p
                break
        if manual_file:
            manual.append(name)
            continue
        h = sha1(src)
        rec = manifest.get(name, {})
        if rec.get('sha1') == h and os.path.exists(out_jpg):
            skipped.append(name)
            continue
        changed.append((name, h))

    print(f'共 {len(targets())} 个目标 | 需重截 {len(changed)} | 跳过 {len(skipped)} | 手动 {len(manual)}')

    if changed:
        env = dict(os.environ)
        env['PLAYWRIGHT_BROWSERS_PATH'] = os.path.join(TOOLS, 'browsers')
        for name, h in changed:
            src = os.path.join(ROOT, name)
            base = os.path.splitext(name)[0]
            out_jpg = os.path.join(THUMBS, base + '.jpg')
            r = subprocess.run(
                [args.node, os.path.join(TOOLS, 'shot.js'), src, out_jpg],
                env=env, capture_output=True, text=True)
            if r.returncode == 0:
                manifest[name] = {'sha1': h, 'thumb': 'thumbs/' + base + '.jpg'}
                print('  OK', name)
            else:
                print('  FAIL', name, r.stderr.strip()[:160])

    json.dump(manifest, open(MANIFEST, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)
    print('清单已更新:', MANIFEST)


if __name__ == '__main__':
    main()
