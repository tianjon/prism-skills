---
name: prism-dongchedi-scraper
description: Use when the user asks to scrape dongchedi.com vehicle configurations, collect brand or series data, compare current or recent historical trims, or publish automotive configuration notes into Obsidian.
---

# prism-dongchedi-scraper

## Overview

Scrape brand, series, trim, and parameter data from dongchedi.com and optionally publish normalized notes into Obsidian.

The canonical entrypoint is `scripts/run_brand_pipeline.py`. Its default mode is non-interactive so Codex can pass explicit flags and run it directly. Human operators can opt into prompts with `--interactive`.

## When to Use

Use this skill when the user asks to:

- scrape vehicle configurations from dongchedi.com
- capture a full brand or model series into structured notes
- compare current trims or recent historical trims from dongchedi
- publish automotive configuration notes into Obsidian

## Hard Constraints

### Canonical entry constraint

Use `scripts/run_brand_pipeline.py` as the default skill entrypoint. Direct sub-scripts such as `search.py`, `configs.py`, and `params.py` are implementation details unless the user is explicitly debugging a single stage.

### Obsidian constraint

All Obsidian operations must ultimately be performed through `Obsidian-cli` exposed as `obsidian`.

### Interaction constraint

Codex should prefer explicit CLI flags. Do not rely on terminal prompts unless the user explicitly wants an interactive shell flow and `--interactive` is passed.

### Output consistency constraint

Future runs must preserve the current note structure and file naming rules unless an explicit versioned output contract is introduced.

### Taxonomy constraint

The current Obsidian path layout under `汽车/品牌库/...` is a project-specific convention for this repository's vault. Preserve it for this project, but do not treat it as a universal cross-project default.

## Runtime Policy

The pipeline uses this runtime selection strategy:

1. Prefer an already-working Python environment that can import `browser_use` and `pydantic`
2. If those dependencies are missing, provision a skill-local `uv` runtime automatically
3. If local bootstrap is required, install Python dependencies first and then run `browser-use install`
4. If Python is missing entirely, stop and tell the user to install Python `3.11+`
5. If `uv` is required but not installed, stop and tell the user to install `uv`
6. If publishing is requested and `obsidian` is unavailable, stop and tell the user to install and verify Obsidian CLI first

Optional manual setup for a fresh machine:

```bash
cd skills/prism-dongchedi-scraper
uv sync
uv run browser-use install
```

## Output Contract

Each run creates JSON artifacts under `tmp/runs/<timestamp>-<brand>/`.

When publishing is enabled, the pipeline writes:

- one current-trim note per active trim
- one monthly snapshot note per trim
- one series overview note per series
- one monthly summary note per series per month
- optional competitor analysis notes when `--with-competitors` is enabled

The current project-specific note hierarchy is:

- `汽车/品牌库/<品牌>/<车型>/当前款型/<款型>.md`
- `汽车/品牌库/<品牌>/<车型>/更新记录/<YYYY-MM>/<款型>.md`
- `汽车/品牌库/<品牌>/<车型>/00-车型总览.md`
- `汽车/品牌库/<品牌>/<车型>/更新记录/<YYYY-MM>/00-本月更新摘要.md`

Current trim note names must preserve the model year when available, for example:

- `2026款 525Li M运动套装.md`
- `2024款 Pro+ 后驱增程版.md`

Publishing behavior:

- scrape-only is the default; publishing only happens when `--publish` is passed
- generated notes are overwritten with the latest rendered content
- publishing automatically runs `scripts/diff.py` first so monthly summaries and change callouts can use `changes.json`
- if `--limit-configs` is used during a publish run, diff skips discontinued detection to avoid false停售 results from partial data
- discontinued trims may receive additional tags and a停售 callout
- live values are not deterministic because dongchedi content can change

## Workflow

1. Run the canonical entry with explicit flags:

```bash
cd skills/prism-dongchedi-scraper
python3 scripts/run_brand_pipeline.py --brand <brand> [flags]
```

2. Use flags to express user choices instead of relying on prompts. Common flags:

- `--publish`
- `--include-history`
- `--with-competitors`
- `--skip-params`
- `--limit-series <n>`
- `--limit-configs <n>`
- `--configs-batch-size <n>`
- `--vault <name>`
- `--keep-session`

3. Only use `--interactive` for a human-driven terminal session that should ask about omitted options.

4. The pipeline then executes these stages:

- search brand results
- prepare target series
- optionally collect competitors
- build series list
- collect configs in batches
- optionally collect params
- optionally diff against current Obsidian notes
- optionally write notes to Obsidian

5. If the task is scrape-only, omit `--publish` and inspect the run directory under `tmp/runs/`.
6. Do not combine `--publish` with `--skip-params`. Publishing requires parameter extraction and will fail early if params are skipped.

Common examples:

```bash
python3 scripts/run_brand_pipeline.py --brand BMW
python3 scripts/run_brand_pipeline.py --brand Mercedes-Benz --include-history --limit-series 3
python3 scripts/run_brand_pipeline.py --brand Audi --publish --with-competitors --vault Cars
```

## Failure Handling

- If Python is missing, stop and instruct the user to install Python `3.11+`
- If required dependencies are unavailable and `uv` is missing, stop and instruct the user to install `uv`
- If `obsidian` is unavailable when publishing is requested, stop and instruct the user to install and verify Obsidian CLI
- If `--publish` is combined with `--skip-params`, stop early and tell the user to remove one of the flags
- If `--interactive` is used without a TTY, stop and tell the user to re-run without `--interactive` and pass explicit flags instead
- If scraping returns empty or invalid JSON artifacts, stop and report which required file is missing or empty
- If dongchedi anti-bot or live site changes break extraction, report the failing stage and keep the existing output contract unchanged

## Directory Layout

- `SKILL.md` — runtime contract and workflow
- `DISTRIBUTION.md` — distribution and reproducibility notes
- `lib/` — reusable extraction and markdown logic
- `scripts/` — executable entrypoints
- `tests/` — regression tests
- `tmp/` — disposable local artifacts
