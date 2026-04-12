# prism-skills

Reusable local skills for AI coding agents.

## Available Skills

| Skill | Description |
|-------|-------------|
| `prism-dongchedi-scraper` | Scrape vehicle configurations from dongchedi.com and publish standardized notes into Obsidian via `Obsidian-cli`. |
| `prism-doc-to-obsidian` | Convert MinerU-supported documents into Markdown and save confirmed notes into Obsidian with indexes, tags, and cross-note links. |
| `prism-macos-calendar-cli` | Operate macOS Calendar.app from the command line (list/search/create/update/delete events) using built-in `osascript` (no Python). |
| `prism-ev-strategy-evolution` | Analyze one brand's pure EV and range-extended EV strategy evolution from Obsidian vehicle notes, including discontinued models and price/configuration/mass tradeoffs. |
| `prism-brand-launch-research` | Research all press conferences and launch events for a Chinese auto brand across a date range, producing a chronological event timeline and strategic analysis report in Obsidian. |

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
| `prism-dongchedi-scraper` | Python `3.11+`, `browser-use`, network access to `dongchedi.com`, browser automation support, `Obsidian-cli` and vault write access for the default pipeline |
| `prism-doc-to-obsidian` | Python `3.10-3.13`, Obsidian `1.12+` with CLI enabled and running, MinerU, network access for MinerU/model bootstrap when needed, and filesystem write access to the target vault |
| `prism-macos-calendar-cli` | macOS with Calendar.app, `/usr/bin/osascript`, GUI session access, and macOS Automation permission for the calling terminal |
| `prism-ev-strategy-evolution` | Obsidian `1.12+` with CLI enabled and running, plus read/write access to the active vault |
| `prism-brand-launch-research` | `agent-reach` or `browser-use`, external web access, Obsidian `1.12+` with CLI enabled and running, plus read/write access to the active vault |

## Sandbox And Permissions

These skills are functional-first. They may require permissions outside the current repository, because several workflows intentionally operate on live desktop apps, network services, or an external Obsidian vault.

Common permission patterns:

- `obsidian`-based skills write to the real vault, not this repository, so a workspace-only filesystem sandbox is usually insufficient.
- `prism-dongchedi-scraper` may create or repair a local Python runtime, install `browser-use`, open a browser session, access `dongchedi.com`, and then write notes into Obsidian.
- `prism-doc-to-obsidian` may create a virtualenv under `$HOME/.base-env/`, install MinerU, download models, and copy extracted assets into the target vault.
- `prism-macos-calendar-cli` is macOS-only and depends on Apple Events / Automation permission to control Calendar.app.
- Prompt-first research skills such as `prism-brand-launch-research` still require live web access plus Obsidian read/write access, even though they do not ship Python scripts.

If your agent runs inside a strict sandbox, expect to grant the minimum required network, GUI automation, and out-of-workspace filesystem permissions per skill.

For a per-skill breakdown, see [docs/permissions-matrix.md](docs/permissions-matrix.md).

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
cp -R skills/prism-macos-calendar-cli ~/.codex/skills/prism-macos-calendar-cli
cp -R skills/prism-ev-strategy-evolution ~/.codex/skills/prism-ev-strategy-evolution
cp -R skills/prism-brand-launch-research ~/.codex/skills/prism-brand-launch-research
```

### Claude Code

```bash
mkdir -p ~/.claude/skills
cp -R skills/prism-dongchedi-scraper ~/.claude/skills/prism-dongchedi-scraper
cp -R skills/prism-doc-to-obsidian ~/.claude/skills/prism-doc-to-obsidian
cp -R skills/prism-macos-calendar-cli ~/.claude/skills/prism-macos-calendar-cli
cp -R skills/prism-ev-strategy-evolution ~/.claude/skills/prism-ev-strategy-evolution
cp -R skills/prism-brand-launch-research ~/.claude/skills/prism-brand-launch-research
```

### OpenCode

```bash
mkdir -p ~/.config/opencode/skills
cp -R skills/prism-dongchedi-scraper ~/.config/opencode/skills/prism-dongchedi-scraper
cp -R skills/prism-doc-to-obsidian ~/.config/opencode/skills/prism-doc-to-obsidian
cp -R skills/prism-macos-calendar-cli ~/.config/opencode/skills/prism-macos-calendar-cli
cp -R skills/prism-ev-strategy-evolution ~/.config/opencode/skills/prism-ev-strategy-evolution
cp -R skills/prism-brand-launch-research ~/.config/opencode/skills/prism-brand-launch-research
```

Restart the agent tool and confirm it discovers the installed skills.

## Quick Start

### `prism-dongchedi-scraper`

The canonical entrypoint is publish-first, not scrape-only. Running the command below will scrape live data, diff against existing Obsidian notes, and write the rendered result back into the vault.

```bash
cd skills/prism-dongchedi-scraper
python3 scripts/run_brand_pipeline.py --brand BMW
```

This default run publishes notes into Obsidian and overwrites the generated target note paths. This requires the `obsidian` CLI to be available. To target a specific vault:

```bash
python3 scripts/run_brand_pipeline.py --brand BMW --vault Cars
```

Note: the canonical entrypoint itself is responsible for publishing via `scripts/diff.py` and `scripts/store.py`; there is no scrape-only mode on that default path.
This default pipeline also assumes network access, browser automation, and write access to the real Obsidian vault.

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
On sandboxed agents, this usually also requires write access outside the repository because the destination vault is external.

See `skills/prism-doc-to-obsidian/SKILL.md` for the workflow, dependency checks, bilingual prompts, and confirmation-first publishing rules.

### `prism-ev-strategy-evolution`

Typical prompt:

```text
Use prism-ev-strategy-evolution to analyze ZEEKR from Obsidian.
Read all models under 汽车/品牌库/ZEEKR, including discontinued models.
Separate pure EV and range-extended EV lines.
Explain the relationship between configuration, price, and vehicle mass.
Write the result to 汽车/配置分析/三电分析/ZEEKR.
```

This skill is intentionally prompt-first. It relies on `obsidian-cli`, reasoning, and the prompt assets in `references/` instead of fixed-rule analysis scripts.

See `skills/prism-ev-strategy-evolution/SKILL.md` for the workflow and output contract.

### `prism-brand-launch-research`

Typical prompt:

```text
Use prism-brand-launch-research to research ZEEKR from 2023-01-01 to today.
Write the timeline and strategic analysis to Obsidian.
```

This skill is prompt-first. It uses `agent-reach` (or `browser-use`) for multi-source web search and `obsidian-cli` for writing results to Obsidian. No Python required.

See `skills/prism-brand-launch-research/SKILL.md` for the workflow and output contract.

## Repository Structure

```text
skills/
  prism-dongchedi-scraper/
  prism-doc-to-obsidian/
  prism-macos-calendar-cli/
  prism-ev-strategy-evolution/
  prism-brand-launch-research/
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
