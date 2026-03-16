# prism-macos-calendar-cli Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a new skill that provides a macOS-built-in CLI for listing/searching/creating/updating/deleting Calendar events without any Python dependency.

**Architecture:** A `bash` CLI (`scripts/cal`) forwards arguments as argv to `osascript` running an AppleScriptObjC backend (`scripts/calendar.applescript`). The AppleScript performs Calendar.app operations and serializes results to JSON using `Foundation` (`NSJSONSerialization`), with ISO 8601 parsing/formatting done via `NSDateFormatter`.

**Tech Stack:** bash, `osascript`, AppleScriptObjC (`use framework "Foundation"`), Calendar.app automation (Apple Events), macOS Automation/TCC permissions.

---

### Task 1: Scaffold The New Skill Directory

**Files:**
- Create: `skills/prism-macos-calendar-cli/` (via template)

**Step 1: Create scaffold**

Run: `./scripts/new-skill.sh prism-macos-calendar-cli`

Expected: directory created under `skills/prism-macos-calendar-cli/`.

**Step 2: Commit**

Run:

```bash
git add skills/prism-macos-calendar-cli
git commit -m "chore: scaffold prism-macos-calendar-cli skill"
```

---

### Task 2: Define The Skill Contract

**Files:**
- Modify: `skills/prism-macos-calendar-cli/SKILL.md`
- Create: `skills/prism-macos-calendar-cli/references/automation-permissions.md`

**Step 1: Update SKILL.md**

Ensure:
- no Python runtime requirements
- exact supported commands, flags, and output contract
- explicit failure handling and permission recovery steps

**Step 2: Add permissions reference**

Document:
- System Settings path for Automation permissions
- how to reset permissions if stuck

**Step 3: Commit**

Run:

```bash
git add skills/prism-macos-calendar-cli/SKILL.md skills/prism-macos-calendar-cli/references/automation-permissions.md
git commit -m "docs: define prism-macos-calendar-cli contract"
```

---

### Task 3: Implement CLI Entrypoint (bash)

**Files:**
- Create: `skills/prism-macos-calendar-cli/scripts/cal`

**Step 1: Implement argument parsing and dispatch**

Requirements:
- `--help` and `help` print usage without touching Calendar
- pass all user-provided values as separate argv entries to `osascript` (no unsafe interpolation)
- support `--format json|text` (default `text`)
- support `--dry-run` for write commands

**Step 2: Smoke check**

Run:
- `skills/prism-macos-calendar-cli/scripts/cal --help`

Expected:
- prints usage
- exit code 0

**Step 3: Commit**

Run:

```bash
git add skills/prism-macos-calendar-cli/scripts/cal
git commit -m "feat: add cal bash entrypoint"
```

---

### Task 4: Implement AppleScript Backend (JSON + Time)

**Files:**
- Create: `skills/prism-macos-calendar-cli/scripts/calendar.applescript`

**Step 1: Implement common helpers**

Helpers:
- parse argv into subcommand + flags
- ISO 8601 parse (date-only and date-time)
- ISO 8601 format
- JSON serialization (`NSJSONSerialization`)
- error output: `{"ok":false,"error":{...}}` for json format

**Step 2: Implement read commands**

- calendars list
- events list (time range, optional calendar)
- events search (query + time range, optional calendar)

**Step 3: Implement write commands**

- events create (requires calendar, title, start, end)
- events update (requires uid; optional calendar to disambiguate)
- events delete (requires uid; optional calendar)
- `--dry-run` returns planned changes without writing

**Step 4: Smoke check JSON validity without Python**

Run (example; replace dates as needed):
- `skills/prism-macos-calendar-cli/scripts/cal calendars list --format json | osascript -l JavaScript -e 'JSON.parse(readline());'`

Expected:
- exit code 0 (valid JSON)

Note: If Calendar Automation permission is not granted, command is expected to fail with a clear remediation message.

**Step 5: Commit**

Run:

```bash
git add skills/prism-macos-calendar-cli/scripts/calendar.applescript
git commit -m "feat: add osascript backend for calendar operations"
```

---

### Task 5: End-to-End Verification (Non-Destructive)

**Files:**
- None (optionally add `tmp/` example outputs if they do not contain private data)

**Step 1: Dry-run write path**

Run:

- `skills/prism-macos-calendar-cli/scripts/cal events create --calendar 'Calendar' --title 'Test' --start '2026-03-16T10:00:00+08:00' --end '2026-03-16T10:30:00+08:00' --dry-run --format json`

Expected:
- ok=true JSON
- no event created

**Step 2: Commit (if any doc tweaks)**

Run:

```bash
git status --porcelain
```

If changes exist, commit them with a scoped message.

