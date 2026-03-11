# Install And Checks

## Purpose

Use this reference when the skill must validate the local runtime or automatically install missing dependencies.

## Base Requirement Checks

Check Python first:

```bash
python3 --version
```

Python must be between `3.10` and `3.13`. If it is outside that range, stop and explain the current version and the required range.

Check Obsidian next:

```bash
obsidian help
```

Obsidian must be at least `1.12`. If the command fails, stop and explain whether:

- Obsidian is not installed
- Obsidian does not support CLI
- CLI is not enabled
- Obsidian is not running

## MinerU Detection

```bash
mineru --help
```

If MinerU is missing, install it automatically with the preferred environment-aware workflow. Prefer `uv` and avoid hardcoded environment paths.

## MinerU Install

Preferred install command:

```bash
uv pip install -U "mineru[all]"
```

After installation, verify:

```bash
mineru --help
mineru-models-download --help
```

## MinerU Model Download

Trigger model download when:

- MinerU is newly installed
- MinerU is installed but local models are missing

Use the official model download entrypoint and follow the active environment's network constraints.

## Obsidian Skill Detection

Check whether these skills are available:

- `obsidian-markdown`
- `obsidian-bases`
- `obsidian-cli`

If any skill is missing, install only the missing items with the local `skill-installer` flow before continuing.

## Stop Conditions

Stop immediately when:

- Python does not meet the required version range
- Obsidian CLI is unavailable
- Obsidian is not running
- MinerU install fails
- MinerU model download fails
- required Obsidian skills cannot be installed
