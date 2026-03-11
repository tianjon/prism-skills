import json
import tempfile
import unittest
from pathlib import Path

from scripts.run_brand_pipeline import build_param_batches, merge_param_batch_outputs


class ParamsBatchingTest(unittest.TestCase):
    def test_build_param_batches_splits_count(self) -> None:
        self.assertEqual(build_param_batches(total=13, batch_size=5), [(0, 5), (5, 5), (10, 3)])

    def test_merge_param_batch_outputs_concatenates_in_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            first = tmp_path / "params-batch-0.json"
            second = tmp_path / "params-batch-1.json"
            out = tmp_path / "all-configs-with-params.json"
            first.write_text(json.dumps([{"car_id": "1"}, {"car_id": "2"}], ensure_ascii=False), encoding="utf-8")
            second.write_text(json.dumps([{"car_id": "3"}], ensure_ascii=False), encoding="utf-8")

            merge_param_batch_outputs([first, second], out)

            payload = json.loads(out.read_text("utf-8"))
            self.assertEqual([item["car_id"] for item in payload], ["1", "2", "3"])


if __name__ == "__main__":
    unittest.main()
