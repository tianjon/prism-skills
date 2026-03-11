import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.publish_competitor_analysis import resolve_browser_use


class PublishCompetitorAnalysisRuntimeTest(unittest.TestCase):
    def test_resolve_browser_use_prefers_active_python_environment(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            bin_dir = Path(tmpdir) / "bin"
            python_bin = bin_dir / "python"
            browser_use_bin = bin_dir / "browser-use"
            bin_dir.mkdir(parents=True)
            python_bin.write_text("", encoding="utf-8")
            browser_use_bin.write_text("", encoding="utf-8")

            with patch("scripts.publish_competitor_analysis.sys.executable", str(python_bin)):
                with patch("scripts.publish_competitor_analysis.shutil.which", return_value=None):
                    self.assertEqual(resolve_browser_use(), str(browser_use_bin.resolve()))


if __name__ == "__main__":
    unittest.main()
