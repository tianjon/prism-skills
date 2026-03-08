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


class ConfigsScriptCompatibilityTest(unittest.TestCase):
    def setUp(self) -> None:
        self.skill_dir = Path(__file__).resolve().parent.parent
        self.script_path = self.skill_dir / "scripts" / "configs.py"
        self.series_list_path = self.skill_dir / "tmp" / "series-list.json"
        self.output_path = self.skill_dir / "tmp" / "all-configs.json"
        self.original_series_list = self.series_list_path.read_text("utf-8") if self.series_list_path.exists() else None
        self.original_output = self.output_path.read_text("utf-8") if self.output_path.exists() else None
        self.previous_cwd = Path.cwd()
        os.chdir(self.skill_dir)

    def tearDown(self) -> None:
        os.chdir(self.previous_cwd)
        if self.original_series_list is None:
            self.series_list_path.unlink(missing_ok=True)
        else:
            self.series_list_path.write_text(self.original_series_list, encoding="utf-8")
        if self.original_output is None:
            self.output_path.unlink(missing_ok=True)
        else:
            self.output_path.write_text(self.original_output, encoding="utf-8")

    def test_configs_script_extracts_nested_info_series_configs(self) -> None:
        self.series_list_path.write_text(
            json.dumps([
                {
                    "series_id": "145",
                    "name": "宝马3系",
                    "brand": "宝马",
                    "level": "轿车",
                    "energy_type": "",
                    "is_target": True,
                }
            ], ensure_ascii=False),
            encoding="utf-8",
        )
        payload = {
            "props": {
                "pageProps": {
                    "seriesName": "宝马3系",
                    "carModelsData": {
                        "tab_list": [
                            {
                                "tab_key": "online_all",
                                "data": [
                                    {
                                        "type": 1115,
                                        "info": {
                                            "car_id": 255689,
                                            "car_name": "325i M运动套装",
                                            "price": "25.80万",
                                            "year": 2026,
                                            "series_name": "宝马3系",
                                            "series_id": 145,
                                            "brand_name": "宝马",
                                        },
                                    }
                                ],
                            }
                        ]
                    },
                }
            }
        }
        html = (
            '<html><script id="__NEXT_DATA__" type="application/json">'
            + json.dumps(payload, ensure_ascii=False)
            + '</script></html>'
        )
        fake_browser = FakeBrowser({"https://www.dongchedi.com/auto/series/145": html})
        globals_dict = {
            "__name__": "__main__",
            "browser": fake_browser,
        }

        exec(compile(self.script_path.read_text("utf-8"), str(self.script_path), "exec"), globals_dict)

        result = json.loads(self.output_path.read_text("utf-8"))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["car_id"], "255689")
        self.assertEqual(result[0]["car_name"], "325i M运动套装")


if __name__ == "__main__":
    unittest.main()
