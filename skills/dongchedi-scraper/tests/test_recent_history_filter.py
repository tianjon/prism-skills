import unittest

from lib.dongchedi import extract_search_results, filter_recent_history_configs
from lib.types import CarConfig


class RecentHistoryFilterTest(unittest.TestCase):
    def test_extract_search_results_include_history_skips_unreleased(self) -> None:
        ssr_data = {
            "props": {
                "pageProps": {
                    "searchData": {
                        "data": [
                            {
                                "cell_type": 129,
                                "display": {
                                    "sub_brand_list": {
                                        "item": [
                                            {
                                                "series_list": {
                                                    "item": [
                                                        {
                                                            "series_id": 143,
                                                            "name": "宝马1系",
                                                            "pricelimits": "停售",
                                                            "level": "轿车",
                                                            "online_car_count": 0,
                                                            "is_salestop": True,
                                                        },
                                                        {
                                                            "series_id": 9272,
                                                            "name": "Vision Neue Klasse",
                                                            "pricelimits": "未上市",
                                                            "level": "轿车",
                                                            "online_car_count": 0,
                                                            "is_salestop": True,
                                                        },
                                                    ]
                                                }
                                            }
                                        ]
                                    }
                                },
                            }
                        ]
                    }
                }
            }
        }

        results = extract_search_results(ssr_data, include_history=True)

        self.assertEqual([item.series_id for item in results], ["143"])

    def test_filter_recent_history_configs_keeps_recent_years_only(self) -> None:
        configs = [
            CarConfig(car_id="1", car_name="2026款 A", year="2026", series_name="宝马1系", series_id="143", brand_name="宝马"),
            CarConfig(car_id="2", car_name="2024款 B", year="2024", series_name="宝马1系", series_id="143", brand_name="宝马"),
            CarConfig(car_id="3", car_name="2023款 C", year="2023", series_name="宝马1系", series_id="143", brand_name="宝马"),
        ]

        kept = filter_recent_history_configs(configs, cutoff_year=2024)

        self.assertEqual([item.car_id for item in kept], ["1", "2"])


if __name__ == "__main__":
    unittest.main()
