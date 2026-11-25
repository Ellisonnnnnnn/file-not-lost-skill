# 文件不迷路 Skill

文件不迷路 —— 文件不是孤立的附件，而是一份文件带着它的历史版本一起走。

> 仓库名使用 `file-not-lost-skill`：GitHub 不支持非 ASCII 字符作为仓库名，中文名仅作项目名称使用。

## 目录结构

| 路径 | 说明 |
| --- | --- |
| `skill/file-not-lost/` | **文件不迷路 Skill 本体**：样式壳 + 四个脚本 + 数据契约 |
| `downloads/智能数据预测-方案索引/智能数据预测/` | 方案索引与各版本设计稿（HTML，单文件零依赖） |
| `downloads/智能数据预测-方案索引/智能数据预测/迭代快照/` | 按日期归档的历史快照 |
| `downloads/智能数据预测-方案索引/智能数据预测/需求输入/` | 需求说明与原始输入 |
| `downloads/智能数据预测-方案索引/智能数据预测/参考/` | 参考稿与素材 |

## Skill 怎么用

```bash
cp -R skill/file-not-lost ~/.workbuddy/skills/     # 装到本机 skill 目录
```

装好后对 agent 说「把这个目录扫成文件地图」即可，它不会要求你写任何代码。

| 脚本 | 作用 |
| --- | --- |
| `scripts/scan_files.py` | 扫目录，排除噪声，算日期体积，猜同族 |
| `scripts/build_map.py` | map.json + 样式壳 → 单文件 HTML |
| `scripts/check_page.py` | 交付前六项自检（指纹 / 注入 / 数据 / 链接 / 体积） |
| `scripts/merge_map.py` | 增量维护，出差异报告，不自动改数据 |
| `scripts/rehash_shell.py` | 升级样式壳后重算指纹 |

详细流程见 `skill/file-not-lost/SKILL.md`，数据格式见 `references/map-schema.md`。

## 入口

| 文件 | 说明 |
| --- | --- |
| `智能数据预测-本对话产出索引-v2-20261125.html` | 产出索引 v2，全站「层叠 2」卡片 |
| `智能数据预测-文件模块优化方案-20261124.html` | 文件模块四方案对比（A/B/C/D） |

## 多机协作

```bash
git clone https://github.com/Ellisonnnnnnn/file-not-lost-skill.git
cd file-not-lost-skill
git config core.quotepath false   # 中文路径按原样显示，不转义成 \346\231\...
```

- 拉取约 44 MB（含 37 份迭代快照），首次 clone 稍慢属正常。
- 换机后先 `git pull --rebase` 再动手，提交前 `git status` 确认只含本次改动。
- 归档用带注释标签：`git tag -a v2.1.0 -m "..." && git push --tags`，版本号延续现有序列。
- 不随仓库同步：`.workbuddy/`（会话与记忆）、`*.zip`（打包产物）、`tools/shots/`（调试截图）。
  跨机器要复用的结论请写进 README 或 `docs/`，别只留在本地记忆里。

## 版本记录

| 版本 | 日期 | 内容 |
| --- | --- | --- |
| `v3.0.0` | 2026-11-25 | 文件不迷路 Skill v1.0：样式壳固化 + 数据契约 + 扫描/构建/自检/增量四脚本；用真实项目验证，重建页与原 v2 逐字一致 |
| `v2.0.0` | 2026-11-25 | 产出索引全站改为「层叠 2」卡片体系；标题更名「文件不迷路（项目名）」 |
| `v1.2.3` | 2026-11-23 | 上一版归档（`智能数据预测-方案索引-20261123-v1.2.3.zip`） |
