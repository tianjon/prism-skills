import unittest

from lib.dongchedi import build_series_list_entries
from lib.types import CarModel


class SeriesListBuildTest(unittest.TestCase):
    def test_build_series_list_entries_targets_first_then_unique_competitors(self) -> None:
        targets = [
            CarModel(name="腾势D9 DM", series_id="5843", level="MPV"),
            CarModel(name="腾势N9 DM", series_id="24726", level="SUV"),
        ]
        competitors = {
            "腾势D9 DM": {
                "target": targets[0].model_dump(),
                "competitors": {
                    "A": [],
                    "B": [],
                    "C": [
                        {"name": "岚图梦想家 PHEV", "series_id": "5924", "level": "MPV", "price_range": ""},
                        {"name": "ZEEKR 009", "series_id": "5878", "level": "MPV", "price_range": ""},
                    ],
                },
            },
            "腾势N9 DM": {
                "target": targets[1].model_dump(),
                "competitors": {
                    "A": [],
                    "B": [],
                    "C": [
                        {"name": "ZEEKR 009", "series_id": "5878", "level": "MPV", "price_range": ""},
                        {"name": "理想L9", "series_id": "5227", "level": "SUV", "price_range": ""},
                    ],
                },
            },
        }

        entries = build_series_list_entries(targets, competitors)

        self.assertEqual([entry["series_id"] for entry in entries], ["5843", "24726", "5924", "5878", "5227"])
        self.assertEqual(entries[0]["is_target"], True)
        self.assertEqual(entries[2]["is_target"], False)


if __name__ == "__main__":
    unittest.main()
