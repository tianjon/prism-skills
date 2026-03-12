import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import sys

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR))

from scripts import import_to_obsidian as import_script


class ImportScriptTest(unittest.TestCase):
    def test_import_to_obsidian_imports_manifest_entries_and_copies_assets(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            mineru_root = root / "mineru"
            md_dir = mineru_root / "nested" / "child" / "auto"
            md_dir.mkdir(parents=True)

            md_path = md_dir / "child.md"
            md_path.write_text("before\n![](images/foo.jpg)\nafter\n", encoding="utf-8")
            assets_dir = md_dir / "images"
            assets_dir.mkdir()
            (assets_dir / "foo.jpg").write_bytes(b"foo")

            manifest_path = root / "manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "input_path": str(root / "src"),
                        "output_root": str(mineru_root),
                        "extensions": [".pdf"],
                        "entries": [
                            {
                                "source_file": "nested/child.pdf",
                                "source_abs_path": str(root / "src" / "nested" / "child.pdf"),
                                "relative_parent": "nested",
                                "output_root": str(mineru_root / "nested"),
                                "markdown_path": str(md_path),
                                "assets_dir": str(assets_dir),
                                "has_assets": True,
                                "target_note_rel_path": "nested/child/child.md",
                                "target_images_rel_path": "nested/child/images",
                            }
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            vault_root = root / "vault"
            vault_root.mkdir()

            def fake_write_obsidian_note(*, target_path: str, content: str, vault: str = "", chunk_size: int = 3000) -> None:
                note_path = vault_root / Path(target_path)
                note_path.parent.mkdir(parents=True, exist_ok=True)
                note_path.write_text(content, encoding="utf-8")

            with patch.object(import_script, "resolve_vault_path", return_value=vault_root), patch.object(
                import_script, "write_obsidian_note", side_effect=fake_write_obsidian_note
            ):
                rc = import_script.main(
                    [
                        "--manifest",
                        str(manifest_path),
                        "--target-root",
                        "Law/Import",
                    ]
                )

            self.assertEqual(rc, 0)
            note_path = vault_root / "Law" / "Import" / "nested" / "child" / "child.md"
            self.assertTrue(note_path.exists())
            self.assertIn("![[images/foo.jpg]]", note_path.read_text(encoding="utf-8"))
            self.assertTrue((note_path.parent / "images" / "foo.jpg").exists())

    def test_import_to_obsidian_fails_on_missing_referenced_asset(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            mineru_root = root / "mineru"
            md_dir = mineru_root / "nested" / "child" / "auto"
            md_dir.mkdir(parents=True)

            md_path = md_dir / "child.md"
            md_path.write_text("![](images/missing.jpg)\n", encoding="utf-8")
            assets_dir = md_dir / "images"
            assets_dir.mkdir()

            manifest_path = root / "manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "input_path": str(root / "src"),
                        "output_root": str(mineru_root),
                        "extensions": [".pdf"],
                        "entries": [
                            {
                                "source_file": "nested/child.pdf",
                                "source_abs_path": str(root / "src" / "nested" / "child.pdf"),
                                "relative_parent": "nested",
                                "output_root": str(mineru_root / "nested"),
                                "markdown_path": str(md_path),
                                "assets_dir": str(assets_dir),
                                "has_assets": True,
                                "target_note_rel_path": "nested/child/child.md",
                                "target_images_rel_path": "nested/child/images",
                            }
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            vault_root = root / "vault"
            vault_root.mkdir()

            def fake_write_obsidian_note(*, target_path: str, content: str, vault: str = "", chunk_size: int = 3000) -> None:
                note_path = vault_root / Path(target_path)
                note_path.parent.mkdir(parents=True, exist_ok=True)
                note_path.write_text(content, encoding="utf-8")

            with patch.object(import_script, "resolve_vault_path", return_value=vault_root), patch.object(
                import_script, "write_obsidian_note", side_effect=fake_write_obsidian_note
            ):
                with self.assertRaises(FileNotFoundError):
                    import_script.main(
                        [
                            "--manifest",
                            str(manifest_path),
                            "--target-root",
                            "Law/Import",
                        ]
                    )


if __name__ == "__main__":
    unittest.main()

