import json
import tempfile
import unittest
from pathlib import Path

from scripts.run_brand_pipeline import build_parser, create_run_dir, trim_target_models


class RunBrandPipelineTest(unittest.TestCase):
    def test_build_parser_accepts_brand_and_options(self) -> None:
        parser = build_parser()
        args = parser.parse_args([
            "--brand", "宝马",
            "--vault", "Cars",
            "--limit-series", "3",
            "--limit-configs", "2",
            "--skip-store",
        ])

        self.assertEqual(args.brand, "宝马")
        self.assertEqual(args.vault, "Cars")
        self.assertEqual(args.limit_series, 3)
        self.assertEqual(args.limit_configs, 2)
        self.assertTrue(args.skip_store)

    def test_create_run_dir_uses_brand_slug(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = create_run_dir(Path(tmpdir), "宝马")
            self.assertTrue(run_dir.exists())
            self.assertIn("宝马", run_dir.name)

    def test_trim_target_models_keeps_first_n(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target_path = Path(tmpdir) / "target-models.json"
            target_path.write_text(
                json.dumps([
                    {"name": "宝马3系", "series_id": "145", "price_range": "", "level": "轿车", "energy_type": ""},
                    {"name": "宝马5系", "series_id": "146", "price_range": "", "level": "轿车", "energy_type": ""},
                    {"name": "宝马X5", "series_id": "5273", "price_range": "", "level": "SUV", "energy_type": ""},
                ], ensure_ascii=False),
                encoding="utf-8",
            )

            trim_target_models(target_path, limit=2)

            payload = json.loads(target_path.read_text("utf-8"))
            self.assertEqual(len(payload), 2)
            self.assertEqual([item["series_id"] for item in payload], ["145", "146"])


if __name__ == "__main__":
    unittest.main()
