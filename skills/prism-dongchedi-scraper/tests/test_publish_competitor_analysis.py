import sys
import unittest
from unittest.mock import call, patch

from scripts import publish_competitor_analysis


class PublishCompetitorAnalysisRuntimeTest(unittest.TestCase):
    def test_resolve_browser_use_uses_shared_runtime_resolver(self) -> None:
        with patch("scripts.publish_competitor_analysis.ensure_python_available"), \
             patch("scripts.publish_competitor_analysis.resolve_runtime", return_value=("/tmp/python", "/tmp/browser-use")):
            self.assertEqual(publish_competitor_analysis.resolve_browser_use(), "/tmp/browser-use")

    def test_main_uses_resolved_python_and_browser_use(self) -> None:
        with patch.object(sys, "argv", ["publish_competitor_analysis.py"]), \
             patch("scripts.publish_competitor_analysis.resolve_runtime_pair", return_value=("/tmp/python", "/tmp/browser-use")), \
             patch("scripts.publish_competitor_analysis.run_step") as run_step:
            publish_competitor_analysis.main()

        self.assertEqual(
            run_step.call_args_list,
            [
                call("Build series-list", ["/tmp/python", "scripts/build_series_list.py"]),
                call("Open browser", ["/tmp/browser-use", "open", "https://www.dongchedi.com"]),
                call("Collect configs", ["/tmp/browser-use", "python", "--file", "scripts/configs.py"]),
                call("Collect params", ["/tmp/browser-use", "python", "--file", "scripts/params.py"]),
                call("Diff against Obsidian", ["/tmp/python", "scripts/diff.py"]),
                call("Store to Obsidian", ["/tmp/python", "scripts/store.py", "--competitors", "--changelog"]),
                call("Close browser", ["/tmp/browser-use", "close"]),
            ],
        )


if __name__ == "__main__":
    unittest.main()
