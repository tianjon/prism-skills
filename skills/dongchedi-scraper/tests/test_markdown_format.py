import unittest

from lib.markdown import format_config_note
from lib.types import CarConfig, ParamItem


class MarkdownFormatTest(unittest.TestCase):
    def test_format_config_note_sanitizes_multiline_table_values(self) -> None:
        config = CarConfig(
            car_id="1",
            car_name="Elite 纯电版",
            series_name="阿维塔 06",
            series_id="10230",
            brand_name="阿维塔",
            brand="阿维塔",
            year="2025",
            price="20.99万",
        )
        params = [
            ParamItem(category="基本信息", name="充电时间(小时)", value="快充0.17小时\n慢充13小时"),
            ParamItem(category="电池/充电", name="充电时间", value="快充0.17小时\n慢充13小时"),
        ]

        content = format_config_note(config, params)

        self.assertIn("快充0.17小时<br>慢充13小时", content)
        self.assertNotIn("快充0.17小时\n慢充13小时 |", content)
        self.assertNotIn("\n慢充13小时 |", content)

    def test_format_config_note_sanitizes_pipe_characters(self) -> None:
        config = CarConfig(
            car_id="2",
            car_name="测试版",
            series_name="测试车",
            series_id="2",
            brand_name="品牌",
            brand="品牌",
        )
        params = [ParamItem(category="基本|信息", name="A|B", value="X|Y")]

        content = format_config_note(config, params)

        self.assertIn("基本\\|信息", content)
        self.assertIn("A\\|B", content)
        self.assertIn("X\\|Y", content)

    def test_format_config_note_sanitizes_tags_with_spaces(self) -> None:
        config = CarConfig(
            car_id="251481",
            car_name="Elite 后驱增程版 39.05kWh",
            series_name="阿维塔 07",
            series_id="10033",
            brand_name="阿维塔",
            brand="阿维塔",
            year="2026",
            price="21.99万",
            level="SUV",
        )
        content = format_config_note(config, [])

        self.assertIn("  - 阿维塔07", content)
        self.assertNotIn("  - 阿维塔 07", content)

    def test_format_config_note_adds_fixed_links(self) -> None:
        config = CarConfig(
            car_id="251481",
            car_name="Elite 后驱增程版 39.05kWh",
            series_name="阿维塔 07",
            series_id="10033",
            brand_name="阿维塔",
            brand="阿维塔",
            year="2026",
            price="21.99万",
            level="SUV",
        )
        content = format_config_note(config, [])

        self.assertIn("https://www.dongchedi.com/auto/series/10033/model-251481", content)
        self.assertIn("https://www.dongchedi.com/auto/params-carIds-251481", content)
        self.assertIn("https://www.dongchedi.com/community/10033", content)
        self.assertIn("https://www.dongchedi.com/auto/series/score/10033-x-x-x-x-x", content)


    def test_format_series_overview_note_adds_fixed_links(self) -> None:
        config = CarConfig(
            car_id="251481",
            car_name="Elite 后驱增程版 39.05kWh",
            series_name="阿维塔 07",
            series_id="10033",
            brand_name="阿维塔",
            brand="阿维塔",
            year="2026",
            price="21.99万",
            level="SUV",
        )
        from lib.markdown import format_series_overview_note
        content = format_series_overview_note(config, ["2026款 Elite 后驱增程版 39.05kWh"], "2026-03")

        self.assertIn("https://www.dongchedi.com/auto/series/10033", content)
        self.assertIn("https://www.dongchedi.com/auto/params-carIds-x-10033", content)
        self.assertIn("https://www.dongchedi.com/community/10033", content)
        self.assertIn("https://www.dongchedi.com/auto/series/score/10033-x-x-x-x-x", content)



if __name__ == "__main__":
    unittest.main()
