# Obsidian Workflow

Execution loop and `obsidian` command patterns for `prism-brand-launch-research`.

## Prerequisites

Before starting any workflow step that touches Obsidian, verify the CLI is available:

```bash
obsidian version
```

If this fails, stop and tell the user to ensure Obsidian is running with CLI mode enabled.

**Vault policy:** Always operate on the default active vault (most recently focused). Do not pass `vault=<name>` in any command. All paths in this document are relative to the active vault root.

## 8-Step Execution Loop

### Step 1: Confirm inputs

Ask the user:
1. Brand name (中文名 and/or English name)
2. Start date (YYYY-MM-DD)
3. End date (defaults to today if not provided)
4. Is there an existing Obsidian vehicle notes path to cross-reference? (base path: `汽车/品牌库/`)

### Step 2: Write methodology note

Write this note before any analysis. It locks the scope and prevents methodology drift.

```bash
obsidian create path="汽车/发布会研究/<品牌名>/00-分析方法与口径.md" content="..." overwrite
```

Contents to include:
- 分析品牌: `<品牌名>`
- 时间范围: `<开始日期>` 至 `<结束日期>`
- 信源策略: Round 1 WebSearch > Round 2 agent-reach > Round 3 agent-reach 抖音/小红书
- 深读触发条件: 全新车型首发 / 重大改款换代 / 战略或定价变化 / 三电或智驾显著变化
- 交叉验证路径: `汽车/品牌库/<品牌名>/` 或 "无，跳过交叉验证"
- 销量数据路径: `汽车/销量Wiki/`
- Markdown 输出路径: `汽车/发布会研究/<品牌名>/`
- Wiki 输出路径: `汽车/发布会Wiki/<品牌名>/`
- 分析执行时间: `<today's date>`

Verify write:
```bash
obsidian read path="汽车/发布会研究/<品牌名>/00-分析方法与口径.md"
```

### Step 3: Discovery search (Round 1 — WebSearch)

Execute Block 1 from `prompt-templates.md` using `WebSearch`. Produces the coarse event inventory in memory.

If Obsidian vehicle notes exist, search the brand path to understand known models before beginning web search:

```bash
obsidian search query="<品牌名>" path="汽车/品牌库"
obsidian read path="汽车/品牌库/<品牌名>/<车型名>/00-车型总览.md"
```

Reading existing vehicle notes first helps:
- Recognize which models are new vs. facelifts vs. known trims
- Identify configuration gaps to look for in the launch event record

### Step 4: Deep read and cross-reference (Round 2 — agent-reach)

Execute Block 2 from `prompt-templates.md` using `agent-reach` for each event meeting deep-read criteria.

**Cross-reference pattern** (when Obsidian vehicle notes are available):

After extracting launch event data, read the corresponding vehicle note to compare:

```bash
obsidian read path="汽车/品牌库/<品牌名>/<车型名>/当前款型/<款型名>.md"
obsidian read path="汽车/品牌库/<品牌名>/<车型名>/更新记录/<YYYY-MM>/<款型名>.md"
```

Record any discrepancies between the launch event claim and the vehicle note as `配置核验说明` in the event record. Do not resolve conflicts — flag them.

### Step 5: Social listening (Round 3 — agent-reach, 抖音 + 小红书)

Execute Block 3 from `prompt-templates.md` using `agent-reach` for each key event.

**Write user voice analysis (no confirmation required):**

```bash
obsidian create path="汽车/发布会研究/<品牌名>/03-用户声音分析.md" content="..." overwrite
```

Verify:
```bash
obsidian read path="汽车/发布会研究/<品牌名>/03-用户声音分析.md"
```

### Step 6: Sales analysis

Execute Block 4 from `prompt-templates.md`. Read `汽车/销量Wiki/` with:

```bash
obsidian search query="<品牌名> 销量" path="汽车/销量Wiki"
obsidian read path="汽车/销量Wiki/..."
```

**Write sales trend analysis (no confirmation required):**

```bash
obsidian create path="汽车/发布会研究/<品牌名>/04-销量趋势分析.md" content="..." overwrite
```

Verify:
```bash
obsidian read path="汽车/发布会研究/<品牌名>/04-销量趋势分析.md"
```

### Step 7: Write outputs (Markdown directory)

**Write timeline (no confirmation required):**

```bash
obsidian create path="汽车/发布会研究/<品牌名>/01-发布会时间线.md" content="..." overwrite
```

Verify:
```bash
obsidian read path="汽车/发布会研究/<品牌名>/01-发布会时间线.md"
```

**Present strategy analysis draft for confirmation:**

Show the full draft of `02-战略演进分析.md` in the conversation. Use this confirmation gate:

> "以上是 `<品牌名>` 战略演进分析草稿（含用户声音与销量趋势参考）。确认后我将写入 Markdown 目录并构建 Wiki 版本，是否继续？"

Only proceed after the user confirms.

**Write strategy report (after confirmation):**

```bash
obsidian create path="汽车/发布会研究/<品牌名>/02-战略演进分析.md" content="..." overwrite
```

Verify:
```bash
obsidian read path="汽车/发布会研究/<品牌名>/02-战略演进分析.md"
```

### Step 8: Build wiki versions

Execute Block 7 from `prompt-templates.md` immediately after Step 7 completes. No additional user confirmation.

Build wiki versions from the markdown content (use in-memory content; do not re-search or re-analyze). Apply wikilink transformation and add YAML frontmatter per the Output Contract rules in `SKILL.md`.

Write all 5 files to `汽车/发布会Wiki/<品牌名>/`:

```bash
obsidian create path="汽车/发布会Wiki/<品牌名>/00-分析方法与口径.md" content="<wiki content>" overwrite
obsidian read  path="汽车/发布会Wiki/<品牌名>/00-分析方法与口径.md"

obsidian create path="汽车/发布会Wiki/<品牌名>/01-发布会时间线.md" content="<wiki content>" overwrite
obsidian read  path="汽车/发布会Wiki/<品牌名>/01-发布会时间线.md"

obsidian create path="汽车/发布会Wiki/<品牌名>/03-用户声音分析.md" content="<wiki content>" overwrite
obsidian read  path="汽车/发布会Wiki/<品牌名>/03-用户声音分析.md"

obsidian create path="汽车/发布会Wiki/<品牌名>/04-销量趋势分析.md" content="<wiki content>" overwrite
obsidian read  path="汽车/发布会Wiki/<品牌名>/04-销量趋势分析.md"

obsidian create path="汽车/发布会Wiki/<品牌名>/02-战略演进分析.md" content="<wiki content>" overwrite
obsidian read  path="汽车/发布会Wiki/<品牌名>/02-战略演进分析.md"
```

Confirm each wiki file has YAML frontmatter at the top and `[[wikilink]]` format for car model names before proceeding to the next file.

## Timeline Note Format

```markdown
# <品牌名> 发布会时间线

> 时间范围：<开始日期> 至 <结束日期>
> 更新时间：<today's date>

---

## <YYYY-MM-DD> — <事件名称>

**涉及产品：** <产品名称>
**产品角色：** <旗舰款 / 走量款 / ...>

| 字段 | 内容 |
|------|------|
| 核心卖点 | <官方主打点> |
| 三电变化 | <电池/续航/充电/电机> |
| 智驾变化 | <功能级别 / 硬件平台> |
| 配置增减 | <增加或删除的配置项> |
| 定价变化 | <起售价，↑/↓/持平/全新定价> |
| 目标人群信号 | <场景、配色、代言人等> |
| 企业战略信号 | <高管表态、slogan、合作等> |

**信源：** [<来源名称>](<URL>)

---
```

Repeat the event block for each event in reverse-chronological order (newest first).

## Re-run Behavior

Both directories follow the same overwrite rules:
- `00`, `01`, `03`, `04` files in both `汽车/发布会研究/<品牌>/` and `汽车/发布会Wiki/<品牌>/` overwrite on re-run via `obsidian create ... overwrite`
- `02-战略演进分析.md` (both markdown and wiki versions) only updates after user confirmation, even on re-runs
