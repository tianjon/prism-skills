# macOS Automation Permissions (Calendar.app)

This skill controls Calendar.app using Apple Events (`osascript`). macOS may block this until you grant Automation permission.

## Symptoms

- The command fails with an AppleScript error mentioning permission/automation.
- Calendar data cannot be read or modified even though Calendar.app works normally.

## Fix

1. Open **System Settings**.
2. Go to **Privacy & Security** -> **Automation**.
3. Find your terminal app (Terminal / iTerm / whichever launches `./scripts/cal`).
4. Enable permission to control **Calendar** (Calendar.app).

If the terminal app is not listed:

- Run a read command once (for example: `./scripts/cal calendars list`) to trigger the system prompt.

## Reset (If It Gets Stuck)

You can try removing the terminal app's Automation permission entry and re-running the command to re-trigger the prompt.

Chinese UI hints:

- 系统设置 -> 隐私与安全性 -> 自动化
- 允许 Terminal/iTerm 控制“日历(Calendar)”

