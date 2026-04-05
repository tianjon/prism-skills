---
name: prism-ev-strategy-evolution
description: Use when the user wants to analyze a brand's pure EV and range-extended EV strategy evolution from Obsidian vehicle notes, including discontinued models, timeline changes, price-to-configuration tradeoffs, and vehicle-mass impacts.
---

# prism-ev-strategy-evolution

## Overview

Analyze one automotive brand across all models in Obsidian and produce a brand-level EV strategy evolution study plus per-model analysis notes.

This skill is prompt-first. The core capability comes from agent reasoning, structured prompts, and `obsidian-cli` reads and writes rather than fixed-rule scripts.

## When to Use

Use this skill when the user asks to:

- analyze a brand's three-electric strategy evolution
- compare pure EV and range-extended EV lines across time
- study how configuration, price, and vehicle mass move together
- include discontinued models in a brand-wide strategy review
- write automotive analysis notes back into Obsidian under a fixed path

## Hard Constraints

- Source notes must be read through `obsidian-cli`.
- The default analysis scope is a full brand, not a single model only.
- The analysis must include discontinued models when evidence exists in the note archive.
- 停售车型必须被视为品牌策略迁移的重要证据，不能默认排除。
- Pure EV (`纯电`) and range-extended EV (`增程`) must be analyzed separately and then compared together.
- The analysis must explain how the brand wins: same-price competitiveness, experience differentiation, scenario focus, and upstream value-chain control.
- Battery supplier changes, battery-technology labels, and upstream value-chain structure must be treated as first-class evidence when the notes contain them.
- **每条策略结论必须有竞品基准**：不允许孤立评价品牌三电能力，必须与 2-3 款主要竞品对比后才下领先/持平/落后的判断。Discovery 阶段必须同步读取竞品笔记。
- **品牌总报告必须包含「策略建议」章节**：每条建议对应一个三电暴露点，格式为【暴露点/影响范围/建议动作/紧迫度】，以商业可执行为标准，不接受纯描述性总结。
- The final notes must be stored under `汽车/配置分析/三电分析/$品牌名`.
- This skill must stay prompt-first and reasoning-led. Do not reduce the workflow to fixed-rule parsing or scripted scoring.
- Only add scripts if prompt orchestration is demonstrably insufficient.

## Runtime Policy

- Require a running Obsidian desktop app with CLI enabled.
- Use the active vault unless the user explicitly names a vault.
- Start with discovery and reading through `obsidian-cli`, then build the analysis in conversation, then write the final notes through `obsidian-cli`.
- Prefer reusable prompt templates in `references/` over custom code.
- Treat note contents as evidence, not ground truth. Missing fields or inconsistent structures must be called out in the analysis.

## Output Contract

Write the analysis results into the following Obsidian path family:

- `汽车/配置分析/三电分析/$品牌名/00-品牌三电策略总报告.md`
- `汽车/配置分析/三电分析/$品牌名/01-分析方法与口径.md`
- `汽车/配置分析/三电分析/$品牌名/车型清单与阶段映射.md`
- `汽车/配置分析/三电分析/$品牌名/车型分析/$车型名.md`

Behavioral requirements:

- Brand report first, then per-model reports.
- Notes must explicitly separate pure EV and range-extended EV findings.
- Reports must explain price/configuration relationships and configuration/mass relationships.
- Reports should explain when supplier choices or supplier shifts support cost, differentiation, or supply stability.
- **The brand report must include a 竞品对标总结 table** (one table per price segment) with 领先/持平/落后 judgments for each three-electric dimension.
- **The brand report must include a 策略建议 chapter** with competitor-grounded, actionable items sorted by urgency.
- When evidence is incomplete, the note must mark the missing fields instead of fabricating a conclusion.

## Workflow

### Step 1: Discover the brand corpus

- Use `obsidian search` to locate the brand root under `汽车/品牌库/$品牌名`.
- Identify all model directories, including archived and discontinued entries.
- Read `当前款型`, `更新记录`, and overview notes as available.

### Step 2: Build the evidence map

- Separate models into pure EV and range-extended EV lines.
- For each model, build a time-ordered view of launch, refresh, key trim changes, and discontinuation.
- Record where price, battery, battery supplier, battery technology label, charging, motor layout, range, and vehicle mass appear in the notes.
- **Identify 2-3 key competitors per price segment** and read their notes from `汽车/品牌库/`. Competitor notes are required evidence — do not skip this step.

### Step 3: Analyze the brand

- Infer brand stages from model launches, route shifts, technical upgrades, price-band changes, and discontinuation timing.
- Infer how the brand is trying to win: cost leadership, differentiation, focus, or stronger value-chain control.
- Explain how pure EV and range-extended EV lines split responsibilities across the brand lifecycle.
- Compare technology progress with commercial strategy rather than only listing parameters.

### Step 4: Analyze each model

- Reconstruct the model timeline.
- Separate true technical progress from configuration redistribution.
- Track whether supplier shifts coincide with chemistry shifts, charging shifts, or price-band moves.
- Explain whether upgrades are offset by higher price or higher vehicle mass.
- Position the model inside the brand's larger stage strategy.

### Step 5: Write back to Obsidian

- Write `01-分析方法与口径.md` first to lock the analysis method.
- Write `00-品牌三电策略总报告.md` next.
- Write or update per-model notes under `车型分析/`.
- Cross-link the brand summary, stage map, and model notes where useful.

Use the detailed matrices and prompt blocks in:

- `references/analysis-framework.md`
- `references/prompt-templates.md`
- `references/obsidian-workflow.md`

## Failure Handling

- If `obsidian-cli` is unavailable or Obsidian is not running, stop and report that the workflow cannot proceed.
- If the brand root cannot be found, stop and report the missing path or naming ambiguity.
- If model evidence is partial, continue only with explicit uncertainty markers in the output.
- If a model's route cannot be determined confidently, mark it as unresolved instead of forcing `纯电` or `增程`.
- If the available notes are too sparse for a brand-stage conclusion, produce only the evidence map and identified gaps.

## Directory Layout

- `SKILL.md` — source of truth for the workflow and output contract
- `references/analysis-framework.md` — analysis dimensions and relationship model
- `references/prompt-templates.md` — reusable prompt blocks for brand and model reports
- `references/obsidian-workflow.md` — concrete `obsidian-cli` read/write loop for this skill
- `tmp/` — disposable scratch outputs when temporary notes are needed during execution
