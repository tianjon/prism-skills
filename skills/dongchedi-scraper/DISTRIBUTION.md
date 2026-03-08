# dongchedi-scraper Distribution Notes

## Purpose

This skill scrapes structured car data from dongchedi and writes standardized notes into Obsidian via `Obsidian-cli`.

## Environment Requirements

- Python 3.11+
- `browser-use` installed and working
- `Obsidian-cli` available as `obsidian`
- Network access to `dongchedi.com`
- An opened and reachable Obsidian vault

## Canonical Entry

```bash
cd skills/dongchedi-scraper
python3 scripts/run_brand_pipeline.py --brand 品牌名
```

## Output Contract

- Brand root: `汽车/品牌库/{品牌}/{车型}/`
- Current trim note: `当前款型/{YYYY款 车型配置名}.md`
- Monthly snapshot: `更新记录/{YYYY-MM}/{YYYY款 车型配置名}.md`
- Series overview: `00-车型总览.md`
- Monthly summary: `更新记录/{YYYY-MM}/00-本月更新摘要.md`

## Determinism Statement

This skill is deterministic at the level of:

- output structure
- note naming
- frontmatter schema
- fixed link layout
- command interface

It is not fully deterministic at the level of live external data because dongchedi content can change.

## Obsidian Alias Policy

`OBS`, `笔记仓库`, and `Obsidian` are aliases of the same system: Obsidian.

## Obsidian Operation Policy

All Obsidian operations must go through `Obsidian-cli`.
