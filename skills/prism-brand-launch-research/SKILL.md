---
name: prism-brand-launch-research
description: Use when the user wants to research all press conferences and launch events for a specified Chinese auto brand from a start date to present, including product strategy insights, enterprise strategy insights, configuration changes, three-electric improvements, smart driving capability evolution, and audience strategy changes.
---

# prism-brand-launch-research

## Overview

Research all press conferences and launch events for a specified Chinese auto brand across a time range. Combines multi-source web search with optional Obsidian cross-reference, producing a chronological event timeline and a strategic synthesis report — both written to Obsidian.

This skill is prompt-first. Core capability comes from agent reasoning, structured web searches, and `obsidian-cli` reads and writes rather than fixed-rule scripts.

## When to Use

Use this skill when the user asks to:

- Research or collect a brand's press conferences, launch events, or product releases from a time period
- Understand how a brand's products and strategy evolved over time (e.g., "ZEEKR 近两年发了什么车")
- Analyze configuration changes, three-electric improvements, or smart driving capability evolution across launches
- Investigate a brand's audience strategy or pricing strategy changes through their launch history
- Build a launch history timeline and strategic analysis for a Chinese auto brand

## Hard Constraints

- All Obsidian write operations must go through `obsidian-cli`
- Write `00-分析方法与口径.md` first to lock methodology before producing any analysis
- Missing information must be marked `待确认` — do not infer or fabricate
- Every timeline event must include at least one verifiable source URL
- Confirm with the user before writing `02-战略演进分析.md`
- Obsidian vehicle notes are optional: cross-reference if available, skip and note if not

## Runtime Policy

Tool selection order:

1. Use `agent-reach` if available — provides multi-platform search including Chinese news sources
2. Fall back to `browser-use` if `agent-reach` is unavailable
3. `obsidian-cli` (exposed as `obsidian`) must be available for writes — stop and report if missing

No Python scripts are required. This is a fully prompt-driven skill.

See `references/search-strategy.md` for search query templates and source priority rules.
See `references/prompt-templates.md` for step-by-step prompt templates for each workflow phase.

## Output Contract

All outputs go to `汽车/发布会研究/<品牌>/`:

| File | Purpose | Write order |
|------|---------|-------------|
| `00-分析方法与口径.md` | Analysis scope, source strategy, classification rules | First |
| `01-发布会时间线.md` | Chronological event database | Second |
| `02-战略演进分析.md` | Strategic synthesis report | Last (after user confirmation) |

**Timeline event fields:** date + event name / products / core selling points / configuration changes (三电, 智驾) / product strategy signals / enterprise strategy signals / ≥1 source URL

**Strategic report structure:** brand stage breakdown / product line evolution / 三电 & 智驾 trajectory / facelift and generation patterns / audience strategy changes / enterprise strategy insights / strategy recommendations `【暴露点/影响范围/建议动作/紧迫度】`

**Write behavior:**
- `00-分析方法与口径.md` and `01-发布会时间线.md` overwrite on re-run
- `02-战略演进分析.md` requires user confirmation before writing
- All writes go through `obsidian-cli`

## Workflow

### Step 1: Confirm input

Collect brand name and start date. End date defaults to today. Ask whether Obsidian vehicle notes exist under `汽车/品牌库/<品牌>/` for optional cross-reference.

### Step 2: Write methodology note

Record brand, date range, source strategy, and classification rules. Write to `汽车/发布会研究/<品牌>/00-分析方法与口径.md` via `obsidian-cli` before producing any analysis.

### Step 3: Discovery search (Round 1)

Execute multiple search queries using templates from `references/search-strategy.md`. Build a coarse event inventory: date, event name, product names, source URLs. Cover the full date range in yearly slices if the span exceeds 18 months.

### Step 4: Deep-read and cross-reference (Round 2)

For events meeting any deep-read criteria (new model launch, major facelift, stated strategy or pricing change, significant 三电 or 智驾 upgrade), retrieve and read source articles to extract all 7 analysis fields per `references/analysis-framework.md`.

Optional: if `汽车/品牌库/<品牌>/` exists in Obsidian, read vehicle configuration notes via `obsidian-cli` to cross-reference trim-level changes against launch event claims.

### Step 5: Write outputs

1. Write `01-发布会时间线.md` (no confirmation required)
2. Present strategic analysis draft to user for review
3. On confirmation, write `02-战略演进分析.md`

See `references/prompt-templates.md` and `references/obsidian-workflow.md` for exact prompts and `obsidian-cli` command patterns.

## Failure Handling

- `obsidian-cli` unavailable → stop, tell user to install and verify Obsidian CLI
- No events found for brand → report empty result, suggest retrying with the Chinese brand name
- Event found but source article unavailable → keep event stub with all fields marked `待确认`
- Obsidian brand path missing → continue, skip cross-reference step, note in methodology note

## Directory Layout

- `SKILL.md` — runtime contract and workflow
- `references/search-strategy.md` — search query templates, source priority, quality rules
- `references/analysis-framework.md` — 7-field extraction table, 5-dimension strategic synthesis
- `references/prompt-templates.md` — step-by-step prompt templates for all workflow phases
- `references/obsidian-workflow.md` — obsidian-cli commands and execution loop
- `tmp/` — disposable scratch outputs
