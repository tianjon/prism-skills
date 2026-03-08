import json
import tempfile
import unittest
from pathlib import Path

from scripts.run_brand_pipeline import assert_non_empty_json_list


class PipelineValidationTest(unittest.TestCase):
    def test_assert_non_empty_json_list_rejects_empty_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "empty.json"
            path.write_text("[]", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "empty search results"):
                assert_non_empty_json_list(path, "empty search results")

    def test_assert_non_empty_json_list_accepts_non_empty_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "ok.json"
            path.write_text(json.dumps([{"a": 1}], ensure_ascii=False), encoding="utf-8")
            payload = assert_non_empty_json_list(path, "should not fail")
            self.assertEqual(len(payload), 1)


if __name__ == "__main__":
    unittest.main()
