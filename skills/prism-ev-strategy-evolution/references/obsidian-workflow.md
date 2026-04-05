# Obsidian Workflow

This reference turns the skill contract into a repeatable read -> analyze -> write loop while keeping the work reasoning-led.

## 1. Discover The Brand Corpus

Use `obsidian search` first to locate the brand root and enumerate likely model folders.

Example:

```bash
obsidian search query="汽车/品牌库/$品牌名" limit=200
```

Discovery checklist:

- find all model folders under the brand root
- include archived and discontinued branches
- identify overview notes and `更新记录` folders
- note naming inconsistencies before analysis starts

## 2. Read Evidence Notes

Use `obsidian read` to collect evidence from:

- `00-车型总览.md`
- `当前款型/*.md`
- `更新记录/<YYYY-MM>/*.md`
- any monthly summary note when it exists

Example:

```bash
obsidian read path="汽车/品牌库/$品牌名/$车型名/00-车型总览.md"
obsidian read path="汽车/品牌库/$品牌名/$车型名/当前款型/$款型名.md"
```

Read with these goals:

- identify `纯电` or `增程`
- capture price, range, battery, charging, motor, and vehicle-mass evidence
- reconstruct timeline nodes such as launch, refresh, and discontinuation

## 3. Build The Analysis In Memory

Do not jump straight to writing.

First produce an internal evidence map:

- brand-stage hypotheses
- pure EV vs range-extended EV split
- per-model timeline
- price/configuration relationships
- configuration/vehicle-mass relationships
- missing-field list

This step is where the agent's reasoning should dominate. Avoid scripted scoring unless the prompt workflow becomes insufficient.

## 4. Write The Method Note

Use `obsidian create` to lock the analysis method before writing conclusions.

Target path:

- `汽车/配置分析/三电分析/$品牌名/01-分析方法与口径.md`

The note should document:

- analysis scope
- route classification rules
- timeline rules
- price/configuration judgment rules
- configuration/mass judgment rules
- missing-data handling

## 5. Write The Brand Summary

Use `obsidian create` for the first write and `obsidian append` if the note is too long.

Target path:

- `汽车/配置分析/三电分析/$品牌名/00-品牌三电策略总报告.md`

The `品牌总报告` should include:

- brand stages
- pure EV route evolution
- range-extended EV route evolution
- route split, replacement, or convergence
- discontinued models as strategy evidence

## 6. Write Per-Model Notes

Write one `车型分报告` per model:

- `汽车/配置分析/三电分析/$品牌名/车型分析/$车型名.md`

Each note should cover:

- timeline
- route positioning
- technical progress vs configuration redistribution
- price/configuration relationship
- configuration/vehicle-mass relationship
- role in the brand stage

## 7. Write The Stage Map

Write a compact index note to tie the brand together:

- `汽车/配置分析/三电分析/$品牌名/车型清单与阶段映射.md`

Minimum columns:

- model
- current status
- route
- inferred stage
- strategic role

## 8. Verify The Result

After writing, use `obsidian read` again on the destination notes to confirm:

- the note exists at the expected path
- the title and major sections are present
- the brand summary links naturally to model notes
- there are no fabricated claims where evidence was missing
