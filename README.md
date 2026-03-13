# prism-skills

Reusable local skills for AI coding agents.

## Available Skills

| Skill | Description |
|-------|-------------|
| `prism-dongchedi-scraper` | Scrape vehicle configurations from dongchedi.com and publish standardized notes into Obsidian via `Obsidian-cli`. |
| `prism-doc-to-obsidian` | Convert MinerU-supported documents into Markdown and save confirmed notes into Obsidian with indexes, tags, and cross-note links. |

## Supported Agents

The repository is currently structured for local skill installation in:

- Codex
- Claude Code
- OpenCode

## Requirements

Base requirements:

- Git
- `uv`
- A compatible local agent CLI such as `Codex`, `Claude Code`, or `OpenCode`

Skill-specific runtime requirements:

| Skill | Runtime Requirements |
|-------|----------------------|
| `prism-dongchedi-scraper` | Python `3.11+`, `browser-use`, `Obsidian-cli` when publishing |
| `prism-doc-to-obsidian` | Python `3.10-3.13`, Obsidian `1.12+` with CLI enabled and running, MinerU |

## Installation

Clone with HTTPS by default:

```bash
git clone https://github.com/tianjon/prism-skills.git
cd prism-skills
```

Install one or more skills into your agent's local skill directory.

### Codex

```bash
mkdir -p ~/.codex/skills
cp -R skills/prism-dongchedi-scraper ~/.codex/skills/prism-dongchedi-scraper
cp -R skills/prism-doc-to-obsidian ~/.codex/skills/prism-doc-to-obsidian
```

### Claude Code

```bash
mkdir -p ~/.claude/skills
cp -R skills/prism-dongchedi-scraper ~/.claude/skills/prism-dongchedi-scraper
cp -R skills/prism-doc-to-obsidian ~/.claude/skills/prism-doc-to-obsidian
```

### OpenCode

```bash
mkdir -p ~/.config/opencode/skills
cp -R skills/prism-dongchedi-scraper ~/.config/opencode/skills/prism-dongchedi-scraper
cp -R skills/prism-doc-to-obsidian ~/.config/opencode/skills/prism-doc-to-obsidian
```

Restart the agent tool and confirm it discovers the installed skills.

## Quick Start

### `prism-dongchedi-scraper`

```bash
cd skills/prism-dongchedi-scraper
python3 scripts/run_brand_pipeline.py --brand BMW
```

Publishing requires an explicit flag:

```bash
python3 scripts/run_brand_pipeline.py --brand BMW --publish
```

Note: publishing is handled by this skill itself via `scripts/diff.py` and `scripts/store.py`.

See `skills/prism-dongchedi-scraper/SKILL.md` for the full workflow and `skills/prism-dongchedi-scraper/DISTRIBUTION.md` for runtime notes.

### `prism-doc-to-obsidian`

Typical prompt:

```text
Convert this file into Obsidian notes with prism-doc-to-obsidian.
Check Python and Obsidian CLI first.
If MinerU or required Obsidian skills are missing, install them automatically.
Before writing, show me the proposed folder structure and file list for confirmation.
```

Deterministic backend (after confirmation):

```bash
cd skills/prism-doc-to-obsidian
python3 scripts/convert_recursive.py --input <file-or-dir> --output tmp/run
python3 scripts/import_to_obsidian.py --manifest tmp/run/manifest.json --target-root <vault-subpath>
```

Note bodies are written via `obsidian-cli`. Binary attachments are copied through the filesystem because the CLI is text-only.

See `skills/prism-doc-to-obsidian/SKILL.md` for the workflow, dependency checks, bilingual prompts, and confirmation-first publishing rules.

## Repository Structure

```text
skills/
  prism-dongchedi-scraper/
  prism-doc-to-obsidian/
docs/plans/
scripts/
```

Each skill should remain self-contained under `skills/<skill-name>/`.

## Contributing

Issues and pull requests are welcome.

When contributing:

- keep each change scoped to one skill or one documentation topic
- update the affected `SKILL.md` when behavior changes
- add focused tests for stable parsing or transformation logic
- include verification steps in your PR description

## License

This repository is licensed under the [MIT License](LICENSE).
