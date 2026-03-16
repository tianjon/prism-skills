# prism-macos-calendar-cli

Operate macOS Calendar.app from the command line using built-in `osascript` (AppleScriptObjC). No Python dependency.

## Quickstart

```bash
cd skills/prism-macos-calendar-cli
./scripts/cal --help
./scripts/cal doctor
./scripts/cal calendars list --format json
./scripts/cal events list --range today --limit 10 --format pretty
./scripts/cal events search --query 会议 --range next7 --format json
./scripts/cal events create --calendar '日历' --title 'Test' --start '2026-03-16T10:00:00+08:00' --end '2026-03-16T10:30:00+08:00' --format json
# Actually write (explicit):
./scripts/cal events create --calendar '日历' --title 'Test' --start '2026-03-16T10:00:00+08:00' --end '2026-03-16T10:30:00+08:00' --apply --format json
```

If Automation permission is denied, see `references/automation-permissions.md`.

For the full contract and failure handling, read `SKILL.md`.
