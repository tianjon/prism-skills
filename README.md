# prism-skills

A local repository for Codex-compatible skills.

This repository currently focuses on a productionized `dongchedi-scraper` skill that scrapes structured vehicle data from dongchedi.com and publishes standardized notes into Obsidian through `Obsidian-cli`.

## Repository Layout

```text
.
├── AGENTS.md
├── README.md
├── docs/
│   └── plans/
├── scripts/
│   └── new-skill.sh
└── skills/
    ├── README.md
    ├── _template/
    └── dongchedi-scraper/
```

## Current Skill

- `skills/dongchedi-scraper/`
  - Brand-driven vehicle scraping pipeline
  - Current model extraction
  - Optional recent-history model supplementation
  - Structured parameter extraction
  - Obsidian publishing through `Obsidian-cli`

## Principles

- Keep every skill self-contained under `skills/<skill-name>/`
- Keep reusable logic in `lib/` and runnable entrypoints in `scripts/`
- Keep temporary outputs in local `tmp/` folders and out of version control
- Treat each `SKILL.md` as the canonical runtime contract for that skill

## Quick Start

```bash
cd skills/dongchedi-scraper
python3 scripts/run_brand_pipeline.py --brand BMW
```

The runtime prefers a globally available Python environment when the required dependencies already exist there. If they do not, it falls back to a local `uv`-managed environment.

## Distribution

See `skills/dongchedi-scraper/DISTRIBUTION.md` for the distribution, environment, determinism, and verification contract.
