import json
import os
import unittest
from pathlib import Path


class FakeBrowser:
    def __init__(self, html_by_url: dict[str, str]):
        self.html_by_url = html_by_url
        self.html = ""
        self.visited_urls = []
        self.wait_calls = []

    def goto(self, url: str) -> None:
        self.visited_urls.append(url)
        self.html = self.html_by_url[url]

    def wait(self, seconds: float) -> None:
        self.wait_calls.append(seconds)


class ParamsScriptCompatibilityTest(unittest.TestCase):
    def setUp(self) -> None:
        self.skill_dir = Path(__file__).resolve().parent.parent
        self.script_path = self.skill_dir / "scripts" / "params.py"
        self.input_path = self.skill_dir / "tmp" / "all-configs.json"
        self.output_path = self.skill_dir / "tmp" / "all-configs-with-params.json"
        self.original_input = self.input_path.read_text("utf-8") if self.input_path.exists() else None
        self.original_output = self.output_path.read_text("utf-8") if self.output_path.exists() else None
        self.previous_cwd = Path.cwd()
        os.chdir(self.skill_dir)

    def tearDown(self) -> None:
        os.chdir(self.previous_cwd)
        if self.original_input is None:
            self.input_path.unlink(missing_ok=True)
        else:
            self.input_path.write_text(self.original_input, encoding="utf-8")
        if self.original_output is None:
            self.output_path.unlink(missing_ok=True)
        else:
            self.output_path.write_text(self.original_output, encoding="utf-8")

    def test_params_script_prefers_structured_ssr_data(self) -> None:
        self.input_path.write_text(
            json.dumps([
                {
                    "car_id": "255689",
                    "car_name": "325i M运动套装",
                    "series_name": "宝马3系",
                    "series_id": "145",
                    "brand_name": "宝马",
                    "brand": "宝马",
                }
            ], ensure_ascii=False),
            encoding="utf-8",
        )
        payload = {
            "props": {
                "pageProps": {
                    "rawData": {
                        "properties": [
                            {"text": "基本信息", "key": "base_info", "type": 0},
                            {"text": "官方指导价", "key": "official_price", "type": 1},
                        ],
                        "car_info": [
                            {"info": {"official_price": {"value": "25.8万"}}}
                        ],
                    }
                }
            }
        }
        html = '<html><script id="__NEXT_DATA__" type="application/json">' + json.dumps(payload, ensure_ascii=False) + '</script></html>'
        fake_browser = FakeBrowser({"https://www.dongchedi.com/auto/params-carIds-255689": html})
        globals_dict = {
            "__name__": "__main__",
            "browser": fake_browser,
        }

        exec(compile(self.script_path.read_text("utf-8"), str(self.script_path), "exec"), globals_dict)

        result = json.loads(self.output_path.read_text("utf-8"))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["params"][0]["name"], "官方指导价")
        self.assertEqual(result[0]["params"][0]["value"], "25.8万")
        self.assertIsNone(result[0]["params_error"])


if __name__ == "__main__":
    unittest.main()
