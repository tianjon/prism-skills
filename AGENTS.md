# Repository Guidelines

## Project Structure & Module Organization
This repository manages local Codex skills under one directory: `skills/`. Each skill should live in `skills/<skill-name>/` so future additions stay isolated and predictable. The current skill is `skills/dongchedi-scraper/`, which includes:

- `SKILL.md` — skill entrypoint and workflow instructions
- `lib/` — reusable Python modules such as parsing and markdown helpers
- `scripts/` — runnable task scripts such as `search.py` and `params.py`
- `tmp/` — generated JSON artifacts and scratch outputs; treat as disposable

When adding a new skill, use the same pattern and add optional `assets/` or `tests/` only when needed.

## Build, Test, and Development Commands
Most work happens inside one skill directory.

- `cd skills/dongchedi-scraper` — enter the current skill workspace
- `uv venv --python 3.11` — create the recommended virtual environment
- `uv pip install browser-use` — install the current runtime dependency
- `browser-use install` — install browser automation support
- `browser-use python --file scripts/search.py` — run a browser-backed scraping step
- `python3 scripts/diff.py` — compare scraped data without launching a browser
- `./scripts/new-skill.sh my-new-skill` — scaffold a new skill under `skills/` from the template

If a future skill needs extra setup, document its commands in that skill’s `SKILL.md`.

## Coding Style & Naming Conventions
Use Python 3.11+, 4-space indentation, and descriptive snake_case names for files, functions, and variables. Keep reusable logic in `lib/` and thin entry scripts in `scripts/`. Name skill directories in kebab-case, such as `dongchedi-scraper` or `wechat-poster`.

## Testing Guidelines
There is no shared `tests/` suite yet. Validate each change at the smallest useful level: run the affected script, inspect generated files in `tmp/`, and confirm outputs against the workflow in `SKILL.md`. If a skill gains stable parsing or transformation logic, add focused tests under that skill, for example `skills/dongchedi-scraper/tests/test_markdown.py`.

## Commit & Pull Request Guidelines
No repository-wide commit convention is established yet, so use short imperative messages such as `feat: add search result normalizer` or `docs: clarify skills layout`. Keep each commit scoped to one skill or one documentation change. PRs should include the purpose, touched skill directories, manual verification steps, and screenshots or sample outputs when behavior changes are user-visible.

## Agent-Specific Notes
Treat each `SKILL.md` as the source of truth for running a skill. Do not hardcode cross-skill assumptions; keep every skill self-contained so new siblings can be added under `skills/` with minimal coupling.
