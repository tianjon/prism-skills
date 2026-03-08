import unittest

from lib.dongchedi import extract_car_configs, extract_series_info


class SeriesConfigParserTest(unittest.TestCase):
    def test_extract_car_configs_supports_nested_info_entries(self) -> None:
        ssr_data = {
            "props": {
                "pageProps": {
                    "carModelsData": {
                        "tab_list": [
                            {
                                "tab_key": "online_all",
                                "data": [
                                    {
                                        "type": 1137,
                                        "info": {"name": "2026款-宝马3系 / 标轴"},
                                    },
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
                                    },
                                ],
                            }
                        ]
                    }
                }
            }
        }

        configs = extract_car_configs(ssr_data)

        self.assertEqual(len(configs), 1)
        self.assertEqual(configs[0].car_id, "255689")
        self.assertEqual(configs[0].car_name, "325i M运动套装")
        self.assertEqual(configs[0].series_name, "宝马3系")
        self.assertEqual(configs[0].brand_name, "宝马")


    def test_extract_car_configs_accepts_string_type_marker(self) -> None:
        ssr_data = {
            "props": {
                "pageProps": {
                    "carModelsData": {
                        "tab_list": [
                            {
                                "tab_key": "online_all",
                                "data": [
                                    {
                                        "type": "1115",
                                        "info": {
                                            "car_id": 255690,
                                            "car_name": "325Li M运动套装",
                                            "price": "27.80万",
                                            "year": 2026,
                                            "series_name": "宝马3系",
                                            "series_id": 145,
                                            "brand_name": "宝马",
                                        },
                                    }
                                ],
                            }
                        ]
                    }
                }
            }
        }

        configs = extract_car_configs(ssr_data)

        self.assertEqual(len(configs), 1)
        self.assertEqual(configs[0].car_name, "325Li M运动套装")

    def test_extract_series_info_supports_page_props_fallbacks(self) -> None:
        ssr_data = {
            "props": {
                "pageProps": {
                    "seriesName": "宝马3系",
                    "seriesHomeHead": {
                        "series_type": "轿车",
                        "sub_title": "25.20-39.98万",
                    },
                    "overviewData": {
                        "energy_type": "汽油",
                    },
                }
            }
        }

        info = extract_series_info(ssr_data)

        self.assertEqual(info["name"], "宝马3系")
        self.assertEqual(info["level"], "轿车")
        self.assertEqual(info["price_range"], "25.20-39.98万")
        self.assertEqual(info["energy_type"], "汽油")


if __name__ == "__main__":
    unittest.main()
