import json
import os
import subprocess
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPT_PATH = SKILL_DIR / "scripts" / "cal-intent"


class CalendarIntentTest(unittest.TestCase):
    def _run_intent(self, text: str, *, env: dict[str, str] | None = None) -> dict:
        proc = subprocess.run(
            [str(SCRIPT_PATH), text],
            capture_output=True,
            text=True,
            env=env,
            check=True,
        )
        return json.loads(proc.stdout)

    def test_tomorrow_meeting_maps_to_search_plan(self) -> None:
        payload = self._run_intent("明天看看会议")

        self.assertEqual(payload["status"], "resolved")
        self.assertEqual(payload["intent"], "search")
        self.assertEqual(payload["resolved_args"]["query"], "会议")
        self.assertIn("--range tomorrow", payload["next_command"])

    def test_create_request_maps_to_dry_run_create_command(self) -> None:
        env = os.environ.copy()
        env["PRISM_CALENDAR_INTENT_TODAY"] = "2026-03-17"

        payload = self._run_intent("明天下午两点在工作日历创建评审会", env=env)

        self.assertEqual(payload["status"], "resolved")
        self.assertEqual(payload["intent"], "create")
        self.assertEqual(payload["resolved_args"]["calendar"], "工作")
        self.assertEqual(payload["resolved_args"]["title"], "评审会")
        self.assertEqual(payload["resolved_args"]["start"], "2026-03-18T14:00:00+08:00")
        self.assertEqual(payload["resolved_args"]["end"], "2026-03-18T15:00:00+08:00")
        self.assertIn("events create", payload["next_command"])
        self.assertNotIn("--apply", payload["next_command"])

    def test_vague_update_request_degrades_to_search(self) -> None:
        payload = self._run_intent("把那个评审往后挪一点")

        self.assertEqual(payload["status"], "needs_search")
        self.assertEqual(payload["intent"], "update")
        self.assertEqual(payload["resolved_args"]["query"], "评审")
        self.assertIn("events search", payload["next_command"])

    def test_delete_request_requires_search_first(self) -> None:
        payload = self._run_intent("删除下周预算会")

        self.assertEqual(payload["status"], "needs_search")
        self.assertEqual(payload["intent"], "delete")
        self.assertEqual(payload["resolved_args"]["query"], "预算会")
        self.assertIn("--range next7", payload["next_command"])
        self.assertNotIn("events delete", payload["next_command"])

    def test_default_calendar_phrase_uses_environment_default(self) -> None:
        env = os.environ.copy()
        env["PRISM_CALENDAR_DEFAULT"] = "家庭"
        env["PRISM_CALENDAR_INTENT_TODAY"] = "2026-03-17"

        payload = self._run_intent("明天下午两点在默认日历创建体检提醒", env=env)

        self.assertEqual(payload["status"], "resolved")
        self.assertEqual(payload["resolved_args"]["calendar"], "家庭")
        self.assertIn("--calendar 家庭", payload["next_command"])

    def test_explicit_chinese_date_create_request_maps_to_reminder_create_plan(self) -> None:
        env = os.environ.copy()
        env["PRISM_CALENDAR_DEFAULT"] = "日历"
        env["PRISM_CALENDAR_INTENT_TODAY"] = "2026-03-17"

        payload = self._run_intent("在2026年3月19日早上9点加一个日历，提醒我喝一杯咖啡", env=env)

        self.assertEqual(payload["status"], "resolved")
        self.assertEqual(payload["intent"], "create")
        self.assertEqual(payload["resolved_args"]["calendar"], "日历")
        self.assertEqual(payload["resolved_args"]["title"], "提醒我喝一杯咖啡")
        self.assertEqual(payload["resolved_args"]["start"], "2026-03-19T09:00:00+08:00")
        self.assertEqual(payload["resolved_args"]["end"], "2026-03-19T10:00:00+08:00")
        self.assertIn("--title 提醒我喝一杯咖啡", payload["next_command"])
        self.assertNotIn("ambiguous", payload["next_command"])


if __name__ == "__main__":
    unittest.main()
