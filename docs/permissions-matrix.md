# Permissions Matrix

This repository is functional-first. Several skills intentionally operate on live desktop applications, external network services, or an Obsidian vault outside this repository.

Use this document to decide the minimum permissions an agent needs before running a skill.

## Common Permission Types

| Permission Type | Meaning |
|-----------------|---------|
| Repository write | Write only inside this repository |
| Out-of-workspace write | Write outside the repository, for example the real Obsidian vault or `$HOME/.base-env/` |
| Network | Reach external sites or download dependencies/models |
| GUI / browser automation | Launch or control browser / desktop apps |
| macOS Automation | Apple Events / TCC permission to control Calendar.app |

## Skill Matrix

| Skill | Repository Write | Out-of-workspace Write | Network | GUI / Browser Automation | macOS Automation | Notes |
|-------|------------------|------------------------|---------|--------------------------|------------------|-------|
| `prism-dongchedi-scraper` | Yes | Yes | Yes | Yes | No | Default pipeline writes to Obsidian, may create `.venv`, may install `browser-use`, and scrapes `dongchedi.com` |
| `prism-doc-to-obsidian` | Yes | Yes | Usually yes | No | No | First-run setup may create `$HOME/.base-env/`, install MinerU, download models, and copy assets into the target vault |
| `prism-macos-calendar-cli` | No persistent write required | No | No | Yes | Yes | Requires a macOS GUI session and permission for the calling terminal to control Calendar.app |
| `prism-ev-strategy-evolution` | No persistent write required | Yes | No | No | No | Reads from and writes to the active Obsidian vault via `obsidian-cli` |
| `prism-brand-launch-research` | No persistent write required | Yes | Yes | Sometimes | No | Uses live web research plus Obsidian read/write; browser automation depends on the chosen search path |

## Skill Details

### `prism-dongchedi-scraper`

Minimum practical permission set:

- network access to `dongchedi.com`
- browser automation support for `browser-use`
- write access to the target Obsidian vault
- local environment write access if runtime bootstrap is needed

Typical out-of-workspace writes:

- skill-local `.venv/`
- dependency/cache directories used by `uv`
- the real Obsidian vault

Typical failures when permissions are missing:

- `uv` / package install failures
- `browser-use install` failures
- captcha / blocked live scraping
- `obsidian` write or read-back verification failures

### `prism-doc-to-obsidian`

Minimum practical permission set:

- write access to the target Obsidian vault
- out-of-workspace write access for `$HOME/.base-env/` when bootstrapping
- network access when MinerU or Python/model bootstrap is missing

Typical out-of-workspace writes:

- `$HOME/.base-env/prism-doc-to-obsidian`
- `uv` tool/cache locations
- MinerU model cache
- the real Obsidian vault

Typical failures when permissions are missing:

- `uv python install` / `uv sync` failures
- `uv tool install "mineru[all]"` failures
- `mineru-models-download` failures
- asset copy failures into the vault

### `prism-macos-calendar-cli`

Minimum practical permission set:

- macOS GUI session
- `/usr/bin/osascript`
- Apple Events / Automation permission for the terminal app controlling Calendar.app

Typical failures when permissions are missing:

- AppleScript permission denied
- Calendar.app cannot be launched in a headless environment

### `prism-ev-strategy-evolution`

Minimum practical permission set:

- `obsidian-cli` access to the active vault
- read/write access to the real vault selected by Obsidian

Typical failures when permissions are missing:

- `obsidian` CLI unavailable
- active vault cannot be read or written

### `prism-brand-launch-research`

Minimum practical permission set:

- live web access for the configured research path
- read/write access to the active Obsidian vault

Additional conditional permissions:

- browser automation if the workflow falls back to `browser-use`
- API credentials and outbound network access if Perplexity or other external services are used

Typical failures when permissions are missing:

- web search cannot execute
- API-backed deep read cannot authenticate
- Obsidian write steps fail after research succeeds

## Agent Guidance

If your agent runs in a strict sandbox, the safest order is:

1. Grant repository access first.
2. Grant only the skill-specific extra permissions listed above.
3. Re-run the smallest meaningful command, not the whole workflow, if you are validating permissions incrementally.

For repository contributors, treat these permission requirements as part of the public contract. Do not hide them inside default behavior or installation side effects.
