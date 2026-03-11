import unittest

from lib.dongchedi import extract_car_configs, extract_search_results


class HistoryModeParserTest(unittest.TestCase):
    def test_extract_search_results_can_include_historical_series(self) -> None:
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
                                                            "series_id": 145,
                                                            "name": "宝马3系",
                                                            "pricelimits": "22.66-31.99万",
                                                            "level": "轿车",
                                                            "online_car_count": 13,
                                                            "is_salestop": False,
                                                        },
                                                        {
                                                            "series_id": 143,
                                                            "name": "宝马1系",
                                                            "pricelimits": "停售",
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

        self.assertEqual([item.series_id for item in results], ["145", "143"])
        self.assertEqual(results[1].name, "宝马1系")

    def test_extract_car_configs_can_include_offline_tab(self) -> None:
        ssr_data = {
            "props": {
                "pageProps": {
                    "carModelsData": {
                        "tab_list": [
                            {
                                "tab_key": "offline",
                                "data": [
                                    {"type": 1137, "info": {"name": "2019款"}},
                                    {
                                        "type": "1115",
                                        "info": {
                                            "car_id": 90001,
                                            "car_name": "118i 时尚型",
                                            "price": "20.38万",
                                            "year": 2019,
                                            "series_name": "宝马1系",
                                            "series_id": 143,
                                            "brand_name": "宝马",
                                        },
                                    },
                                ],
                            }
                        ]
                    }
                }
            }
        }

        configs = extract_car_configs(ssr_data, include_history=True)

        self.assertEqual(len(configs), 1)
        self.assertEqual(configs[0].series_name, "宝马1系")
        self.assertEqual(configs[0].car_name, "118i 时尚型")


if __name__ == "__main__":
    unittest.main()
