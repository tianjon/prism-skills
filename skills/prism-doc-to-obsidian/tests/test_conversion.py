import tempfile
import unittest
from pathlib import Path

import sys

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR))

from lib.conversion import (
    build_conversion_batches,
    build_manifest_entries,
    discover_supported_inputs,
)


class ConversionDiscoveryTest(unittest.TestCase):
    def test_discover_supported_inputs_recurses(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir).resolve()
            (root / "top.pdf").write_text("pdf", encoding="utf-8")
            (root / "ignore.txt").write_text("txt", encoding="utf-8")
            nested = root / "nested"
            nested.mkdir()
            (nested / "child.PDF").write_text("pdf", encoding="utf-8")
            deep = nested / "deep"
            deep.mkdir()
            (deep / "page.png").write_text("png", encoding="utf-8")

            files = discover_supported_inputs(root)

            self.assertEqual(
                [path.relative_to(root).as_posix() for path in files],
                [
                    "nested/child.PDF",
                    "nested/deep/page.png",
                    "top.pdf",
                ],
            )

    def test_build_conversion_batches_groups_by_direct_parent(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir).resolve()
            (root / "top.pdf").write_text("pdf", encoding="utf-8")
            nested = root / "nested"
            nested.mkdir()
            (nested / "child-a.pdf").write_text("pdf", encoding="utf-8")
            (nested / "child-b.pdf").write_text("pdf", encoding="utf-8")
            deep = nested / "deep"
            deep.mkdir()
            (deep / "deep-child.pdf").write_text("pdf", encoding="utf-8")

            files = discover_supported_inputs(root)
            batches = build_conversion_batches(root, files)

            self.assertEqual(
                [(batch.relative_parent.as_posix(), [item.name for item in batch.files]) for batch in batches],
                [
                    (".", ["top.pdf"]),
                    ("nested", ["child-a.pdf", "child-b.pdf"]),
                    ("nested/deep", ["deep-child.pdf"]),
                ],
            )

    def test_build_manifest_entries_tracks_relative_source_and_assets(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir).resolve()
            output_root = root / "out"
            source_file = root / "nested" / "child.pdf"
            source_file.parent.mkdir(parents=True)
            source_file.write_text("pdf", encoding="utf-8")

            generated_dir = output_root / "nested" / "child" / "auto"
            generated_dir.mkdir(parents=True)
            markdown_path = generated_dir / "child.md"
            markdown_path.write_text("# child", encoding="utf-8")
            images_dir = generated_dir / "images"
            images_dir.mkdir()

            entries = build_manifest_entries(root, output_root, [source_file])

            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0].source_file, "nested/child.pdf")
            self.assertEqual(entries[0].relative_parent, "nested")
            self.assertEqual(entries[0].markdown_path, str(markdown_path))
            self.assertEqual(entries[0].assets_dir, str(images_dir))
            self.assertTrue(entries[0].has_assets)
            self.assertEqual(entries[0].target_note_rel_path, "nested/child/child.md")
            self.assertEqual(entries[0].target_images_rel_path, "nested/child/images")

    def test_build_manifest_entries_avoids_collisions_for_same_named_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir).resolve()
            output_root = root / "out"

            # Two different inputs with the same stem under different parents.
            a_dir = root / "a"
            b_dir = root / "b"
            a_dir.mkdir()
            b_dir.mkdir()
            a_pdf = a_dir / "same.pdf"
            b_pdf = b_dir / "same.pdf"
            a_pdf.write_text("pdf-a", encoding="utf-8")
            b_pdf.write_text("pdf-b", encoding="utf-8")

            # Simulate MinerU outputs in the mirrored output tree.
            a_md_dir = output_root / "a" / "same" / "auto"
            b_md_dir = output_root / "b" / "same" / "auto"
            a_md_dir.mkdir(parents=True)
            b_md_dir.mkdir(parents=True)
            (a_md_dir / "same.md").write_text("# a", encoding="utf-8")
            (b_md_dir / "same.md").write_text("# b", encoding="utf-8")

            entries = build_manifest_entries(root, output_root, [a_pdf, b_pdf])

            self.assertEqual(len(entries), 2)
            by_source = {entry.source_file: entry for entry in entries}
            self.assertEqual(by_source["a/same.pdf"].relative_parent, "a")
            self.assertEqual(by_source["b/same.pdf"].relative_parent, "b")
            self.assertNotEqual(by_source["a/same.pdf"].markdown_path, by_source["b/same.pdf"].markdown_path)


if __name__ == "__main__":
    unittest.main()
