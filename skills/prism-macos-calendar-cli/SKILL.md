---
name: prism-macos-calendar-cli
description: Use when the user asks to operate macOS Calendar from the command line (list/search/create/update/delete events), especially requests like “用命令行操作日历/创建日程/修改日程/删除日程/导出日程 JSON”.
---

# prism-macos-calendar-cli

Command-line wrappers around Calendar.app on macOS using `osascript` (AppleScriptObjC). No Python dependency.

## Overview

This skill provides a deterministic CLI for common calendar operations on macOS:

- list calendars
- list/search events in a time range (supports `--range` shortcuts and `--limit`)
- create/update/delete events (safe by default: requires `--apply` to write)
- `doctor` to diagnose runtime/permissions
- `cal-intent` to normalize fuzzy user requests into deterministic dry-run/search plans

The backend automates Calendar.app via Apple Events, so macOS Automation permissions may be required.

Performance note: querying all calendars can be slow on some setups (subscribed/remote calendars). Prefer `--calendar <name>` or set `PRISM_CALENDAR_DEFAULT`.

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
- Treat `scripts/cal` as the deterministic execution layer. Do not add fuzzy natural-language parsing to AppleScript.
- Write operations must support a plan-first flow:
  - default is dry-run (no changes)
  - only write when `--apply` is provided
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

- `--format pretty` (default): agent-friendly human output
- `--format json`: a single JSON object per invocation
- `--format text`: TSV-like output

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
- time range (`--from/--to` or `--range`) for list/search
- `--limit` to cap list/search output
- event fields (`--title/--start/--end/...`) for create/update
- target selector (`--id` or `--uid`) for update/delete

For fuzzy natural-language requests, collect instead:

- intent hint: `list/search/create/update/delete`
- calendar hint
- time hint
- event hint
- whether the user explicitly wants to write now or only preview

### Step 2: Execute

Run the CLI from the skill directory:

```bash
cd skills/prism-macos-calendar-cli
./scripts/cal --help
```

Optional ergonomics:

```bash
export PRISM_CALENDAR_DEFAULT='日历'
./scripts/cal events list --range tomorrow --format pretty
```

For fuzzy requests, normalize first:

```bash
cd skills/prism-macos-calendar-cli
./scripts/cal-intent "把那个评审往后挪一点"
./scripts/cal-intent "在2026年3月19日早上9点加一个日历，提醒我喝一杯咖啡"
```

`cal-intent` returns one of:

- `resolved`: already deterministic; the returned `next_command` can be run directly
- `needs_search`: insufficient certainty for write; run the returned `events search/list` command first
- `ambiguous`: still missing required information; stop and ask the user or show candidates

Normalization policy:

- read intent may map directly to `events list/search`
- create intent may map to a dry-run `events create`
- explicit Chinese date requests such as `在2026年3月19日早上9点...` should be normalized directly instead of manually decomposing them first
- if create intent has no explicit calendar but `PRISM_CALENDAR_DEFAULT` is set, use that default directly instead of listing calendars first
- update/delete without a unique selector must degrade to `events search`
- do not emit `--apply` from `cal-intent`
- treat `提醒我...` content as the preferred event title when present

### Step 3: Confirm or validate
For write operations:

- Prefer default dry-run first (omit `--apply`) to confirm the planned write.
- Then re-run with `--apply` to apply the change.

When following a `cal-intent` result:

- if `status=resolved` and the command is a write, run the dry-run command first
- if `status=needs_search`, inspect search results and only continue once a unique target is identified
- if `status=ambiguous`, do not guess
- if create intent is ambiguous only because the calendar is missing, run `./scripts/cal calendars list --format json` once; do not probe Calendar.app through ad-hoc raw AppleScript first

## Failure Handling

- macOS Automation permission denied: follow `references/automation-permissions.md`.
- Calendar.app not running: re-run the command; the backend attempts to launch Calendar.app.
- Invalid ISO time inputs: fix the date/time string and retry.
- Target not found or ambiguous (`--id/--uid` matches 0 or >1 events): refine selectors (add `--calendar`, use `--id`).
- Fuzzy request cannot be normalized into a unique write target: use `cal-intent`, then search, then dry-run, then `--apply`.
- If `./scripts/cal` fails with AppleScript syntax error such as `(-2741)`, treat it as a local skill regression:
  - run `osacompile` on `scripts/calendar.applescript` once
  - fix the bundled script if compilation fails
  - do not continue with raw `osascript -e ...`, `sdef`, app-name probing, or repeated Calendar.app activation attempts
- If direct execution requires permission approval, batch the minimal read/write sequence after approval instead of interleaving extra exploratory commands.
