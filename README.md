# prism-skills

Skills shared for local AI coding agents.

本仓库目前主要提供 `dongchedi-scraper`，用于抓取懂车帝车型配置，并通过 `Obsidian-cli` 发布到 Obsidian。

## Prerequisites

- Git
- Python 3.11+
- `uv`（用于 Python 环境管理）
- 已安装并可正常使用的 Agent CLI：`Codex`、`Claude Code` 或 `OpenCode`

## Installation

### Add to Codex

```bash
rm -rf /tmp/prism-skills
git clone git@github.com:tianjon/prism-skills.git /tmp/prism-skills
mkdir -p ~/.codex/skills
cp -R /tmp/prism-skills/skills/dongchedi-scraper ~/.codex/skills/dongchedi-scraper
rm -rf /tmp/prism-skills
```

### Add to Claude Code

```bash
rm -rf /tmp/prism-skills
git clone git@github.com:tianjon/prism-skills.git /tmp/prism-skills
mkdir -p ~/.claude/skills
cp -R /tmp/prism-skills/skills/dongchedi-scraper ~/.claude/skills/dongchedi-scraper
rm -rf /tmp/prism-skills
```

### Add to OpenCode

```bash
rm -rf /tmp/prism-skills
git clone git@github.com:tianjon/prism-skills.git /tmp/prism-skills
mkdir -p ~/.config/opencode/skills
cp -R /tmp/prism-skills/skills/dongchedi-scraper ~/.config/opencode/skills/dongchedi-scraper
rm -rf /tmp/prism-skills
```

### Verify

Restart the tool and confirm it can discover `dongchedi-scraper`.

## Available Skills

| Skill | Description |
|-------|-------------|
| `dongchedi-scraper` | Scrape vehicle configurations from dongchedi.com and publish standardized notes into Obsidian via `Obsidian-cli`. |

### dongchedi-scraper

```bash
cd skills/dongchedi-scraper
python3 scripts/run_brand_pipeline.py --brand BMW
```

See `skills/dongchedi-scraper/SKILL.md` for workflow details and `skills/dongchedi-scraper/DISTRIBUTION.md` for environment notes.

## Usage Restrictions

- Personal learning, research, evaluation, and non-commercial experiments only
- No commercial use
- No paid service, SaaS hosting, enterprise production use, or closed-source commercial redistribution

See `LICENSE` for full terms.

## Maintainer Notes

If code is published to GitHub, use this Git identity:

```bash
git config --global user.name "tianjon"
git config --global user.email "fengyadong@gmail.com"
```

## License

This repository uses `Personal Research Non-Commercial License 1.0`.
