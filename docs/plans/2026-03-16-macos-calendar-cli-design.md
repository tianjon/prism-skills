# macOS Calendar CLI Skill Design (No Python)

Date: 2026-03-16

## Summary

Add a new repository skill under `skills/` that wraps common macOS Calendar operations into a deterministic command-line interface.

Hard requirement: the runtime must not depend on Python code. The implementation must rely only on macOS built-ins.

## Goals

- Provide a CLI to:
  - list calendars
  - list events in a time range
  - search events by keyword (within a time range)
  - create, update, delete events
- Provide stable JSON output for scripting (`--format json`).
- Provide safe write operations with `--dry-run`.
- Avoid unsafe shell interpolation; pass user input to `osascript` as argv entries.

## Non-Goals (v1)

- Recurrence rule authoring (RRULE) or advanced attendee management.
- Full-text search across the entire database without a time range.
- Cross-platform support (macOS only).

## Approach Options Considered

1. AppleScript via `osascript` controlling Calendar.app (selected for v1)
2. Swift CLI using EventKit (candidate for v2)
3. Python + PyObjC/EventKit (rejected: Python dependency)

Rationale: Option 1 is built-in and fastest to ship. We keep a backend-agnostic CLI/JSON contract so Option 2 can replace the backend later without breaking users.

## Proposed Skill

Skill name: `prism-macos-calendar-cli`

### Directory Layout

- `skills/prism-macos-calendar-cli/SKILL.md`
- `skills/prism-macos-calendar-cli/scripts/cal` (bash entrypoint)
- `skills/prism-macos-calendar-cli/scripts/calendar.applescript` (logic + JSON + ISO time parsing)
- `skills/prism-macos-calendar-cli/references/automation-permissions.md`
- `skills/prism-macos-calendar-cli/tmp/` (disposable)

No Python runtime, no `uv`.

## CLI Contract

Canonical invocation:

- `cd skills/prism-macos-calendar-cli`
- `./scripts/cal ...`

Commands:

- `cal calendars list [--format json|text]`
- `cal events list --from <ISO> --to <ISO> [--calendar <name>] [--format json|text]`
- `cal events search --query <text> --from <ISO> --to <ISO> [--calendar <name>] [--format json|text]`
- `cal events create --calendar <name> --title <text> --start <ISO> --end <ISO> [--location <text>] [--notes <text>] [--url <text>] [--dry-run] [--format json|text]`
- `cal events update --uid <uid> [--calendar <name>] [--title <text>] [--start <ISO>] [--end <ISO>] [--location <text>] [--notes <text>] [--url <text>] [--dry-run] [--format json|text]`
- `cal events delete --uid <uid> [--calendar <name>] [--dry-run] [--format json|text]`

### Time Parsing

- Accept ISO 8601:
  - `YYYY-MM-DD`
  - `YYYY-MM-DDTHH:MM`
  - `YYYY-MM-DDTHH:MM:SS`
  - optional timezone: `Z` or `+08:00`
  - allow a single space instead of `T` (normalized to `T` internally)
- For list/search:
  - If `--from` is date-only, treat as local start-of-day.
  - If `--to` is date-only, treat as local next-day start (exclusive) to cover the full day.
- For create/update:
  - Require a time component for `--start/--end` (reject date-only).

## Output Contract

`--format json` returns a single JSON object:

- Success:
  - `{"ok":true,"data":<payload>}`
- Error:
  - `{"ok":false,"error":{"code":"...","message":"...","details":{...}}}`

Calendars payload:

- `[{ "name": "..." }]`

Events payload:

- `[{ "uid": "...", "calendar": "...", "title": "...", "start": "ISO", "end": "ISO", "location": "...", "notes": "...", "url": "..." }]`

Notes:

- v1 uses Calendar.app scripting. If event `uid` cannot be retrieved reliably through AppleScript on some systems, the tool must fail write operations that require `--uid` and instruct the user to migrate to the EventKit backend (v2).

## Safety & Permissions

- Calendar access via AppleScript requires Automation permission:
  - System Settings -> Privacy & Security -> Automation
  - Allow the calling terminal app (Terminal/iTerm) to control Calendar
- `--dry-run` must not modify Calendar data and should not require Calendar access for the write operation path.

## Verification Plan

- `./scripts/cal --help` prints usage without touching Calendar.
- `./scripts/cal calendars list --format json` returns valid JSON.
- `./scripts/cal events list --from <date> --to <date> --format json` returns valid JSON (on a machine with Calendar access).
- `./scripts/cal events create ... --dry-run --format json` returns planned event JSON and does not create an event.

## Future Work (v2)

- Implement the same CLI/JSON contract with Swift + EventKit for stronger UID semantics and better performance.

