import unittest

from lib.markdown import competitor_index_note_path, monthly_changelog_note_path
from lib.types import CarConfig, CarModel


class PublishPathStructureTest(unittest.TestCase):
    def test_competitor_index_note_path_uses_brand_series_month(self) -> None:
        target = CarModel(
            name="秦L DM",
            series_id="9796",
            price_range="8.98-14.38万",
            level="轿车",
            energy_type="插电式混合动力",
        )
        path = competitor_index_note_path(target, brand="比亚迪", update_month="2026-03")
        self.assertEqual(
            path,
            "汽车/品牌库/比亚迪/秦L DM/更新记录/2026-03/竞品分析.md",
        )

    def test_monthly_changelog_note_path_uses_brand_series_month(self) -> None:
        config = CarConfig(
            car_id="123",
            car_name="2025款 DM-i 120KM领先型",
            year="2025",
            series_name="秦L DM",
            series_id="9796",
            brand_name="比亚迪",
            brand="比亚迪",
            price="8.98万",
        )
        path = monthly_changelog_note_path(config, "2026-03")
        self.assertEqual(
            path,
            "汽车/品牌库/比亚迪/秦L DM/更新记录/2026-03/00-本月更新摘要.md",
        )


if __name__ == "__main__":
    unittest.main()
