# Obsidian Workflow

Execution loop and `obsidian-cli` command patterns for `prism-brand-launch-research`.

## Prerequisites

Before starting any workflow step that writes to Obsidian, verify the CLI is available:

```bash
obsidian --version
```

If this fails, stop and tell the user to install and verify Obsidian CLI before continuing.

## 5-Step Execution Loop

### Step 1: Confirm inputs

Ask the user:
1. Brand name (中文名 and/or English name)
2. Start date (YYYY-MM-DD)
3. End date (defaults to today if not provided)
4. Is there an existing Obsidian vehicle notes path to cross-reference? (e.g., `汽车/品牌库/ZEEKR/`)

### Step 2: Write methodology note

Write this note before any analysis. It locks the scope and prevents methodology drift.

```bash
obsidian write "汽车/发布会研究/<品牌名>/00-分析方法与口径.md" --content "..."
```

Contents to include:
- 分析品牌: `<品牌名>`
- 时间范围: `<开始日期>` 至 `<结束日期>`
- 信源策略: 汽车之家 > 懂车帝 > 36氪汽车 > 电动汽车之家 > 品牌官网 > 其他
- 深读触发条件: 全新车型首发 / 重大改款换代 / 战略或定价变化 / 三电或智驾显著变化
- 交叉验证路径: `<Obsidian 车型笔记路径>` 或 "无，跳过交叉验证"
- 分析执行时间: `<today's date>`

Verify write:
```bash
obsidian read "汽车/发布会研究/<品牌名>/00-分析方法与口径.md"
```

### Step 3: Discovery search

Execute Block 1 from `prompt-templates.md`. Produces the coarse event inventory in memory.

If Obsidian vehicle notes exist, search the brand path to understand known models before beginning web search:

```bash
obsidian search "<品牌名>"
obsidian read "汽车/品牌库/<品牌名>/<车型名>/00-车型总览.md"
```

Reading existing vehicle notes first helps:
- Recognize which models are new vs. facelifts vs. known trims
- Identify configuration gaps to look for in the launch event record

### Step 4: Deep read and cross-reference

Execute Block 2 from `prompt-templates.md` for each event meeting deep-read criteria.

**Cross-reference pattern** (when Obsidian vehicle notes are available):

After extracting launch event data, read the corresponding vehicle note to compare:

```bash
obsidian read "汽车/品牌库/<品牌名>/<车型名>/当前款型/<款型名>.md"
obsidian read "汽车/品牌库/<品牌名>/<车型名>/更新记录/<YYYY-MM>/<款型名>.md"
```

Record any discrepancies between the launch event claim and the vehicle note as `配置核验说明` in the event record. Do not resolve conflicts — flag them.

### Step 5: Write outputs

**Write timeline (no confirmation required):**

```bash
obsidian write "汽车/发布会研究/<品牌名>/01-发布会时间线.md" --content "..."
```

Verify:
```bash
obsidian read "汽车/发布会研究/<品牌名>/01-发布会时间线.md"
```

**Present strategy analysis draft for confirmation:**

Show the full draft of `02-战略演进分析.md` in the conversation. Use this confirmation gate:

> "以上是 `<品牌名>` 战略演进分析草稿。确认后我将写入 Obsidian，是否继续？"

Only proceed after the user confirms.

**Write strategy report (after confirmation):**

```bash
obsidian write "汽车/发布会研究/<品牌名>/02-战略演进分析.md" --content "..."
```

Verify:
```bash
obsidian read "汽车/发布会研究/<品牌名>/02-战略演进分析.md"
```

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

- Re-running the skill for the same brand and date range overwrites `00-分析方法与口径.md` and `01-发布会时间线.md` with updated content
- `02-战略演进分析.md` is only updated after user confirmation, even on re-runs
- `obsidian write` is idempotent for path-identical notes — the existing note is replaced in full
