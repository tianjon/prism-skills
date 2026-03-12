import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from scripts import diff as diff_script


class DiffScriptTest(unittest.TestCase):
    def test_tmp_dir_uses_dongchedi_tmp_dir_environment(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / "all-configs-with-params.json").write_text("[]", encoding="utf-8")

            calls: list[list[str]] = []

            def fake_run(cmd, capture_output=None, text=None, timeout=None):
                calls.append(cmd)
                return MagicMock(returncode=0, stdout="")

            with patch.dict(os.environ, {"DONGCHEDI_TMP_DIR": str(tmp_path)}), \
                 patch.object(diff_script.sys, "argv", ["diff.py"]), \
                 patch("scripts.diff.subprocess.run", side_effect=fake_run), \
                 patch("scripts.diff.sys.exit") as exit_mock:
                diff_script.main()

            # It should not call sys.exit(1) due to missing file when the env var is set.
            exit_mock.assert_not_called()

    def test_discontinued_scans_current_trim_folders_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            payload = [{
                "car_id": "123",
                "car_name": "2025款 DM-i 120KM领先型",
                "year": "2025",
                "series_name": "秦L DM",
                "series_id": "9796",
                "brand_name": "比亚迪",
                "brand": "比亚迪",
                "price": "8.98万",
            }]
            (tmp_path / "all-configs-with-params.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

            calls: list[list[str]] = []

            def fake_run(cmd, capture_output=None, text=None, timeout=None):
                calls.append(cmd)
                return MagicMock(returncode=0, stdout="")

            with patch.dict(os.environ, {"DONGCHEDI_TMP_DIR": str(tmp_path)}), \
                 patch.object(diff_script.sys, "argv", ["diff.py"]), \
                 patch("scripts.diff.subprocess.run", side_effect=fake_run):
                diff_script.main()

            self.assertIn(
                ["obsidian", "files", "folder=汽车/品牌库/比亚迪/秦L DM/当前款型", "ext=md"],
                calls,
            )

    def test_skip_discontinued_avoids_files_listing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            payload = [{
                "car_id": "1",
                "car_name": "2025款 1",
                "series_name": "A",
                "series_id": "100",
                "brand": "B",
                "brand_name": "B",
                "price": "10万",
                "year": "2025",
            }]
            (tmp_path / "all-configs-with-params.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

            def fake_run(cmd, capture_output=None, text=None, timeout=None):
                # If we ever call obsidian files, the behavior is wrong for this flag.
                if cmd[:2] == ["obsidian", "files"]:
                    raise AssertionError("obsidian files should not be called with --skip-discontinued")
                return MagicMock(returncode=0, stdout="")

            with patch.dict(os.environ, {"DONGCHEDI_TMP_DIR": str(tmp_path)}), \
                 patch.object(diff_script.sys, "argv", ["diff.py", "--skip-discontinued"]), \
                 patch("scripts.diff.subprocess.run", side_effect=fake_run):
                diff_script.main()
