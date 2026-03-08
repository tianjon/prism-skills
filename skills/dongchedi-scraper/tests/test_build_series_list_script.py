import json
import os
import tempfile
import unittest
from pathlib import Path


class BuildSeriesListScriptTest(unittest.TestCase):
    def test_build_series_list_falls_back_to_targets_only_when_competitors_missing(self) -> None:
        skill_dir = Path(__file__).resolve().parent.parent
        script_path = skill_dir / "scripts" / "build_series_list.py"

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / "target-models.json").write_text(
                json.dumps([
                    {
                        "name": "宝马3系",
                        "series_id": "145",
                        "price_range": "22.66-31.99万",
                        "level": "轿车",
                        "energy_type": "",
                    }
                ], ensure_ascii=False),
                encoding="utf-8",
            )

            globals_dict = {
                "__name__": "__main__",
                "__file__": str(script_path),
            }

            previous_cwd = Path.cwd()
            previous_tmp = os.environ.get("DONGCHEDI_TMP_DIR")
            try:
                os.chdir(skill_dir)
                os.environ["DONGCHEDI_TMP_DIR"] = str(tmp_path)
                exec(compile(script_path.read_text("utf-8"), str(script_path), "exec"), globals_dict)
            finally:
                os.chdir(previous_cwd)
                if previous_tmp is None:
                    os.environ.pop("DONGCHEDI_TMP_DIR", None)
                else:
                    os.environ["DONGCHEDI_TMP_DIR"] = previous_tmp

            payload = json.loads((tmp_path / "series-list.json").read_text("utf-8"))
            self.assertEqual(len(payload), 1)
            self.assertEqual(payload[0]["series_id"], "145")
            self.assertTrue(payload[0]["is_target"])


if __name__ == "__main__":
    unittest.main()
