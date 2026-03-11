---
name: prism-dongchedi-scraper
description: Scrape vehicle configurations and structured parameters from dongchedi.com, then publish standardized notes into Obsidian. Use this skill when the user asks about dongchedi, vehicle specifications, configuration scraping, brand-wide vehicle capture, or automotive note publishing.
---

# prism-dongchedi-scraper

A brand-driven scraping skill for vehicle series, trims, and parameters from dongchedi.com.

## When to Use

Use this skill when the user asks to:

- scrape vehicle configurations from dongchedi.com
- capture a full brand or model series into structured notes
- compare current trims or recent historical trims from dongchedi
- publish automotive configuration notes into Obsidian

## Capability Summary

This skill currently provides:

1. A single brand entrypoint through `scripts/run_brand_pipeline.py`
2. Current-model scraping for a brand
3. Optional recent-history supplementation through `--include-history`
4. Structured parameter extraction from SSR data whenever possible
5. Stable note naming that preserves model year in file names, titles, and trim labels
6. Stable markdown rendering for parameter tables, including escaped pipes and multiline values
7. Fixed links for every config note and series overview note:
   - model home
   - parameter page
   - community page
   - score/review page
8. Obsidian publishing through `Obsidian-cli`

## Terminology

In this skill, the following terms are aliases of the same system:

- `OBS`
- `note repository`
- `Obsidian`

## Hard Constraints

### Obsidian constraint

All Obsidian operations must ultimately be performed through `Obsidian-cli`.

Other wrapper skills or helpers may be used, but the final Obsidian write path must still resolve to `Obsidian-cli`.

### Output consistency constraint

Future runs must preserve the current output structure unless an explicit versioned output contract is introduced.

## Output Contract

The note hierarchy is stable and must remain structurally identical across runs:

- one brand root per brand
- one series folder per vehicle series
- one current-trim folder for active trim notes
- one monthly snapshot folder for archived trim notes
- one series overview note per series
- one monthly summary note per series per month

The current trim note names must preserve the model year, for example:

- `2026 MY 525Li M Sport Package.md`
- `2024 MY Facelift Pro+ RWD Range-Extended.md`

## Environment Checks

Before running the pipeline, verify the base tools:

```bash
python3 --version
obsidian help >/dev/null 2>&1 || echo OBSIDIAN_MISSING
browser-use doctor 2>/dev/null || echo BROWSER_USE_MISSING
```

If Python or Obsidian CLI is missing, stop and instruct the user to complete the base environment setup first.

## Runtime Policy

The pipeline uses this runtime selection strategy:

1. Prefer a global Python environment when the required dependencies are already available there
2. If the global environment is missing the required dependencies, provision and use a local runtime with `uv`
3. If Python is missing entirely, stop and tell the user to install Python first
4. If `uv` is required but not installed, stop and tell the user to install `uv` first
5. If `Obsidian-cli` is required for publishing but is missing, stop and tell the user to install and verify it first

## Script Entry

Primary script entrypoint:

| Script | Purpose |
|--------|---------|
| `scripts/run_brand_pipeline.py` | End-to-end brand pipeline with runtime resolution and interactive option handling |

## Canonical Entry

```bash
cd ${SKILL_DIR}
python3 scripts/run_brand_pipeline.py --brand <brand>
```

## Interactive Option Policy

When the user does not explicitly pass options, the pipeline must ask for confirmation interactively instead of silently selecting user-facing defaults.

Interactive confirmation is required for:

- whether to include historical models
- the historical model-year window
- whether to extract competitors
- whether to extract parameters
- whether to publish into Obsidian
- the target vault name
- the number of series to process
- the number of configurations to process
- config batch size
- parameter batch size
- whether to keep browser sessions open

## Common Examples

```bash
python3 scripts/run_brand_pipeline.py --brand BMW
python3 scripts/run_brand_pipeline.py --brand Mercedes-Benz --include-history
python3 scripts/run_brand_pipeline.py --brand Audi --limit-series 3 --limit-configs 10
```

## Determinism Boundary

The skill is deterministic in:

- output structure
- note naming rules
- frontmatter shape
- fixed link layout
- historical filtering policy
- command interface

The skill is not fully deterministic in live data values because dongchedi content can change over time.

## Failure Handling

- If Python is missing, stop and instruct the user to install Python `3.11+`.
- If required runtime dependencies are unavailable and `uv` is missing, stop and instruct the user to install `uv`.
- If `Obsidian-cli` is unavailable when publishing is requested, stop and instruct the user to install and verify Obsidian CLI.
- If scraping returns empty or invalid JSON artifacts, stop and report which required file is missing or empty.
- If live dongchedi data changes produce unstable results, describe the failed step and preserve the existing output contract.

## Directory Layout

- `SKILL.md` — runtime contract
- `DISTRIBUTION.md` — distribution and reproducibility notes
- `lib/` — reusable extraction and markdown logic
- `scripts/` — executable entrypoints
- `tests/` — regression tests
- `tmp/` — disposable local artifacts
