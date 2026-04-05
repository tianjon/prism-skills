---
name: prism-brand-launch-research
description: Use when the user wants to research all press conferences and launch events for a specified Chinese auto brand from a start date to present, including product strategy insights, enterprise strategy insights, configuration changes, three-electric improvements, smart driving capability evolution, and audience strategy changes.
---

# prism-brand-launch-research

## Overview

Research all press conferences and launch events for a specified Chinese auto brand across a time range. Combines multi-source web search with optional Obsidian cross-reference, producing a chronological event timeline and a strategic synthesis report — both written to Obsidian.

This skill is prompt-first. Core capability comes from agent reasoning, structured web searches, and `obsidian` CLI reads and writes rather than fixed-rule scripts.

## When to Use

Use this skill when the user asks to:

- Research or collect a brand's press conferences, launch events, or product releases from a time period
- Understand how a brand's products and strategy evolved over time (e.g., "ZEEKR 近两年发了什么车")
- Analyze configuration changes, three-electric improvements, or smart driving capability evolution across launches
- Investigate a brand's audience strategy or pricing strategy changes through their launch history
- Build a launch history timeline and strategic analysis for a Chinese auto brand

## Hard Constraints

- All Obsidian operations (read, write, search) must use the `obsidian` CLI — no direct filesystem access to vault files
- Always operate on the default active vault; never pass `vault=<name>` in any command
- Write `00-分析方法与口径.md` first to lock methodology before producing any analysis
- Missing information must be marked `待确认` — do not infer or fabricate
- Every timeline event must include at least one verifiable source URL
- Confirm with the user before writing `02-战略演进分析.md` (applies to both markdown and wiki versions)
- Obsidian vehicle notes are optional: cross-reference if available, skip and note if not
- Vehicle configuration notes are stored under `汽车/品牌库/` in Obsidian
- Sales data lives at `汽车/销量Wiki/` — always cross-reference this path for sales analysis
- Wiki build (Step 8) must run after ALL markdown writes complete, including `02-战略演进分析.md`

## Runtime Policy

Three-round search strategy:

1. **Round 1 (Discovery):** Use general `WebSearch` — broad coverage of Chinese auto news, press releases, and event records
2. **Round 2 (Deep read):** Use Perplexity API via `curl` — deeper web search and full article extraction for events meeting deep-read criteria. Read API key from `$PERPLEXITY_API_KEY` environment variable; stop and report if unset.
3. **Round 3 (Social listening):** Use `agent-reach` across four channels — 小红书 (`xhs`), 汽车之家论坛 + 懂车帝口碑区 (Jina Reader), B站 (bilibili API), 微信公众号 (Exa search) — to capture post-launch user voices, reactions, and sentiment for each key event

The `obsidian` CLI must be available and Obsidian must be running — stop and report if missing.

No Python scripts are required. This is a fully prompt-driven skill.

See `references/search-strategy.md` for search query templates and source priority rules.
See `references/prompt-templates.md` for step-by-step prompt templates for each workflow phase.

## Output Contract

Two parallel output directories are written on every run:

### Markdown outputs → `汽车/发布会研究/<品牌>/`

Plain markdown, no wikilinks or frontmatter. Human-readable outside Obsidian.

| File | Purpose | Write order |
|------|---------|-------------|
| `00-分析方法与口径.md` | Analysis scope, source strategy, classification rules | First |
| `01-发布会时间线.md` | Chronological event database | Second |
| `03-用户声音分析.md` | Post-launch social listening: 抖音 & 小红书 user feedback | Third |
| `04-销量趋势分析.md` | Brand total + model-specific sales trends, 6 months pre/post launch | Fourth |
| `02-战略演进分析.md` | Strategic synthesis report | Last (after user confirmation) |

### Wiki outputs → `汽车/发布会Wiki/<品牌>/`

Built from the markdown content. Adds YAML frontmatter and wikilinks to enable Obsidian Graph View, backlinks, and Dataview queries. Same 5 files, written after all markdown writes complete. No additional user confirmation required.

**Wikilink transformation rules:**
- Car model names → `[[汽车/品牌库/<品牌>/<车型>|<车型名>]]`
- Sales data month references → `[[汽车/销量Wiki/<品牌>/<YYYY-MM>|<YYYY-MM>]]`
- Cross-file references within wiki dir → `[[汽车/发布会Wiki/<品牌>/01-发布会时间线|发布会时间线]]` etc.
- External URLs: preserve as-is, do not convert to wikilinks

**YAML frontmatter added to each wiki file:**
```yaml
---
brand: <品牌名>
date_range_start: <YYYY-MM-DD>
date_range_end: <YYYY-MM-DD>
generated: <YYYY-MM-DD>
type: <methodology | launch-timeline | strategy-analysis | user-voice | sales-analysis>
---
```

**Timeline event fields:** date + event name / products / core selling points / configuration changes (三电, 智驾) / product strategy signals / enterprise strategy signals / ≥1 source URL

**User voice report structure:** per-event post-launch reactions from 抖音 and 小红书 / key praise themes / key complaint themes / sentiment summary / representative quotes (with source links)

**Sales analysis structure:** per-event 6-month pre/post sales comparison — brand total monthly sales / model-specific monthly sales / trend direction (↑/↓/持平) / notable inflection points

**Strategic report structure:** brand stage breakdown / product line evolution / 三电 & 智驾 trajectory / facelift and generation patterns / audience strategy changes / enterprise strategy insights / strategy recommendations `【暴露点/影响范围/建议动作/紧迫度】`

**Write behavior:**
- `00`, `01`, `03`, `04` files in both directories overwrite on re-run
- `02-战略演进分析.md` requires user confirmation before writing in both directories
- All writes use `obsidian create path=... content=... overwrite`

## Workflow

### Step 1: Confirm input

Collect brand name and start date. End date defaults to today. Ask whether Obsidian vehicle notes exist under `汽车/品牌库/` for optional cross-reference. Note that sales data is expected at `汽车/销量Wiki/`.

### Step 2: Write methodology note

Record brand, date range, source strategy, and classification rules. Write to `汽车/发布会研究/<品牌>/00-分析方法与口径.md` via `obsidian` before producing any analysis.

### Step 3: Discovery search (Round 1 — WebSearch)

Use `WebSearch` to execute multiple search queries from `references/search-strategy.md`. Build a coarse event inventory: date, event name, product names, source URLs. Cover the full date range in yearly slices if the span exceeds 18 months.

### Step 4: Deep-read and cross-reference (Round 2 — agent-reach)

Use `agent-reach` for each event meeting deep-read criteria (new model launch, major facelift, strategy/pricing change, significant 三电 or 智驾 upgrade). Extract all 7 analysis fields per `references/analysis-framework.md`.

Optional: if `汽车/品牌库/` exists in Obsidian, read vehicle configuration notes via `obsidian` to cross-reference trim-level changes against launch event claims.

### Step 5: Social listening (Round 3 — agent-reach, 抖音 & 小红书)

For each key event in the timeline, use `agent-reach` to search 抖音 and 小红书 for post-launch user reactions. Query window: 0–4 weeks after the event date. Extract: praise themes, complaint themes, sentiment summary, and representative quotes with source links. Write `03-用户声音分析.md`.

### Step 6: Sales analysis

Read `汽车/销量Wiki/` via `obsidian` to retrieve brand total monthly sales and model-specific monthly sales. For each key launch event, compare the 6-month window before and after the event date. Note trend direction, volume inflection points, and whether sales moved in the direction of the launch positioning. Write `04-销量趋势分析.md`.

### Step 7: Write strategic synthesis

1. Write `01-发布会时间线.md` (no confirmation required)
2. Present strategic analysis draft to user for review
3. On confirmation, write `02-战略演进分析.md`

### Step 8: Build wiki versions

After all markdown files are written, build wiki versions for all 5 files and write to `汽车/发布会Wiki/<品牌>/`. Apply wikilink transformation rules and add YAML frontmatter per the Output Contract. No additional user confirmation required.

See `references/prompt-templates.md` (Block 7) and `references/obsidian-workflow.md` (Step 8) for exact prompts and `obsidian` command patterns.

## Failure Handling

- `obsidian` CLI unavailable or Obsidian not running → stop, tell user to open Obsidian with CLI mode enabled
- No events found for brand → report empty result, suggest retrying with the Chinese brand name
- Event found but source article unavailable → keep event stub with all fields marked `待确认`
- Obsidian brand path missing → continue, skip cross-reference step, note in methodology note

## Directory Layout

- `SKILL.md` — runtime contract and workflow
- `references/search-strategy.md` — query templates by round (WebSearch / agent-reach / 抖音+小红书), source priority, sales wiki read strategy
- `references/analysis-framework.md` — 7-field extraction table, 5-dimension strategic synthesis
- `references/prompt-templates.md` — 7 prompt blocks covering all workflow phases (Block 7 = wiki build)
- `references/obsidian-workflow.md` — obsidian command patterns, execution loop, re-run behavior
- `tmp/` — disposable scratch outputs
