# prism-macos-calendar-cli Agent Usability Improvements

Date: 2026-03-16

## Goal

Optimize `prism-macos-calendar-cli` for human-in-the-loop use via an agent:

- fewer required flags for common queries
- no missing “跨天/长事件” when listing events in a range
- stable, sorted outputs
- safer writes by default (plan first, apply explicitly)
- clearer remediation for permissions and ambiguous selectors

## Scope (This Change)

P0:

- Add `--range` shortcuts for list/search: `today|tomorrow|next7|thisweek|next30`
- Add `--limit N` for list/search
- Change list/search filtering to “overlap” semantics: `start < to && end > from`
- Sort results by start date ascending
- Add `--format pretty` for agent-friendly human output

P1:

- Write commands default to dry-run unless `--apply` is provided
- Improve error payloads with hints for disambiguation
- Add `cal doctor` to quickly diagnose permissions/runtime problems

## Tasks

### Task 1: Plan + Docs Updates

**Files:**
- Modify: `skills/prism-macos-calendar-cli/SKILL.md`
- Modify: `skills/prism-macos-calendar-cli/README.md`

Steps:

1. Update CLI contract to include `--range`, `--limit`, `--format pretty`, `--apply`, and `doctor`.
2. Document the new range/overlap semantics and the default dry-run behavior.

### Task 2: Bash CLI Enhancements

**Files:**
- Modify: `skills/prism-macos-calendar-cli/scripts/cal`

Steps:

1. Implement `--range` expansion into `--from/--to` for list/search (macOS `date -v`).
2. Keep all user inputs passed as argv entries to `osascript`.

### Task 3: Backend Enhancements (AppleScriptObjC)

**Files:**
- Modify: `skills/prism-macos-calendar-cli/scripts/calendar.applescript`

Steps:

1. Implement overlap filtering in `collect_events_in_range`.
2. Add `start_ts` for sorting and strip it before output.
3. Add `--limit` trimming after sort.
4. Add `pretty` output formatting (short local timestamps).
5. Implement default dry-run unless `--apply`.
6. Add `doctor` command.
7. Improve error details for ambiguous/not-found/calendar-not-found.

### Task 4: Verification

Commands:

1. Compile: `osacompile -o /tmp/prism-macos-calendar-cli-test.scpt skills/prism-macos-calendar-cli/scripts/calendar.applescript`
2. Help: `skills/prism-macos-calendar-cli/scripts/cal --help`
3. Doctor: `skills/prism-macos-calendar-cli/scripts/cal doctor`
4. JSON parse sanity (JXA): `... | osascript -l JavaScript -e 'ObjC.import(\"Foundation\"); var data=$.NSFileHandle.fileHandleWithStandardInput.readDataToEndOfFile; var str=ObjC.unwrap($.NSString.alloc.initWithDataEncoding(data,$.NSUTF8StringEncoding)); JSON.parse(str);'`
5. Range shortcuts: `... events list --range today --limit 5 --format pretty`
6. Writes are safe by default: `... events create ... --format json` should show `dry_run:true` unless `--apply`.

