import json
import os
import unittest
from pathlib import Path


class FakeBrowser:
    def __init__(self, html: str):
        self.html = html
        self.url = "https://www.dongchedi.com/search?keyword=%E9%98%BF%E7%BB%B4%E5%A1%94"
        self.title = "懂车帝搜索"
        self.visited_urls = []
        self.wait_calls = []

    def goto(self, url: str) -> None:
        self.visited_urls.append(url)

    def wait(self, seconds: float) -> None:
        self.wait_calls.append(seconds)


class SearchScriptCompatibilityTest(unittest.TestCase):
    def setUp(self) -> None:
        self.skill_dir = Path(__file__).resolve().parent.parent
        self.script_path = self.skill_dir / "scripts" / "search.py"
        self.output_path = self.skill_dir / "tmp" / "search-results.json"
        self.raw_html_path = self.skill_dir / "tmp" / "raw-search.html"
        self.metadata_path = self.skill_dir / "tmp" / "search-metadata.json"
        self.original_output = self.output_path.read_text("utf-8") if self.output_path.exists() else None
        self.original_raw_html = self.raw_html_path.read_text("utf-8") if self.raw_html_path.exists() else None
        self.original_metadata = self.metadata_path.read_text("utf-8") if self.metadata_path.exists() else None
        self.output_path.unlink(missing_ok=True)
        self.raw_html_path.unlink(missing_ok=True)
        self.metadata_path.unlink(missing_ok=True)
        self.previous_cwd = Path.cwd()
        os.chdir(self.skill_dir)

    def tearDown(self) -> None:
        os.chdir(self.previous_cwd)
        if self.original_output is None:
            self.output_path.unlink(missing_ok=True)
        else:
            self.output_path.write_text(self.original_output, encoding="utf-8")
        if self.original_raw_html is None:
            self.raw_html_path.unlink(missing_ok=True)
        else:
            self.raw_html_path.write_text(self.original_raw_html, encoding="utf-8")
        if self.original_metadata is None:
            self.metadata_path.unlink(missing_ok=True)
        else:
            self.metadata_path.write_text(self.original_metadata, encoding="utf-8")

    def run_search_script(self, html: str) -> FakeBrowser:
        fake_browser = FakeBrowser(html)
        globals_dict = {
            "__name__": "__main__",
            "KEYWORD": "示例品牌",
            "browser": fake_browser,
        }
        exec(compile(self.script_path.read_text("utf-8"), str(self.script_path), "exec"), globals_dict)
        return fake_browser

    def test_search_script_runs_without___file__in_browser_use_mode(self) -> None:
        fake_html = (
            '<html><script id="__NEXT_DATA__" type="application/json">'
            '{"props":{"pageProps":{"searchData":{"data":['
            '{"series_id":5308,"display":{"series_name":"示例11",'
            '"official_price":"27.99-41.99万","series_type":"中大型SUV"}}'
            ']}}}}</script></html>'
        )

        fake_browser = self.run_search_script(fake_html)

        self.assertTrue(self.output_path.exists())
        self.assertTrue(self.raw_html_path.exists())
        self.assertTrue(self.metadata_path.exists())
        payload = json.loads(self.output_path.read_text("utf-8"))
        metadata = json.loads(self.metadata_path.read_text("utf-8"))
        self.assertEqual(payload[0]["series_id"], "5308")
        self.assertEqual(payload[0]["name"], "示例11")
        self.assertEqual(metadata["keyword"], "示例品牌")
        self.assertEqual(metadata["result_count"], 1)
        self.assertIn("懂车帝搜索", metadata["title"])
        self.assertEqual(len(fake_browser.visited_urls), 1)
        self.assertEqual(fake_browser.wait_calls, [3])

    def test_search_script_fails_fast_on_captcha_interstitial(self) -> None:
        captcha_html = '<html><head><title>验证码中间页</title></head><body><script>window.TTGCaptcha={}</script></body></html>'

        with self.assertRaisesRegex(RuntimeError, "captcha"):
            self.run_search_script(captcha_html)

        self.assertFalse(self.output_path.exists())
        self.assertTrue(self.raw_html_path.exists())
        metadata = json.loads(self.metadata_path.read_text("utf-8"))
        self.assertEqual(metadata["keyword"], "示例品牌")


if __name__ == "__main__":
    unittest.main()
