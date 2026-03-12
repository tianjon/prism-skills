# prism-dongchedi-scraper Distribution Notes

## Purpose

This skill scrapes structured vehicle data from dongchedi.com and can publish normalized notes into Obsidian through `obsidian`.

## Supported Execution Model

- Default: non-interactive CLI execution driven by explicit flags
- Optional: `--interactive` for a human terminal session
- Canonical entrypoint: `scripts/run_brand_pipeline.py`

## Environment Requirements

- Python 3.11+
- `uv` when local runtime bootstrap is needed
- `obsidian` available on PATH when publishing is enabled
- Network access to `dongchedi.com`

## Browser Automation Bootstrap

The canonical entrypoint handles browser automation setup in this order:

1. Reuse a working Python environment that already has `browser-use` and `pydantic`
2. Otherwise provision a skill-local `uv` runtime automatically
3. Install Python dependencies into that runtime
4. Run `browser-use install` inside that runtime before scraping

Optional manual setup:

```bash
cd skills/prism-dongchedi-scraper
uv sync
uv run browser-use install
```

## Publishing Contract

- All Obsidian writes go through `obsidian`
- Publishing is opt-in. Use `--publish` on the canonical entrypoint.
- Publishing runs `scripts/diff.py` first to generate `changes.json` for monthly summaries and change callouts.
- When publishing with partial data (for example `--limit-configs`), diff skips discontinued detection to avoid false停售 results.
- Generated notes overwrite the latest generated version of the same target path
- The `汽车/品牌库/...` note layout is a project-specific convention for this repository

## Determinism Boundary

Deterministic:

- note directory structure
- note naming rules
- frontmatter structure
- fixed link layout
- command interface

Non-deterministic:

- live external content from dongchedi.com
- anti-bot and site-structure behavior
