import unittest

from lib.dongchedi import extract_params_from_ssr


class ParamsParserTest(unittest.TestCase):
    def test_extract_params_from_ssr_maps_categories_and_values(self) -> None:
        ssr_data = {
            "props": {
                "pageProps": {
                    "rawData": {
                        "properties": [
                            {"text": "基本信息", "key": "base_info", "type": 0},
                            {"text": "官方指导价", "key": "official_price", "type": 1},
                            {"text": "能源类型", "key": "fuel_form", "type": 1},
                            {"text": "主动安全", "key": "", "type": 2},
                            {
                                "text": "主动安全预警系统",
                                "key": "car_warning_system",
                                "type": 3,
                                "sub_list": [
                                    {"key": "lane_warning_system", "text": "车道偏离预警"},
                                    {"key": "front_collision_warning", "text": "前方碰撞预警"},
                                ],
                            },
                        ],
                        "car_info": [
                            {
                                "info": {
                                    "official_price": {"value": "25.8万"},
                                    "fuel_form": {"value": "汽油"},
                                    "lane_warning_system": {"value": "车道偏离预警", "icon_type": 1},
                                    "front_collision_warning": {"value": "前方碰撞预警", "icon_type": 1},
                                }
                            }
                        ],
                    }
                }
            }
        }

        params = extract_params_from_ssr(ssr_data)

        self.assertTrue(any(p.category == "基本信息" and p.name == "官方指导价" and p.value == "25.8万" for p in params))
        self.assertTrue(any(p.category == "基本信息" and p.name == "能源类型" and p.value == "汽油" for p in params))
        self.assertTrue(any(p.category == "主动安全" and p.name == "车道偏离预警" and p.value == "车道偏离预警" for p in params))
        self.assertTrue(any(p.category == "主动安全" and p.name == "前方碰撞预警" and p.value == "前方碰撞预警" for p in params))


if __name__ == "__main__":
    unittest.main()
