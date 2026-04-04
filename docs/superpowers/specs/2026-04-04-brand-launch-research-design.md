# Design: prism-brand-launch-research

**Date:** 2026-04-04
**Status:** Approved

## Context

Users want to research the full press conference and product launch history of a specified Chinese auto brand across a date range, and extract structured insights — not just a raw event list. Key analysis dimensions include configuration changes (三电 parameters, smart driving capabilities), facelift and generation patterns, audience strategy shifts, and enterprise-level strategic signals. Results should be written into Obsidian as a reusable research artifact.

## Approach

**Prompt-first, no scripts.** Agent uses `agent-reach` (or `browser-use` as fallback) for web search plus `obsidian-cli` for reads and writes. This mirrors the `prism-ev-strategy-evolution` architecture: reasoning-led analysis over structured prompt templates, with external tool calls as the only I/O layer.

Rationale: web news content is unstructured and requires reasoning to distinguish confirmed launch events from rumors, and to synthesize strategy from event patterns. Scripts add maintenance burden without improving accuracy.

## Skill Name

`prism-brand-launch-research`

## Output Contract

Three Obsidian notes under `汽车/发布会研究/<品牌>/`:

| File | Purpose |
|------|---------|
| `00-分析方法与口径.md` | Methodology note written first to lock scope |
| `01-发布会时间线.md` | Chronological event database |
| `02-战略演进分析.md` | Strategic synthesis report (requires user confirmation before writing) |

## Search Strategy

Two-round approach:
1. **Discovery (Round 1):** Multi-query search using 6 base templates across yearly time slices. Builds coarse event inventory.
2. **Deep read (Round 2):** Full article retrieval for events meeting any of 4 criteria (new model, major facelift, strategy/pricing change, significant 三电 or 智驾 change).

Source priority: 汽车之家 > 懂车帝 > 36氪汽车 > 电动汽车之家 > 品牌官网 > others.

## Analysis Framework

Each event extracts 7 fields: 产品角色 / 三电变化 / 智驾变化 / 配置增减 / 定价变化 / 目标人群信号 / 企业战略信号. Missing fields → `待确认`, never inferred.

Strategic synthesis uses 5 dimensions consistent with `prism-ev-strategy-evolution`: 同价做强 / 体验做开 / 场景做准 / 上游做稳 / 竞争压力应对.

## Obsidian Cross-Reference (Optional)

If `汽车/品牌库/<品牌>/` exists, read vehicle configuration notes via `obsidian-cli` to cross-reference trim changes against launch event claims. No cross-reference capability → skill continues normally.

## Hard Constraints

- All Obsidian writes via `obsidian-cli`
- Write methodology note first
- Missing info → `待确认`, not inferred
- Every timeline event needs ≥1 verifiable source URL
- User confirmation required before writing strategy report

## Reference Files

| File | Contents |
|------|---------|
| `references/search-strategy.md` | Query templates, source priority, deep-read triggers, quality rules, time slicing |
| `references/analysis-framework.md` | 7-field extraction table, product role classification, 三电/智驾 dimensions, 5-dimension synthesis, recommendation format |
| `references/prompt-templates.md` | 4 prompt blocks: discovery, deep-read, synthesis, write-back |
| `references/obsidian-workflow.md` | 5-step execution loop, obsidian-cli command patterns, timeline note format |
