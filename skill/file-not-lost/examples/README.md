# examples

## golden-map.json

真实项目（智能数据预测 · 设计师视角）的完整数据块，可当作写 `map.json` 时的参照。

- 5 个区：01 主稿（lead）· 02 产品原型（grid）· 03 模块方案（grid）· 04 迭代轨迹（timeline）· 05 其他文件（subgroups）
- 02 原型区是空的：这个项目由需求方口头对齐、没有产出原型稿，正好当作「空区写法」的实例
- 17 张卡 · 24 个文件版本 · 38 份快照
- 覆盖了几种边界情况：单版本卡、4 版本卡、5 个文件的脚本组合卡、带 `+N` 折叠入口、无缩略图走扩展名占位的 CSV/TXT/PY

**它的 `href` / `thumb` 是相对原项目目录的**，拿去别处直接构建会链接全红。当格式参考看，不要当可运行样例。

想验证构建链路，用一个临时目录造两个小文件即可：

```bash
mkdir -p /tmp/fl-demo && cd /tmp/fl-demo
echo '<h1>v1</h1>' > demo-v1-20261101.html
echo '<h1>v2</h1>' > demo-v2-20261102.html
python3 <skill>/scripts/scan_files.py . -o cand.json
# 按 references/map-schema.md 手写 map.json（1 个区 1 张卡 2 个版本）
python3 <skill>/scripts/build_map.py map.json 文件地图.html
python3 <skill>/scripts/check_page.py 文件地图.html
```
