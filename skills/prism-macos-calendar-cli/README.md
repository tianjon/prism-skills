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

Optional: set a default calendar name (so you can omit `--calendar` for list/search/create):

```bash
export PRISM_CALENDAR_DEFAULT='日历'
./scripts/cal events list --range tomorrow --format pretty
```

For fuzzy requests, use the intent layer first:

```bash
./scripts/cal-intent "明天看看会议"
./scripts/cal-intent "明天下午两点在工作日历创建评审会"
./scripts/cal-intent "在2026年3月19日早上9点加一个日历，提醒我喝一杯咖啡"
./scripts/cal-intent "把那个评审往后挪一点"
```

`cal-intent` emits a JSON plan with:

- `status=resolved`: deterministic next command is ready
- `status=needs_search`: run the returned search/list command first
- `status=ambiguous`: stop and gather more information

Write requests stay safe by default:

- `cal-intent` does not emit `--apply`
- if `PRISM_CALENDAR_DEFAULT` is set, create requests may inherit it automatically
- `create/update/delete` should still be previewed via dry-run before writing

If Automation permission is denied, see `references/automation-permissions.md`.

For the full contract and failure handling, read `SKILL.md`.
