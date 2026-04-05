import json
import os
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import patch


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


class FakeResponse(BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False


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

    def test_configs_script_fetches_series_html_without_browser(self) -> None:
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

        globals_dict = {
            "__name__": "__main__",
        }

        with patch("urllib.request.urlopen", return_value=FakeResponse(html.encode("utf-8"))):
            exec(compile(self.script_path.read_text("utf-8"), str(self.script_path), "exec"), globals_dict)

        result = json.loads(self.output_path.read_text("utf-8"))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["series_name"], "宝马3系")
        self.assertEqual(result[0]["car_id"], "255689")

    def test_configs_script_merges_recent_offline_configs_for_active_series(self) -> None:
        self.series_list_path.write_text(
            json.dumps([
                {
                    "series_id": "3352",
                    "name": "小鹏P7",
                    "brand": "小鹏汽车",
                    "level": "中型车",
                    "energy_type": "纯电动",
                    "is_target": True,
                }
            ], ensure_ascii=False),
            encoding="utf-8",
        )
        ssr_payload = {
            "props": {
                "pageProps": {
                    "seriesName": "小鹏P7",
                    "carModelsData": {
                        "tab_list": [
                            {
                                "tab_key": "online_all",
                                "data": [
                                    {
                                        "type": 1115,
                                        "info": {
                                            "car_id": 257034,
                                            "car_name": "702 Max",
                                            "price": "20.38万",
                                            "year": 2025,
                                            "series_name": "小鹏P7",
                                            "series_id": 3352,
                                            "brand_name": "小鹏汽车",
                                        },
                                    }
                                ],
                            },
                            {"tab_key": "offline", "data": []},
                        ]
                    },
                }
            }
        }
        api_payload = {
            "status": 0,
            "data": {
                "tab_list": [
                    {
                        "tab_key": "online_all",
                        "data": [
                            {
                                "type": 1115,
                                "info": {
                                    "car_id": 257034,
                                    "car_name": "702 Max",
                                    "price": "20.38万",
                                    "year": 2025,
                                    "series_name": "小鹏P7",
                                    "series_id": 3352,
                                    "brand_name": "小鹏汽车",
                                },
                            }
                        ],
                    },
                    {
                        "tab_key": "offline",
                        "data": [
                            {"type": 1137, "info": {"name": "2025款"}},
                            {
                                "type": 1115,
                                "info": {
                                    "car_id": 257031,
                                    "car_name": "702 长续航 Ultra",
                                    "price": "21.98万",
                                    "year": 2025,
                                    "series_name": "小鹏P7",
                                    "series_id": 3352,
                                    "brand_name": "小鹏汽车",
                                },
                            },
                            {"type": 1137, "info": {"name": "2023款"}},
                            {
                                "type": 1115,
                                "info": {
                                    "car_id": 230001,
                                    "car_name": "586E",
                                    "price": "23.99万",
                                    "year": 2023,
                                    "series_name": "小鹏P7",
                                    "series_id": 3352,
                                    "brand_name": "小鹏汽车",
                                },
                            },
                        ],
                    },
                ]
            },
        }
        html = (
            '<html><script id="__NEXT_DATA__" type="application/json">'
            + json.dumps(ssr_payload, ensure_ascii=False)
            + "</script></html>"
        )

        def fake_urlopen(request, timeout=30):
            url = request.full_url if hasattr(request, "full_url") else str(request)
            if url == "https://www.dongchedi.com/auto/series/3352":
                return FakeResponse(html.encode("utf-8"))
            if "/motor/pc/car/series/car_list?" in url and "series_id=3352" in url:
                return FakeResponse(json.dumps(api_payload, ensure_ascii=False).encode("utf-8"))
            raise AssertionError(f"unexpected url: {url}")

        globals_dict = {
            "__name__": "__main__",
        }

        with patch.dict(os.environ, {"DONGCHEDI_INCLUDE_HISTORY": "1", "DONGCHEDI_HISTORY_CUTOFF_YEAR": "2024"}, clear=False):
            with patch("urllib.request.urlopen", side_effect=fake_urlopen):
                exec(compile(self.script_path.read_text("utf-8"), str(self.script_path), "exec"), globals_dict)

        result = json.loads(self.output_path.read_text("utf-8"))
        self.assertEqual([item["car_name"] for item in result], ["702 Max", "702 长续航 Ultra"])


if __name__ == "__main__":
    unittest.main()
