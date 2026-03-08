# dongchedi-scraper Distribution Notes

## Purpose

This skill scrapes structured vehicle data from dongchedi.com and publishes standardized notes into Obsidian through `Obsidian-cli`.

## Environment Requirements

- Python 3.11+
- `browser-use`
- `Obsidian-cli` available as `obsidian`
- Network access to `dongchedi.com`
- An open and reachable Obsidian vault

## Runtime Selection Policy

The skill follows this runtime policy:

1. Prefer a global Python environment if the required dependencies are already installed there
2. If the global environment is missing the required dependencies, use `uv` to provision a local runtime
3. If Python or Obsidian CLI is missing entirely, stop and instruct the user to complete the base environment setup first

## Canonical Entry

```bash
cd skills/dongchedi-scraper
python3 scripts/run_brand_pipeline.py --brand <brand>
```

## Deterministic Output Contract

The skill is deterministic at the level of:

- note directory structure
- note naming rules
- frontmatter structure
- fixed link layout
- historical-model filtering policy
- command interface

The skill is not fully deterministic at the level of live external content because dongchedi data can change over time.

## Obsidian Alias Policy

The following terms are aliases of the same system:

- `OBS`
- `note repository`
- `Obsidian`

## Obsidian Operation Policy

All Obsidian operations must ultimately go through `Obsidian-cli`.
