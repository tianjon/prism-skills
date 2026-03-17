import os
import subprocess
import tempfile
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPT_PATH = SKILL_DIR / "scripts" / "cal"


class CalendarCliPreprocessTest(unittest.TestCase):
    def _run_script(self, *args: str, env: dict[str, str] | None = None) -> list[str]:
        script_text = SCRIPT_PATH.read_text(encoding="utf-8")
        script_text = script_text.replace(
            '/usr/bin/osascript "$backend" "${expanded[@]}"',
            'printf "%s\\n" "${expanded[@]}"',
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            script_copy = root / "cal"
            script_copy.write_text(script_text, encoding="utf-8")
            script_copy.chmod(0o755)
            (root / "calendar.applescript").write_text("-- stub backend\n", encoding="utf-8")

            proc = subprocess.run(
                [str(script_copy), *args],
                capture_output=True,
                text=True,
                env=env,
                check=True,
            )
            return [line for line in proc.stdout.splitlines() if line]

    def test_default_calendar_injects_for_create(self) -> None:
        env = os.environ.copy()
        env["PRISM_CALENDAR_DEFAULT"] = "日历"

        lines = self._run_script(
            "events",
            "create",
            "--title",
            "Test",
            "--start",
            "2026-03-17T10:00:00+08:00",
            "--end",
            "2026-03-17T11:00:00+08:00",
            "--format",
            "json",
            env=env,
        )

        self.assertEqual(
            lines,
            [
                "events",
                "create",
                "--title",
                "Test",
                "--start",
                "2026-03-17T10:00:00+08:00",
                "--end",
                "2026-03-17T11:00:00+08:00",
                "--format",
                "json",
                "--calendar",
                "日历",
            ],
        )

    def test_default_calendar_does_not_inject_for_update_or_delete(self) -> None:
        env = os.environ.copy()
        env["PRISM_CALENDAR_DEFAULT"] = "日历"

        update_lines = self._run_script(
            "events",
            "update",
            "--id",
            "evt-1",
            "--title",
            "Changed",
            "--format",
            "json",
            env=env,
        )
        delete_lines = self._run_script(
            "events",
            "delete",
            "--id",
            "evt-1",
            "--format",
            "json",
            env=env,
        )

        self.assertNotIn("--calendar", update_lines)
        self.assertNotIn("日历", update_lines)
        self.assertNotIn("--calendar", delete_lines)
        self.assertNotIn("日历", delete_lines)


if __name__ == "__main__":
    unittest.main()
