# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

A collection of local AI agent skills — self-contained units of capability designed for Codex, Claude Code, and OpenCode. Skills are installed by copying them into the agent's skill directory. Each skill is independent and communicates through its `SKILL.md` contract.

## Commands

Most commands run inside a specific skill directory.

### Setup (prism-dongchedi-scraper)

```bash
cd skills/prism-dongchedi-scraper
uv sync
uv run browser-use install
```

### Run the dongchedi pipeline

```bash
cd skills/prism-dongchedi-scraper
python3 scripts/run_brand_pipeline.py --brand BMW
python3 scripts/run_brand_pipeline.py --brand BMW --vault Cars
python3 scripts/run_brand_pipeline.py --brand Audi --with-competitors --limit-series 3
```

### Run tests

Each skill uses Python's `unittest`. From the repo root:

```bash
# All tests in a skill
cd skills/prism-dongchedi-scraper && python3 -m pytest tests/

# Single test file
cd skills/prism-dongchedi-scraper && python3 -m pytest tests/test_run_brand_pipeline.py

# Single test case
cd skills/prism-dongchedi-scraper && python3 -m pytest tests/test_run_brand_pipeline.py::RunBrandPipelineTest::test_build_parser_accepts_brand_and_options
```

### Scaffold a new skill

```bash
./scripts/new-skill.sh prism-<name>
```

## Architecture

### Skill layout

Every skill lives under `skills/<skill-name>/` and is self-contained:

- `SKILL.md` — the only source of truth for triggering, constraints, workflow, and output contract
- `references/` — schemas, prompt templates, extended workflow notes
- `lib/` — reusable Python modules (opt-in, not default)
- `scripts/` — executable entrypoints (opt-in when prompt orchestration is insufficient)
- `tests/` — regression tests for stable parsing/transformation logic
- `tmp/` — disposable local artifacts; never commit

### Design philosophy

Skills are **prompt-first**. Scripts and libraries are added only when deterministic code is genuinely required. Most orchestration lives in `SKILL.md` and `references/`, not in Python files.

### Cross-skill rules

- No runtime dependencies between sibling skills
- Obsidian operations always go through the `obsidian` CLI (`obsidian-cli`)
- Temporary outputs stay inside the skill's own `tmp/`

### Publishing pipeline (prism-dongchedi-scraper)

The canonical flow is: `run_brand_pipeline.py` → scrape → diff (`changes.json`) → write to Obsidian via `obsidian`. The diff step runs automatically before publish so monthly summaries and change callouts are accurate. With `--limit-configs`, diff skips discontinued detection to avoid false停售 results from partial data.

## Conventions

- Skill names: `prism-` prefix, kebab-case (e.g. `prism-wechat-poster`)
- Python: 3.11+ for dongchedi; 3.10–3.13 for doc-to-obsidian; managed via `uv`
- `tmp/` is gitignored scratch space — never treat it as a stable artifact location
- `SKILL.md` sections must include: Overview, When to Use, Hard Constraints, Runtime Policy, Output Contract, Workflow, Failure Handling, Directory Layout

## Key Files

- `docs/skill-writing-guidelines.md` — read before adding or heavily refactoring a skill
- `skills/_template/SKILL.md` — the scaffold template, kept in sync with the guidelines
- `AGENTS.md` — repository-level agent conventions (security rules, naming, structure)
