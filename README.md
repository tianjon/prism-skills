# prism-skills

A local repository for managing Codex skills in one place. All skills live under `skills/`, so the repository can grow cleanly as more skills are added.

## Repository Layout

Current structure:

```text
.
├── AGENTS.md
├── README.md
├── .gitignore
├── scripts/
│   └── new-skill.sh
└── skills/
    ├── README.md
    ├── _template/
    └── dongchedi-scraper/
        ├── SKILL.md
        ├── lib/
        ├── scripts/
        ├── tmp/
        └── pyproject.toml
```

Recommended pattern for future skills:

```text
skills/<skill-name>/
├── SKILL.md
├── lib/
├── scripts/
├── assets/         # optional
├── tests/          # optional
└── pyproject.toml  # optional
```

Create a new skill from the template:

```bash
./scripts/new-skill.sh my-new-skill
```

## Current Skills

- `skills/dongchedi-scraper/`: scrape car configuration data from 懂车帝, with browser automation scripts and data post-processing helpers.
- `skills/_template/`: starter scaffold for creating new skills consistently.

## Working Conventions

- Keep each skill self-contained inside `skills/<skill-name>/`.
- Put reusable logic in `lib/` and task entrypoints in `scripts/`.
- Treat each `SKILL.md` as the source of truth for setup and runtime workflow.
- Keep generated artifacts in local temp/output folders such as `tmp/`.

## Quick Start

```bash
cd skills/dongchedi-scraper
uv venv --python 3.11
uv pip install browser-use
browser-use install
browser-use python --file scripts/search.py
```

See `AGENTS.md` for contributor guidelines and `skills/README.md` for the skill directory policy.
