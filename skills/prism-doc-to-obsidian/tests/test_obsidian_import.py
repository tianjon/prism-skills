import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import sys

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR))

from lib.obsidian_import import (
    copy_all_assets,
    copy_referenced_assets,
    plan_import_targets,
    rewrite_markdown_image_embeds,
    write_obsidian_note,
    write_obsidian_note_iter,
)


class MarkdownRewriteTest(unittest.TestCase):
    def test_rewrite_markdown_image_embeds_converts_relative_image_links(self) -> None:
        content = "\n".join(
            [
                "# Title",
                "",
                "before",
                "![](images/foo.jpg)",
                "middle",
                "![](images/bar.png)",
                "",
            ]
        )

        rewritten, image_names = rewrite_markdown_image_embeds(content)

        self.assertEqual(image_names, ["foo.jpg", "bar.png"])
        self.assertIn("![[images/foo.jpg]]", rewritten)
        self.assertIn("![[images/bar.png]]", rewritten)
        self.assertNotIn("![](images/foo.jpg)", rewritten)

    def test_rewrite_markdown_image_embeds_leaves_non_image_markdown_unchanged(self) -> None:
        content = "\n".join(
            [
                "# Title",
                "",
                "no images here",
                "",
            ]
        )

        rewritten, image_names = rewrite_markdown_image_embeds(content)

        self.assertEqual(image_names, [])
        self.assertEqual(rewritten, content)


class AssetCopyTest(unittest.TestCase):
    def test_copy_referenced_assets_copies_only_requested_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            src = root / "src"
            src.mkdir()
            (src / "foo.jpg").write_bytes(b"foo")
            (src / "bar.png").write_bytes(b"bar")
            (src / "unused.jpg").write_bytes(b"unused")
            dest = root / "dest"

            copied = copy_referenced_assets(src, ["foo.jpg", "bar.png"], dest)

            self.assertEqual([path.name for path in copied], ["foo.jpg", "bar.png"])
            self.assertTrue((dest / "foo.jpg").exists())
            self.assertTrue((dest / "bar.png").exists())
            self.assertFalse((dest / "unused.jpg").exists())

    def test_copy_referenced_assets_fails_when_a_referenced_asset_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            src = root / "src"
            src.mkdir()
            (src / "foo.jpg").write_bytes(b"foo")
            dest = root / "dest"

            with self.assertRaises(FileNotFoundError):
                copy_referenced_assets(src, ["foo.jpg", "bar.png"], dest)

    def test_copy_all_assets_copies_everything_under_assets_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            src = root / "src"
            (src / "sub").mkdir(parents=True)
            (src / "foo.jpg").write_bytes(b"foo")
            (src / "sub" / "bar.png").write_bytes(b"bar")
            dest = root / "dest"

            copied = copy_all_assets(src, dest)

            self.assertEqual(sorted([path.relative_to(dest).as_posix() for path in copied]), ["foo.jpg", "sub/bar.png"])
            self.assertTrue((dest / "foo.jpg").exists())
            self.assertTrue((dest / "sub" / "bar.png").exists())


class ImportTargetPlanTest(unittest.TestCase):
    def test_plan_import_targets_places_notes_under_target_root_with_images_dir(self) -> None:
        entries = [
            {"source_file": "nested/child.pdf"},
            {"source_file": "top.pdf"},
        ]

        planned = plan_import_targets(entries, target_root="Law/Import")

        self.assertEqual(planned["nested/child.pdf"].target_note_path, "Law/Import/nested/child/child.md")
        self.assertEqual(planned["nested/child.pdf"].target_images_dir, "Law/Import/nested/child/images")
        self.assertEqual(planned["top.pdf"].target_note_path, "Law/Import/top/top.md")
        self.assertEqual(planned["top.pdf"].target_images_dir, "Law/Import/top/images")

    def test_plan_import_targets_disambiguates_same_stem_under_same_parent(self) -> None:
        entries = [
            {"source_file": "nested/same.pdf"},
            {"source_file": "nested/same.png"},
        ]

        planned = plan_import_targets(entries, target_root="Law/Import")

        self.assertEqual(planned["nested/same.pdf"].target_note_path, "Law/Import/nested/same__pdf/same.md")
        self.assertEqual(planned["nested/same.png"].target_note_path, "Law/Import/nested/same__png/same.md")


class ObsidianWriteTest(unittest.TestCase):
    def test_write_obsidian_note_uses_create_then_chunked_append(self) -> None:
        calls: list[list[str]] = []
        content = "x" * 6500

        def fake_run(cmd, capture_output=True, text=True, timeout=60):
            calls.append(cmd)

            class Result:
                returncode = 0
                stdout = content if cmd[1] == "read" else ""
                stderr = ""

            return Result()

        with patch("lib.obsidian_import.subprocess.run", side_effect=fake_run):
            write_obsidian_note(
                target_path="Law/Test/long.md",
                content=content,
                vault="obs",
                chunk_size=3000,
            )

        self.assertEqual(calls[0][0:3], ["obsidian", "create", "vault=obs"])
        self.assertIn("path=Law/Test/long.md", calls[0])
        self.assertIn("overwrite", calls[0])
        self.assertIn("silent", calls[0])
        self.assertEqual(calls[1][0:3], ["obsidian", "append", "vault=obs"])
        self.assertIn("inline", calls[1])
        self.assertEqual(calls[2][0:3], ["obsidian", "append", "vault=obs"])
        self.assertEqual(calls[3][0:3], ["obsidian", "read", "vault=obs"])
        self.assertEqual(len(calls), 4)

    def test_write_obsidian_note_fails_when_readback_mismatches(self) -> None:
        calls: list[list[str]] = []
        content = "x" * 10

        def fake_run(cmd, capture_output=True, text=True, timeout=60):
            calls.append(cmd)

            class Result:
                returncode = 0
                stdout = "DIFF" if cmd[1] == "read" else ""
                stderr = ""

            return Result()

        with patch("lib.obsidian_import.subprocess.run", side_effect=fake_run):
            with self.assertRaises(RuntimeError):
                write_obsidian_note(
                    target_path="Law/Test/mismatch.md",
                    content=content,
                    vault="obs",
                    chunk_size=3000,
                )


class ObsidianWriteIterTest(unittest.TestCase):
    def test_write_obsidian_note_iter_preserves_literal_backslash_sequences(self) -> None:
        """Regression test: Obsidian CLI interprets literal `\\n` and `\\t` sequences.

        The streaming writer must preserve content such as LaTeX commands (e.g. `\\text`)
        without accidentally turning them into real newlines/tabs.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_root = Path(tmpdir)
            target_path = "Law/Test/escapes.md"
            content = (
                "Line1 literal \\\\n and literal \\\\t sequences.\n"
                "LaTeX: \\\\nrightarrow and \\\\text{abc}.\n"
                "Tab->\t<-end.\n"
                "Space-before-newline: X \n"
                "Done."
            )

            calls: list[list[str]] = []

            def fake_run(cmd, capture_output=True, text=True, timeout=60):
                calls.append(cmd)

                command = cmd[1]
                path_arg = next((item for item in cmd if item.startswith("path=")), "")
                content_arg = next((item for item in cmd if item.startswith("content=")), "")
                rel_path = path_arg.split("=", 1)[1] if path_arg else ""
                raw = content_arg.split("=", 1)[1] if content_arg else ""

                # Mimic the Obsidian CLI's behavior: interpret `\n` and `\t` sequences
                # inside each content= argument, then trim trailing whitespace.
                decoded = raw.replace("\\n", "\n").replace("\\t", "\t").rstrip(" \t\n")

                file_path = vault_root / rel_path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                if command == "create":
                    file_path.write_text(decoded, encoding="utf-8")
                elif command == "append":
                    with file_path.open("a", encoding="utf-8") as handle:
                        handle.write(decoded)

                class Result:
                    returncode = 0
                    stdout = ""
                    stderr = ""

                return Result()

            with patch("lib.obsidian_import.subprocess.run", side_effect=fake_run):
                write_obsidian_note_iter(
                    target_path=target_path,
                    content_parts=[content],
                    chunk_size=17,  # force chunking boundaries around backslashes/whitespace
                    vault_root=vault_root,
                )

            written = (vault_root / target_path).read_text(encoding="utf-8")
            self.assertEqual(written, content)
            self.assertIn("\\nrightarrow", written)
            self.assertIn("\\text{abc}", written)
            self.assertIn("Tab->\t<-end.", written)
            self.assertIn("X \nDone.", written)
            self.assertTrue(any(cmd[1] == "create" for cmd in calls))
            self.assertTrue(any(cmd[1] == "append" for cmd in calls))


if __name__ == "__main__":
    unittest.main()
