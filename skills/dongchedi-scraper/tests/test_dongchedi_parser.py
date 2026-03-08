import unittest

from lib.dongchedi import extract_search_results, parse_ssr_data


class SearchResultParserTest(unittest.TestCase):
    def test_extract_search_results_from_brand_card_series_list(self) -> None:
        ssr_data = {
            "props": {
                "pageProps": {
                    "searchData": {
                        "data": [
                            {
                                "cell_type": 129,
                                "display": {
                                    "brand_name": "示例品牌",
                                    "sub_brand_list": {
                                        "item": [
                                            {
                                                "series_list": {
                                                    "item": [
                                                        {
                                                            "series_id": 5308,
                                                            "name": "示例 11",
                                                            "pricelimits": "27.99-41.99万",
                                                            "level": "SUV",
                                                            "is_salestop": False,
                                                        },
                                                        {
                                                            "series_id": 25692,
                                                            "name": "示例VISION XPECTRA概念车",
                                                            "pricelimits": "未上市",
                                                            "level": "轿车",
                                                            "is_salestop": True,
                                                        },
                                                    ]
                                                }
                                            }
                                        ]
                                    },
                                },
                            }
                        ]
                    }
                }
            }
        }

        results = extract_search_results(ssr_data)

        self.assertEqual([item.series_id for item in results], ["5308"])
        self.assertEqual(results[0].name, "示例 11")
        self.assertEqual(results[0].price_range, "27.99-41.99万")
        self.assertEqual(results[0].level, "SUV")


    def test_extract_search_results_from_series_tabs_brand_card(self) -> None:
        ssr_data = {
            "props": {
                "pageProps": {
                    "searchData": {
                        "data": [
                            {
                                "cell_type": 184,
                                "display": {
                                    "see_more_text": "查看全部车系(114)",
                                    "series_tabs": [
                                        {
                                            "series_list": [
                                                {
                                                    "series_id": 101,
                                                    "name": "比亚迪 汉",
                                                    "price": "16.58-25.98万",
                                                    "level": "中大型车",
                                                    "is_salestop": False,
                                                    "online_car_count": 9,
                                                },
                                                {
                                                    "series_id": 102,
                                                    "name": "比亚迪 概念车",
                                                    "price": "未上市",
                                                    "level": "概念车",
                                                    "is_salestop": True,
                                                    "online_car_count": 0,
                                                },
                                            ]
                                        }
                                    ],
                                },
                            }
                        ]
                    }
                }
            }
        }

        results = extract_search_results(ssr_data)

        self.assertEqual([item.series_id for item in results], ["101"])
        self.assertEqual(results[0].name, "比亚迪 汉")
        self.assertEqual(results[0].price_range, "16.58-25.98万")
        self.assertEqual(results[0].level, "中大型车")

    def test_extract_search_results_from_series_tabs_item_dict(self) -> None:
        ssr_data = {
            "props": {
                "pageProps": {
                    "searchData": {
                        "data": [
                            {
                                "cell_type": 184,
                                "display": {
                                    "series_tabs": [
                                        {
                                            "sub_brand_name": "热门车系",
                                            "series_list": {
                                                "item": [
                                                    {
                                                        "series_id": 9796,
                                                        "name": "秦L DM",
                                                        "pricelimits": "8.98-14.38万",
                                                        "level": "轿车",
                                                        "online_car_count": 10,
                                                        "is_salestop": False,
                                                    },
                                                    {
                                                        "series_id": 20000,
                                                        "name": "未上市车型",
                                                        "pricelimits": "未上市",
                                                        "level": "轿车",
                                                        "online_car_count": 0,
                                                        "is_salestop": False,
                                                    },
                                                ]
                                            },
                                        }
                                    ]
                                },
                            }
                        ]
                    }
                }
            }
        }

        results = extract_search_results(ssr_data)

        self.assertEqual([item.series_id for item in results], ["9796"])
        self.assertEqual(results[0].name, "秦L DM")
        self.assertEqual(results[0].price_range, "8.98-14.38万")
        self.assertEqual(results[0].level, "轿车")


    def test_parse_ssr_data_handles_embedded_script_closer_in_json_string(self) -> None:
        html = (
            '<html><body><script id="__NEXT_DATA__" type="application/json">'
            '{"props":{"pageProps":{"searchData":{"data":[],'
            '"note":"literal </script> inside json string"}}}}'
            '</script><div>after</div></body></html>'
        )

        parsed = parse_ssr_data(html)

        self.assertIn("props", parsed)
        self.assertEqual(
            parsed["props"]["pageProps"]["searchData"]["note"],
            "literal </script> inside json string",
        )

if __name__ == "__main__":
    unittest.main()
