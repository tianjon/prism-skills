import unittest

from lib.types import CarConfig
from scripts.store import build_config_note_targets


class StoreStructureTest(unittest.TestCase):
    def test_build_config_note_targets_returns_current_and_snapshot_paths(self) -> None:
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

        targets = build_config_note_targets(config, update_month="2026-03")

        self.assertEqual(
            targets["current_path"],
            "汽车/品牌库/比亚迪/秦L DM/当前款型/2025款 DM-i 120KM领先型.md",
        )
        self.assertEqual(
            targets["snapshot_path"],
            "汽车/品牌库/比亚迪/秦L DM/更新记录/2026-03/2025款 DM-i 120KM领先型.md",
        )
        self.assertEqual(
            targets["overview_path"],
            "汽车/品牌库/比亚迪/秦L DM/00-车型总览.md",
        )


if __name__ == "__main__":
    unittest.main()
