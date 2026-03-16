---
name: prism-macos-calendar-cli
description: Use when the user asks to operate macOS Calendar from the command line (list/search/create/update/delete events), especially requests like “用命令行操作日历/创建日程/修改日程/删除日程/导出日程 JSON”.
---

# prism-macos-calendar-cli

Command-line wrappers around Calendar.app on macOS using `osascript` (AppleScriptObjC). No Python dependency.

## Overview

This skill provides a deterministic CLI for common calendar operations on macOS:

- list calendars
- list/search events in a time range
- create/update/delete events (with `--dry-run` support)

The backend automates Calendar.app via Apple Events, so macOS Automation permissions may be required.

## When to Use

Use this skill when the user asks to:
- list calendars from macOS Calendar via CLI
- search or export calendar events as JSON
- create/update/delete calendar events from the terminal
- "把日历操作封装为命令行脚本"

## Hard Constraints

- macOS only. This skill automates Calendar.app via `osascript`.
- Do not require Python code or a Python runtime.
- Do not pass unsanitized user input into shell command strings. Pass values as argv entries to `osascript`.
- Write operations must support `--dry-run` and must not modify Calendar when `--dry-run` is set.
- If an update/delete target is ambiguous, stop and return a structured error (do not guess).

## Runtime Policy

Runtime prerequisites:

- macOS with Calendar.app installed.
- `/usr/bin/osascript` available (built-in).

Permissions:

- Calendar automation may prompt for macOS Automation permission (Terminal/iTerm controlling Calendar).
- See `references/automation-permissions.md` for recovery steps.

## Output Contract

This skill writes no persistent files by default.

The CLI writes to stdout:

- `--format text` (default): human-readable output
- `--format json`: a single JSON object per invocation

JSON contract:

- Success: `{"ok":true,"data":<payload>}`
- Error: `{"ok":false,"error":{"code":"...","message":"...","details":{...}}}`

Payload shapes:

- calendars: `[{ "name": "..." }]`
- events: `[{ "id":"...", "uid":"...", "calendar":"...", "title":"...", "start":"ISO", "end":"ISO", "location":"...", "notes":"...", "url":"..." }]`

Notes:

- `id` is Calendar.app's internal event id (useful for deterministic updates on the same machine).
- `uid` is the iCalendar UID when available.

## Directory Layout

- `SKILL.md` — source of truth for runtime behavior
- `references/` — permissions and operational notes
- `scripts/` — executable entrypoints (`bash` + `osascript`)
- `tmp/` — disposable scratch outputs

## Workflow

### Step 1: Gather input
Collect:

- command: calendars list, events list/search/create/update/delete
- time range (`--from/--to`) for list/search
- event fields (`--title/--start/--end/...`) for create/update
- target selector (`--id` or `--uid`) for update/delete

### Step 2: Execute

Run the CLI from the skill directory:

```bash
cd skills/prism-macos-calendar-cli
./scripts/cal --help
```

### Step 3: Confirm or validate
For write operations:

- Prefer `--dry-run --format json` first to confirm the planned write.
- Then re-run without `--dry-run` to apply the change.

## Failure Handling

- macOS Automation permission denied: follow `references/automation-permissions.md`.
- Calendar.app not running: re-run the command; the backend attempts to launch Calendar.app.
- Invalid ISO time inputs: fix the date/time string and retry.
- Target not found or ambiguous (`--id/--uid` matches 0 or >1 events): refine selectors (add `--calendar`, use `--id`).
