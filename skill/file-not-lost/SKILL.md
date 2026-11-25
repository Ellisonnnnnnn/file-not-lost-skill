---
name: file-not-lost
description: "文件不迷路：把一个项目目录里的历史产出整理成一张可交互的 HTML 文件地图。当用户说「文件不迷路」「文件地图」「把这些文件整理成索引」「产出索引」「我找不到之前做的文件了」「做个文件导航页」「这个项目产出太乱了」，或要求重新生成/更新已有的文件地图时使用。适用角色：设计师（现行）、产品经理。不用于单纯的目录列表、重命名或清理磁盘。"
description_en: "Build and maintain a single interactive HTML file map for a project's scattered deliverables. Triggered by file-not-lost, file map, output index, organize project files into a navigable index page, or updating an existing map. Roles: designer, product manager."
version: 1.0.0
author: Ellisonnnnnnn
---

# 文件不迷路

把一个项目目录里散落的产出，整理成**一张持续维护的 HTML 文件地图**。用户只需要说「把我这个目录扫成文件地图」，不需要写一行代码。

产物是单文件、零依赖、双击 `file://` 就能用的页面：卡片即文件，多版本的卡点开是扇形展开的历史版本，可以删除、可以撤回。

## 核心约定

**样式是固定的，数据是生成的。** `assets/index-template.html` 里的 CSS 与交互逻辑是成品，任何一次调用都不重写、不微调。你只负责产出一份 `map.json`，注入进去。

**地图是同一张，不是每次新建。** 第二次更新时改的是 `map.json`，页面壳、指纹、样式一律不动。重新生成会把人工写的一句话说明、手动归的组、刻意删掉的卡全部冲掉——这是这套东西最容易毁掉的地方。

**分区跟着角色走，不跟着文件类型走。** 设计师看到的是「主稿 / 模块方案 / 迭代轨迹 / 其他」，PM 看到的是「需求范围 / 流程状态 / 方案对比 / 口径验收」。见 `references/taxonomy-*.md`。

## 五步流程

### 1. 扫描

```bash
python3 scripts/scan_files.py <项目目录> -o candidates.json --include-thumbs
```

它会排除噪声（临时文件、`.git`、`node_modules`、zip）、算好日期与体积、标出哪些是快照、并把「剥掉日期和版本号后同名」的文件归成疑似同族。

**同族候选要拿给人确认。** 脚本给的是候选不是结论，合错比拆错代价大。

### 2. 归类

先判角色，再落区：

- 用户是这个项目的设计师 → `references/taxonomy-designer.md`
- 用户是产品经理 → `references/taxonomy-pm.md`

没有明确信号时问一句，别猜。判区看「这份文件在流程里干什么」，不看扩展名。

归组细节（什么进版本链、什么进轨迹、同族怎么判）见 `references/grouping.md`。

### 3. 写 map.json

严格按 `references/map-schema.md`。三条最容易错的：

- `versions[0]` 必须是**当前版本**——主图、底栏、单版本直达链接都用它
- `name` ≤ 12 字，`note` ≤ 30 字，超了会被截断成省略号（字数预算见 `references/copy-rules.md`）
- 卡片 `id` 全局唯一，浮层靠它反查

### 4. 构建

```bash
python3 scripts/build_map.py map.json <输出目录>/文件地图.html
```

脚本会先校验壳指纹与数据契约。壳被手改过、字段缺失、`tone` 非法，都直接拒绝构建，不产出半个页面。

### 5. 自检

```bash
python3 scripts/check_page.py <输出目录>/文件地图.html
```

六项全过才交付：壳指纹、注入属性、MAP 可解析、数据契约与卡号唯一、标题元信息、链接可达、体积。

**交付前必须真的打开看一眼**（浏览器或预览面板），确认卡片排布、缩略图、扇形展开正常。静态检查通过但视觉错位是有的。

## 维护已有地图

```bash
python3 scripts/scan_files.py <目录> -o candidates.json --include-thumbs
python3 scripts/merge_map.py map.json candidates.json -o merge-report.md --ignore "*.png"
```

报告分四类：未变 / 变更 / 消失 / 新增。按它改 `map.json`，只动该动的地方：

| 情况 | 动作 |
| --- | --- |
| 变更 | 只更新 `size` 和 `date`，**保留 note** |
| 新增 | 能并进已有卡的进 `versions`（放最前），其余按区归类 |
| 消失 | 别直接删卡。先确认是改名还是真删；真删按页面的软删语义处理 |
| 未变 | 不动 |

`note` 是人写的一句话说明，机器永远不覆盖它。

`--ignore` 用来滤掉不该进图的文件（设计稿的 PNG 截图、页面自身、临时导出），可重复。体积比较有 2% 容差、日期只比 `MM-DD`——页面存的是四舍五入后的展示值，逐字节比对会把每个文件都报成变更。

如果报告里大面积出现「日期 A→B」，先看是不是口径问题：图里的 `date` 是人标的日期，脚本取的是文件名里的日期。这类差异可以不改。

## 升级样式壳

只有在**确实需要改视觉或交互**时才碰 `assets/index-template.html`，改完必须重算指纹：

```bash
python3 scripts/rehash_shell.py          # 重算并写回头部注释
python3 scripts/rehash_shell.py --check  # 只比对
```

顺序是：改壳 → 重算指纹 → 重新构建所有用这张壳产出的地图。忘掉这一步，`build_map.py` 会以「壳被改动」为由拒绝构建，这是故意的。

改完必须在真实项目上重建一次，肉眼过三处：卡片排布、扇形展开、删除确认。自检全绿但视觉错位是发生过的。

## 硬规则

1. **不改 CSS、不改交互逻辑。** 需要改样式说明规格要升级，那是改模板 + 更新指纹，不是就地微调。
2. **不删用户的文件。** 页面上的删除只是展示态（内存），没有真实删除磁盘文件的动作。
3. **快照不进主图卡片。** 几十份「改动前」快照只进 03 轨迹区，默认收起。
4. **一个部件一张卡。** 同一部件的 A/B/C/D 方案是这张卡的版本，不是四张卡。
5. **一句话说明必须说「解决了什么」，不是「包含什么」。** 见 `copy-rules.md` 对照表。
6. **交付前清掉预览面板注入的 `data-page-node-id`。** 构建脚本已处理，但如果事后用编辑器保存过，要再跑一次 `check_page.py`。

## 文件地图

```
file-not-lost/
  SKILL.md                      本文件：流程与硬规则
  assets/index-template.html    样式壳（CSS + 渲染器 + 浮层交互 + 指纹）
  scripts/scan_files.py         扫目录 → candidates.json
  scripts/build_map.py          map.json + 壳 → HTML
  scripts/check_page.py         交付前六项自检
  scripts/merge_map.py          增量维护，出差异报告（不改数据）
  scripts/rehash_shell.py       升级壳之后重算指纹
  examples/golden-map.json      真实项目的完整数据块，写 map.json 时对照
  references/
    map-schema.md               数据契约，写 map.json 前必读
    taxonomy-designer.md        设计师四区 + 卡片元信息
    taxonomy-pm.md              产品经理四区 + 卡片元信息
    grouping.md                 同族判据、命名建议、常见错法
    card-spec.md                层叠 2 视觉与交互规格（含容量三级约束）
    copy-rules.md               字数预算、note 写法、状态词表、禁止项
```

## 一次完整的调用

```
用户：把 downloads/智能数据预测 这个目录扫成文件地图

1. scan_files.py 扫描 → 51 个文件，其中 37 份快照，疑似同族 4 组
2. 同族候选给人确认：「核对数据抽屉」4 个文件合成一张卡
3. 判角色 = 设计师，落四区：主稿 1 / 模块方案 6 / 轨迹 37 / 其他 10
4. 写 map.json，note 逐张写「问题」不写「目录」
5. build_map.py → 文件地图.html（74 KB）
6. check_page.py 全过 → 打开截图确认三列排布与扇形正常 → 交付
```

第二次来同一目录时，走「维护」那两步，而不是从头再做一遍。
