---
name: dongchedi-scraper
description: 从懂车帝批量抓取车型配置参数，支持任意车型搜索、竞品分析、智能合并更新，存入 Obsidian。Use when user mentions "懂车帝", "车型配置", "汽车参数", "竞品分析", "dongchedi", or wants to scrape car specifications.
---

# 懂车帝车型配置抓取

从懂车帝 (dongchedi.com) 批量抓取车型配置参数，智能合并存入 Obsidian。

## 本次沉淀能力

本 skill 当前已经固化的核心能力如下：

1. **单入口品牌抓取**
   - 用 `scripts/run_brand_pipeline.py` 输入品牌名，串起搜索 → 车型 → 配置 → 参数 → 入库
2. **当前车型全量抓取**
   - 默认抓取品牌当前在售车型、在售配置和结构化参数
3. **历史车型补充模式**
   - 支持 `--include-history`
   - 当前默认历史窗口为最近 `3` 年已上市产品
4. **稳定命名规则**
   - 配置笔记文件名、快照文件名、标题、`trim` 字段统一保留年款，例如 `2026款 525Li M运动套装`
5. **稳定 Markdown 输出**
   - 参数表已处理换行和 `|` 转义，避免破坏 Markdown 表格
6. **固定链接**
   - 配置笔记和车型总览都包含：车型首页、参数配置、车友圈、懂车分(口碑)

## 术语约定

在本 skill 中，下列术语视为同义：

- `OBS`
- `笔记仓库`
- `Obsidian`

上面三者均指向 **Obsidian**。

## Obsidian 操作约束

**强约束**：所有对 `Obsidian` / `OBS` / `笔记仓库` 的操作，均基于 `Obsidian-cli`。

- 不允许假定其他笔记写入通道
- 不允许把本地文件直写作为默认分发行为
- 运行前应保证 `obsidian help` 可执行

## 数据一致性约束

**强约束**：未来通过本 skill 写入 `Obsidian` 的数据结构，必须与当前版本保持一致，除非显式声明版本升级。

当前版本的稳定契约包括：

- 目录结构：`汽车/品牌库/{品牌}/{车型}/...`
- 当前款型路径：`当前款型/{年款+款型}.md`
- 月度快照路径：`更新记录/{YYYY-MM}/{年款+款型}.md`
- 车型总览：`00-车型总览.md`
- 月度摘要：`更新记录/{YYYY-MM}/00-本月更新摘要.md`
- frontmatter 关键字段：`title` / `tags` / `source` / `brand` / `model` / `trim` / `model_year`
- 固定链接：`车型首页` / `参数配置` / `车友圈` / `懂车分(口碑)`

## 可分发 / 可复现边界

本 skill 可以被分发到其他环境执行，但“确定性结果”定义如下：

### 可确定的部分
- 输出目录结构
- 文件命名规则
- frontmatter 字段结构
- 固定链接结构
- 品牌抓取入口命令
- 历史车型过滤口径（最近三年已上市）

### 不可完全确定的部分
- 懂车帝页面实时内容
- 当前在售车型与价格
- 历史车型是否仍保留在站点中
- 验证码、限流、页面改版

### 因此，本 skill 的“可复现”定义为
- 在**相同依赖版本**、**相同命令参数**、**相同站点页面内容**下，产物结构和命名规则可重现
- 若站点内容变化，允许数据值变化，但不允许产物结构悄悄变化

## 前置条件

**检查环境（每次运行前执行）：**

```bash
browser-use doctor 2>/dev/null || echo "NEED_INSTALL"
obsidian help >/dev/null 2>&1 || echo "OBSIDIAN_MISSING"
```

**如需安装 browser-use：**

```bash
cd ~/ai/prism-skills/skills/dongchedi-scraper && uv venv --python 3.11 && source .venv/bin/activate && uv pip install browser-use && browser-use install
```

## 脚本目录

**Important**: 确定此 SKILL.md 所在目录为 `SKILL_DIR`，所有脚本路径 = `${SKILL_DIR}/scripts/<name>.py`

**执行约定**:
1. 先 `cd ${SKILL_DIR}` 再执行 `browser-use` 相关脚本
2. 浏览器脚本统一用 `${SKILL_DIR}/scripts/<name>.py` 作为文件路径
3. 某些 `browser-use python --file` 运行环境不会注入 `__file__`；本 skill 已回退到当前工作目录解析路径，因此 `cd ${SKILL_DIR}` 是必须步骤
4. 非浏览器脚本也建议在 `cd ${SKILL_DIR}` 后执行，保证 `tmp/` 输入输出路径一致

| 脚本 | 用途 | 运行方式 |
|------|------|----------|
| `scripts/search.py` | 搜索车型，或按品牌自动识别在售车型 | `browser-use python --file` |
| `scripts/prepare_targets.py` | 从搜索结果生成 `target-models.json` | `python3` |
| `scripts/competitors.py` | 为目标车型提取竞品 | `browser-use python --file` |
| `scripts/build_series_list.py` | 将目标车型和竞品合并为 `series-list.json` | `python3` |
| `scripts/publish_competitor_analysis.py` | 从 `target-models.json` / `competitors.json` 一路发布到 Obsidian | `python3` |
| `scripts/configs.py` | 配置列表 | `browser-use python --file` |
| `scripts/params.py` | 批量参数抓取 | `browser-use python --file` |
| `scripts/diff.py` | 差异对比 | `python3` (无需浏览器) |
| `scripts/store.py` | Obsidian 存储 | `python3` (无需浏览器) |
| `scripts/run_brand_pipeline.py` | 输入品牌名，串起搜索→车型→配置→参数→笔记输出 | `python3` |

## 推荐单入口

如果用户已经明确给出品牌名，优先使用单入口脚本：

```bash
cd ${SKILL_DIR}
python3 ${SKILL_DIR}/scripts/run_brand_pipeline.py --brand 品牌名
```

常用变体：

```bash
python3 ${SKILL_DIR}/scripts/run_brand_pipeline.py --brand 宝马 --limit-series 3 --skip-store
python3 ${SKILL_DIR}/scripts/run_brand_pipeline.py --brand 比亚迪 --vault 你的Vault名
python3 ${SKILL_DIR}/scripts/run_brand_pipeline.py --brand 理想 --with-competitors
```

说明：
- 默认创建独立运行目录到 `tmp/runs/<timestamp-brand>/`
- 默认抓取品牌搜索、目标车型、配置、参数
- 默认写入 Obsidian；若只想测试抓取链路，用 `--skip-store`
- 若只想做小样本验证，用 `--limit-series N`

## 交互引导流程

### Step 1: 选择模式

向用户询问：

1. **自由抓取模式** — 用户指定任意车型列表，批量抓取配置参数
2. **竞品分析模式** — 用户指定目标品牌/车型，自动发现竞品 + A/B/C 分类 + 索引笔记

### Step 2: 输入目标

引导用户提供信息：
- **自由抓取**: 提供车型名称列表（如"比亚迪汉, 特斯拉 Model 3"）
- **竞品分析 / 自动模式**: 提供品牌名（如"比亚迪"），先自动识别该品牌在售车型，再让用户确认/删减
- **竞品分析 / 手动模式**: 提供品牌名 + 手动指定目标车型列表

### Step 3: 搜索确认

使用 search.py 搜索懂车帝，展示匹配结果让用户确认。

### Step 4: 执行抓取

按以下流程执行（详见各模式章节）。

### Step 5: 输出摘要

展示最终结果统计。

---

## 模式 A: 自由抓取

### A1. 搜索车型

对用户提供的每个关键词，执行搜索：

```bash
cd ${SKILL_DIR}
browser-use open "https://www.dongchedi.com"  # 初始化浏览器
browser-use python "KEYWORD = '关键词'"
browser-use python --file ${SKILL_DIR}/scripts/search.py
```

读取 `tmp/search-results.json`，展示结果让用户选择。

### A2. 准备 series 列表

将用户确认的车型写入 `tmp/series-list.json`：

```json
[
  {"series_id": "1234", "name": "比亚迪 汉", "brand": "比亚迪", "is_target": true},
  ...
]
```

### A3. 获取在售配置

```bash
cd ${SKILL_DIR}
browser-use python --file ${SKILL_DIR}/scripts/configs.py
```

读取 `tmp/all-configs.json` 确认配置数量。

### A4. 批量抓取参数

```bash
cd ${SKILL_DIR}
browser-use python --file ${SKILL_DIR}/scripts/params.py
```

**注意**: 此步骤耗时较长，约 2.5 秒/配置。300 个配置约需 12-15 分钟。

### A5. 差异对比（更新场景）

```bash
cd ${SKILL_DIR}
python3 ${SKILL_DIR}/scripts/diff.py
```

读取 `tmp/changes.json` 查看变更统计。

### A6. 存入 Obsidian

```bash
cd ${SKILL_DIR}
python3 ${SKILL_DIR}/scripts/store.py --changelog
```

---

## 模式 B: 竞品分析

竞品分析保留两种入口，默认推荐自动模式。

### B1. 选择入口

1. **自动模式（推荐）** — 输入品牌名，自动识别该品牌在售车型，用户确认/删减后再提取竞品
2. **手动模式** — 输入品牌名 + 手动指定目标车型，直接提取竞品

### B2. 自动模式：品牌 → 车型列表

```bash
cd ${SKILL_DIR}
browser-use open "https://www.dongchedi.com"  # 初始化浏览器
browser-use python "KEYWORD = '品牌名'"
browser-use python --file ${SKILL_DIR}/scripts/search.py
```

读取 `tmp/search-results.json`，展示自动识别出的在售车型列表，让用户确认保留哪些车型。

生成 `tmp/target-models.json`：

```bash
cd ${SKILL_DIR}
python3 ${SKILL_DIR}/scripts/prepare_targets.py --series-ids 目标series_id1,目标series_id2
```

如果用户确认全部车型，可直接执行：

```bash
cd ${SKILL_DIR}
python3 ${SKILL_DIR}/scripts/prepare_targets.py
```

### B3. 手动模式：品牌 + 指定车型

将用户指定的目标车型写入 `tmp/target-models.json`：

```json
[
  {"name": "比亚迪 汉", "series_id": "1234", "price_range": "20.00-30.00万", "level": "中大型车", "energy_type": "插电式混合动力"}
]
```

### B4. 提取竞品

```bash
cd ${SKILL_DIR}
browser-use python --file ${SKILL_DIR}/scripts/competitors.py
```

读取 `tmp/competitors.json`，展示竞品分类让用户确认/调整。

**如果竞品不足 10 个**: 根据目标车型的级别和价格区间，补充搜索更多竞品。用 `search.py` 搜索同级别车型，手动追加到 `tmp/competitors.json`。

### B5. 准备完整 series 列表

将目标车型 + 所有竞品车型合并写入 `tmp/series-list.json`：

```bash
cd ${SKILL_DIR}
python3 ${SKILL_DIR}/scripts/build_series_list.py
```

### B6-B9. 抓取配置、比对变更并发布到 Obsidian

推荐直接使用总控脚本：

```bash
cd ${SKILL_DIR}
python3 ${SKILL_DIR}/scripts/publish_competitor_analysis.py
```

如需指定 Obsidian vault：

```bash
cd ${SKILL_DIR}
python3 ${SKILL_DIR}/scripts/publish_competitor_analysis.py --vault "你的 Vault 名称"
```

该脚本会自动执行：
1. `build_series_list.py`
2. `browser-use python --file scripts/configs.py`
3. `browser-use python --file scripts/params.py`
4. `python3 scripts/diff.py [--vault]`
5. `python3 scripts/store.py --competitors --changelog [--vault]`

---

## 智能合并策略

更新已有数据时的处理逻辑：

1. **新配置** — 直接创建新笔记
2. **价格变动** — 更新笔记，在顶部插入 `[!tip]` callout 记录变化
3. **参数变化** — 更新参数表，插入变更 callout
4. **停售配置** — 保留笔记不删除，添加 `#停售` tag 和 `[!warning]` callout
5. **无变化** — 跳过（不覆盖 updated 日期）
6. **更新日志** — 生成 `汽车/更新日志/YYYY-MM-DD-更新日志.md` 汇总所有变化

## Obsidian 存储结构

```
汽车/
├── 参数配置/{车型名}/{车型名}-{年款 配置名}-参数配置.md
├── 竞品分析/{品牌车型}-竞品分析.md          # 仅竞品模式
└── 更新日志/YYYY-MM-DD-更新日志.md          # 每次更新
```

## 错误处理

- **浏览器启动失败**: 运行 `browser-use close --all` 清理后重试
- **页面加载超时**: 增加 `browser.wait()` 时间或跳过该配置
- **Captcha interstitial**: 如果脚本报 `dongchedi returned a captcha interstitial`，先在已打开浏览器中完成验证码，再重新执行对应脚本
- **SSR 数据缺失**: 某些页面结构会调整；优先检查 `tmp/` 里的原始 HTML 和 `searchData` / `seriesInfo` 结构
- **Obsidian 未运行**: 提示用户打开 Obsidian 后重试
- **Vault 选择**: 如需写入非当前激活 vault，给 `diff.py` / `store.py` / `publish_competitor_analysis.py` 传 `--vault "Vault 名称"`

## 清理

完成后清理临时文件：

```bash
rm -f ${SKILL_DIR}/tmp/*.json
browser-use close
```

## 测试

最小回归测试：

```bash
cd ${SKILL_DIR}
.venv/bin/python -m unittest discover -s tests -v
```

当前测试覆盖：
- `browser-use python --file` 缺少 `__file__` 时，`scripts/search.py` 仍能运行
- 搜索页出现验证码中间页时，脚本会明确报错
- 输入品牌名时，品牌卡中的在售车型能被自动识别并用于后续竞品分析
