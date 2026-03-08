import unittest

from lib.markdown import (
    config_current_note_name,
    config_current_note_path,
    config_snapshot_note_path,
    series_overview_note_path,
)
from lib.types import CarConfig


class ObsidianPathStructureTest(unittest.TestCase):
    def setUp(self) -> None:
        self.config = CarConfig(
            car_id="123",
            car_name="2025款 DM-i 120KM领先型",
            year="2025",
            series_name="秦L DM",
            series_id="9796",
            brand_name="比亚迪",
            brand="比亚迪",
            price="8.98万",
        )

    def test_current_note_path_uses_brand_series_and_trim(self) -> None:
        path = config_current_note_path(self.config)
        self.assertEqual(
            path,
            "汽车/品牌库/比亚迪/秦L DM/当前款型/2025款 DM-i 120KM领先型.md",
        )

    def test_snapshot_note_path_uses_brand_series_month_and_trim(self) -> None:
        path = config_snapshot_note_path(self.config, "2026-03")
        self.assertEqual(
            path,
            "汽车/品牌库/比亚迪/秦L DM/更新记录/2026-03/2025款 DM-i 120KM领先型.md",
        )

    def test_series_overview_note_path_uses_brand_and_series(self) -> None:
        path = series_overview_note_path(self.config)
        self.assertEqual(path, "汽车/品牌库/比亚迪/秦L DM/00-车型总览.md")


    def test_current_note_name_prepends_year_when_missing(self) -> None:
        config = CarConfig(
            car_id="321",
            car_name="Elite 后驱增程版 39.05kWh",
            year="2026",
            series_name="阿维塔 07",
            series_id="10033",
            brand_name="阿维塔",
            brand="阿维塔",
            price="21.99万",
        )
        self.assertEqual(config_current_note_name(config), "2026款 Elite 后驱增程版 39.05kWh")

    def test_current_note_name_matches_trim_name(self) -> None:
        self.assertEqual(config_current_note_name(self.config), "2025款 DM-i 120KM领先型")


if __name__ == "__main__":
    unittest.main()
