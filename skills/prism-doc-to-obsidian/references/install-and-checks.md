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
which mineru
```

If `which mineru` returns nothing, MinerU is not installed. Install it automatically.

## MinerU Install

Preferred install command (installs MinerU as a global tool and adds it to PATH):

```bash
uv tool install "mineru[all]"
```

If `uv` is not available, fall back to:

```bash
pip install -U "mineru[all]"
```

After installation, verify with:

```bash
which mineru
```

If the command is still not found after installation, stop and report the failure.

## MinerU Model Download

Run model download immediately after installation. The download command is idempotent — it skips files that are already present, so there is no need to detect whether models exist before running it.

Default to `huggingface`. Use `modelscope` only if the user is in mainland China or explicitly requests it.

For international networks:

```bash
mineru-models-download -s huggingface
```

For Chinese networks:

```bash
mineru-models-download -s modelscope
```

If the download fails, stop and report the exact error output.

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
- `uv` and `pip` are both unavailable
- MinerU install fails
- MinerU model download fails
- required Obsidian skills cannot be installed
