---
name: prism-gpt-image-2
description: Use when the user wants to generate or edit images via the OpenAI-compatible Images API (default model gpt-image-2). Routes to the Anspire AI gateway when ANS_BASE_URL + ANS_API_KEY are set, otherwise falls back to standard OPENAI_BASE_URL + OPENAI_API_KEY, otherwise blocks for a one-time interactive setup. Trigger phrases include 生图 / 改图 / 抠图 / 图像编辑 / generate image / edit image / gpt-image / gpt-image-2 / Anspire 生图.
---

# prism-gpt-image-2

## Overview

Generates and edits images through any OpenAI-compatible Images API endpoint. The default model is `gpt-image-2`. Defaults route to the Anspire AI gateway when its environment variables are present, falling back to the official OpenAI endpoint, and finally to a one-time interactive setup that persists credentials to a per-user config file.

The skill is a thin wrapper:

- one Python CLI under `scripts/cli.py` with `generate`, `edit`, and `setup` subcommands
- credential resolution and config-file loading in `lib/credentials.py`
- a stdlib-only HTTP client in `lib/api.py` (no external runtime dependencies)

## When to Use

Use this skill when the user asks to:

- generate an image from a text prompt (生图)
- edit, inpaint, or recompose an existing image (改图 / 抠图 / 蒙版)
- run the OpenAI Images API or the Anspire `gpt-image-2` gateway
- set up or reconfigure the API credentials used for image generation

Do not use this skill for:

- chat completions or text generation (use the regular Anthropic / OpenAI tooling)
- image generation through Gemini, DashScope, or Replicate (use the matching `baoyu-*` skills)
- bulk illustration pipelines tied to a specific publishing target — call this skill from inside that pipeline instead

## Hard Constraints

- The skill MUST NOT read credentials from any file outside `~/.config/prism-gpt-image-2/env` and the user's process environment.
- The skill MUST NOT hardcode API keys, base URLs, or absolute paths into committed code or docs.
- Saved credentials MUST be written with mode `0600` and only inside `~/.config/prism-gpt-image-2/`.
- When credentials cannot be resolved, the skill MUST stop and ask the user; it MUST NOT call the network with empty or guessed values.
- All network errors MUST surface the upstream HTTP status and response body so the user can debug API issues directly.
- User-supplied paths MUST be resolved against the current working directory and validated for existence before any HTTP call.
- Do not pipe untrusted shell commands (no `curl | bash`) anywhere in this skill.

## Runtime Policy

### Python runtime

- Requires Python 3.10+.
- Uses only the standard library at runtime; no `pip install` is required.
- `pyproject.toml` is included so `uv sync` works for parity with sibling skills, but no dependencies are declared.

### Credential resolution (precedence order)

1. `ANS_API_KEY` and `ANS_BASE_URL` both set in the environment — route every request to the Anspire gateway exactly as in the upstream curl example.
2. `OPENAI_API_KEY` set in the environment — use the standard OpenAI Images API. `OPENAI_BASE_URL` is honored when present and defaults to `https://api.openai.com/v1`.
3. Persisted config file at `~/.config/prism-gpt-image-2/env` — auto-loaded into the process environment at startup. Written by step 4 below; never required to exist.
4. First-time interactive setup. The CLI prompts for an OpenAI base URL (default `https://api.openai.com/v1`) and an API key, then writes them to the config file with mode `0600`. Subsequent invocations read from that file.

The base URL is treated as the API root that has `/images/generations` and `/images/edits` directly underneath. Use:

- Anspire: `https://open-gateway.anspire.ai/v6`
- OpenAI default: `https://api.openai.com/v1`

Trailing slashes on the base URL are stripped automatically.

### Authentication

All requests use `Authorization: Bearer <key>` with the resolved key — matching both OpenAI and the Anspire gateway. No vendor-specific header tweaks are needed.

## Output Contract

Generation and edit responses are decoded as follows:

- If the upstream response includes `data[i].b64_json`, the bytes are decoded and saved to disk.
- Otherwise the skill falls back to downloading `data[i].url`.
- If `--json` is passed, the raw API response is printed to stdout instead of saving files.
- The CLI prints one absolute or relative output path per saved image, one per line, to stdout. Errors and progress go to stderr.

Saving rules:

- `--output PATH` with `n=1` writes exactly that file.
- `--output PATH` with `n>1` writes `PATH_0.png`, `PATH_1.png`, … using the original stem and suffix.
- `--output-dir DIR` writes `generated_0.png`, `generated_1.png`, … (or `edited_*` for edits) inside `DIR`.
- With neither flag, files are written to the current working directory.

The skill does not write anywhere else and does not mutate any vault.

## Workflow

### Step 1: Resolve credentials

Call `lib.credentials.resolve_credentials()`. This loads the persisted config file (if any), then walks the precedence order above. If it falls through to step 4, the function blocks on stdin to prompt the user. After saving, the function returns the new `(api_key, base_url)` and the same process can immediately make requests.

When the skill is invoked from a non-interactive caller (CI, another script), pass `--no-interactive` so missing credentials raise a clear `SystemExit` instead of blocking forever.

### Step 2: Generate or edit

For generation:

```bash
python3 scripts/cli.py generate \
  --prompt "A cute baby sea otter" \
  --size 1024x1024 \
  --n 1 \
  --output ./tmp/otter.png
```

For edit (image-to-image with optional mask):

```bash
python3 scripts/cli.py edit \
  --prompt "Replace the sky with northern lights" \
  --image ./tmp/source.png \
  --mask  ./tmp/mask.png \
  --output ./tmp/edited.png
```

Common flags on both subcommands:

- `--model gpt-image-2` (default; override to use a different OpenAI-compatible model)
- `--n 1..N`
- `--size 1024x1024 | 1024x1536 | 1536x1024 | auto`
- `--quality low | medium | high | auto` (forwarded only when set; ignored by the gateway if unsupported)
- `--background opaque | transparent | auto` (generation only)
- `--response-format b64_json | url` (generation only; default behavior left to the server)
- `--output PATH`, `--output-dir DIR`, `--json`
- `--no-interactive`

Multiple input images for edits are supported by passing `--image a.png b.png …`.

### Step 3: Confirm and report

After saving images, list every produced path back to the user. If the user asked for a single image with no destination, default to `./generated_0.png` (or `./edited_0.png`) so the path is predictable.

For automation that wants the raw JSON response, pass `--json` and parse the response yourself instead of using the file-saving branch.

### First-time setup as an explicit step

```bash
python3 scripts/cli.py setup
```

Use this when:

- the user wants to switch credentials
- the user is on a new machine and has never run the skill
- the persisted config file was deleted or corrupted

## Failure Handling

- Missing credentials in non-interactive mode → CLI exits with code 1 and a message naming all four supported environment variables and the setup subcommand.
- HTTP non-2xx response → CLI exits with the upstream status and response body so the user can see whether it is an auth, quota, or model-mismatch error.
- Network failure (DNS, timeout) → CLI exits with the underlying error reason; no retry loop, since image gen is expensive and silent retries hide rate limits.
- Output path is a directory but `--output-dir` was not used → CLI exits before calling the API and tells the user which flag to switch to.
- Input image path missing for `edit` → CLI exits before calling the API.
- Config file exists but is unreadable or malformed → the loader skips it silently; environment variables already set in the process always win, and the user can rerun `setup` to overwrite.

## Directory Layout

- `SKILL.md` — source of truth for runtime behavior
- `pyproject.toml` — empty dependency set, declared for `uv sync` parity
- `scripts/cli.py` — `generate` / `edit` / `setup` subcommands
- `lib/credentials.py` — env var precedence + config-file load + interactive setup
- `lib/api.py` — stdlib HTTP client for `/images/generations` and `/images/edits`
- `tests/test_credentials.py` — unit tests for the credential precedence order
- `tmp/` — disposable scratch outputs (gitignored)
- `references/openai-images-api.md` — short reference of the request/response shape this skill targets
