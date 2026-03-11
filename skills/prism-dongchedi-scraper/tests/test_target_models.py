import unittest

from lib.dongchedi import select_target_models
from lib.types import CarModel


class TargetModelSelectionTest(unittest.TestCase):
    def test_select_target_models_keeps_all_when_no_filter(self) -> None:
        models = [
            CarModel(name="比亚迪 汉", series_id="1", price_range="20-30万", level="中大型车"),
            CarModel(name="比亚迪 唐", series_id="2", price_range="22-32万", level="SUV"),
        ]

        selected = select_target_models(models)

        self.assertEqual([model.series_id for model in selected], ["1", "2"])

    def test_select_target_models_filters_by_series_ids_in_order(self) -> None:
        models = [
            CarModel(name="比亚迪 汉", series_id="1", price_range="20-30万", level="中大型车"),
            CarModel(name="比亚迪 唐", series_id="2", price_range="22-32万", level="SUV"),
            CarModel(name="比亚迪 宋", series_id="3", price_range="12-18万", level="SUV"),
        ]

        selected = select_target_models(models, ["2", "1"])

        self.assertEqual([model.series_id for model in selected], ["2", "1"])
        self.assertEqual([model.name for model in selected], ["比亚迪 唐", "比亚迪 汉"])

    def test_select_target_models_rejects_unknown_series_ids(self) -> None:
        models = [CarModel(name="比亚迪 汉", series_id="1")]

        with self.assertRaisesRegex(ValueError, "Unknown series_id"):
            select_target_models(models, ["9999"])


if __name__ == "__main__":
    unittest.main()
