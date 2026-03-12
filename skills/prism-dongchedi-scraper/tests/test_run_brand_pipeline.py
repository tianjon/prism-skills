import json
import tempfile
import unittest
from pathlib import Path

from unittest.mock import MagicMock, patch

from scripts import run_brand_pipeline
from scripts.run_brand_pipeline import (
    _console_script_is_runnable,
    build_parser,
    create_run_dir,
    ensure_obsidian_available,
    trim_target_models,
)


class RunBrandPipelineTest(unittest.TestCase):
    def test_build_parser_accepts_brand_and_options(self) -> None:
        parser = build_parser()
        args = parser.parse_args([
            "--brand", "宝马",
            "--publish",
            "--vault", "Cars",
            "--limit-series", "3",
            "--limit-configs", "2",
            "--interactive",
        ])

        self.assertEqual(args.brand, "宝马")
        self.assertTrue(args.publish)
        self.assertEqual(args.vault, "Cars")
        self.assertEqual(args.limit_series, 3)
        self.assertEqual(args.limit_configs, 2)
        self.assertTrue(args.interactive)

    def test_build_parser_rejects_reserved_params_batch_option(self) -> None:
        parser = build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args(["--brand", "宝马", "--params-batch-size", "2"])

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

    def test_skip_store_does_not_require_obsidian(self) -> None:
        with patch('scripts.run_brand_pipeline.shutil.which', return_value=None):
            with self.assertRaisesRegex(RuntimeError, 'Obsidian CLI is not installed'):
                ensure_obsidian_available()

    def test_console_script_with_missing_shebang_interpreter_is_not_runnable(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            script_path = Path(tmpdir) / "browser-use"
            script_path.write_text(
                "#!/tmp/does-not-exist/python\nprint('hello')\n",
                encoding="utf-8",
            )
            script_path.chmod(0o755)

            self.assertFalse(_console_script_is_runnable(script_path))

    def test_ensure_uv_runtime_reinstalls_when_browser_use_entrypoint_is_broken(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir)
            bin_dir = skill_dir / ".venv" / "bin"
            bin_dir.mkdir(parents=True)

            python_bin = bin_dir / "python"
            python_bin.write_text("#!/bin/sh\n", encoding="utf-8")
            python_bin.chmod(0o755)

            browser_use_bin = bin_dir / "browser-use"
            browser_use_bin.write_text("#!/tmp/does-not-exist/python\n", encoding="utf-8")
            browser_use_bin.chmod(0o755)

            calls: list[list[str]] = []

            def fake_run(cmd, cwd=None, check=None, **kwargs):
                calls.append(cmd)
                return MagicMock(returncode=0, stdout="OK")

            with patch.object(run_brand_pipeline, "SKILL_DIR", skill_dir), \
                 patch("scripts.run_brand_pipeline.shutil.which", side_effect=lambda name: "/opt/homebrew/bin/uv" if name == "uv" else None), \
                 patch("scripts.run_brand_pipeline._python_has_modules", return_value=True), \
                 patch("scripts.run_brand_pipeline.subprocess.run", side_effect=fake_run):
                python_exec, browser_use_exec = run_brand_pipeline._ensure_uv_runtime()

            self.assertEqual(python_exec, str(python_bin))
            self.assertEqual(browser_use_exec, str(browser_use_bin))
            self.assertEqual(
                calls,
                [
                    ["/opt/homebrew/bin/uv", "pip", "install", "--reinstall", "--python", str(python_bin), "browser-use", "pydantic>=2.0"],
                    [str(browser_use_bin), "install"],
                ],
            )

    def test_main_skips_interactive_resolution_by_default(self) -> None:
        commands: list[list[str]] = []

        def fake_run(cmd, env):
            commands.append(cmd)

        with patch("scripts.run_brand_pipeline.ensure_python_available"), \
             patch("scripts.run_brand_pipeline.ensure_obsidian_available") as ensure_obsidian, \
             patch("scripts.run_brand_pipeline.resolve_options_interactively") as resolve_interactive, \
             patch("scripts.run_brand_pipeline.resolve_runtime", return_value=("/tmp/python", "/tmp/browser-use")), \
             patch("scripts.run_brand_pipeline.create_run_dir", return_value=Path("/tmp/dongchedi-run")), \
             patch("scripts.run_brand_pipeline.assert_non_empty_json_list", return_value=[{"ok": True}]), \
             patch("scripts.run_brand_pipeline._run", side_effect=fake_run), \
             patch("scripts.run_brand_pipeline._run_configs_in_batches"), \
             patch("scripts.run_brand_pipeline.subprocess.run", return_value=MagicMock(returncode=0)):
            exit_code = run_brand_pipeline.main(["--brand", "BMW", "--skip-params"])

        self.assertEqual(exit_code, 0)
        ensure_obsidian.assert_not_called()
        resolve_interactive.assert_not_called()
        self.assertFalse(any(cmd[1:3] == ["scripts/diff.py"] for cmd in commands))
        self.assertFalse(any(cmd[1:3] == ["scripts/store.py"] for cmd in commands))

    def test_main_uses_interactive_resolution_when_requested(self) -> None:
        with patch("scripts.run_brand_pipeline.ensure_python_available"), \
             patch("scripts.run_brand_pipeline.resolve_options_interactively", side_effect=lambda args, argv: args) as resolve_interactive, \
             patch("scripts.run_brand_pipeline.resolve_runtime", return_value=("/tmp/python", "/tmp/browser-use")), \
             patch("scripts.run_brand_pipeline.create_run_dir", return_value=Path("/tmp/dongchedi-run")), \
             patch("scripts.run_brand_pipeline.assert_non_empty_json_list", return_value=[{"ok": True}]), \
             patch("scripts.run_brand_pipeline._run"), \
             patch("scripts.run_brand_pipeline._run_configs_in_batches"), \
             patch("scripts.run_brand_pipeline.subprocess.run", return_value=MagicMock(returncode=0)):
            exit_code = run_brand_pipeline.main(["--brand", "BMW", "--skip-store", "--skip-params", "--interactive"])

        self.assertEqual(exit_code, 0)
        resolve_interactive.assert_called_once()

    def test_main_publish_runs_diff_before_store(self) -> None:
        commands: list[list[str]] = []

        def fake_run(cmd, env):
            commands.append(cmd)

        with patch("scripts.run_brand_pipeline.ensure_python_available"), \
             patch("scripts.run_brand_pipeline.ensure_obsidian_available") as ensure_obsidian, \
             patch("scripts.run_brand_pipeline.resolve_runtime", return_value=("/tmp/python", "/tmp/browser-use")), \
             patch("scripts.run_brand_pipeline.create_run_dir", return_value=Path("/tmp/dongchedi-run")), \
             patch("scripts.run_brand_pipeline.assert_non_empty_json_list", return_value=[{"ok": True}]), \
             patch("scripts.run_brand_pipeline._run", side_effect=fake_run), \
             patch("scripts.run_brand_pipeline._run_configs_in_batches"), \
             patch("scripts.run_brand_pipeline.subprocess.run", return_value=MagicMock(returncode=0)):
            exit_code = run_brand_pipeline.main(["--brand", "BMW", "--publish", "--vault", "Cars"])

        self.assertEqual(exit_code, 0)
        ensure_obsidian.assert_called_once()
        self.assertIn(["/tmp/python", "scripts/diff.py", "--vault", "Cars"], commands)
        self.assertIn(["/tmp/python", "scripts/store.py", "--changelog", "--vault", "Cars"], commands)
        self.assertLess(
            commands.index(["/tmp/python", "scripts/diff.py", "--vault", "Cars"]),
            commands.index(["/tmp/python", "scripts/store.py", "--changelog", "--vault", "Cars"]),
        )

    def test_main_publish_with_limit_configs_skips_discontinued_detection(self) -> None:
        commands: list[list[str]] = []

        def fake_run(cmd, env):
            commands.append(cmd)

        with patch("scripts.run_brand_pipeline.ensure_python_available"), \
             patch("scripts.run_brand_pipeline.ensure_obsidian_available"), \
             patch("scripts.run_brand_pipeline.resolve_runtime", return_value=("/tmp/python", "/tmp/browser-use")), \
             patch("scripts.run_brand_pipeline.create_run_dir", return_value=Path("/tmp/dongchedi-run")), \
             patch("scripts.run_brand_pipeline.assert_non_empty_json_list", return_value=[{"ok": True}]), \
             patch("scripts.run_brand_pipeline.trim_configs"), \
             patch("scripts.run_brand_pipeline._run", side_effect=fake_run), \
             patch("scripts.run_brand_pipeline._run_configs_in_batches"), \
             patch("scripts.run_brand_pipeline.subprocess.run", return_value=MagicMock(returncode=0)):
            exit_code = run_brand_pipeline.main(["--brand", "BMW", "--publish", "--limit-configs", "2"])

        self.assertEqual(exit_code, 0)
        self.assertIn(["/tmp/python", "scripts/diff.py", "--skip-discontinued"], commands)

    def test_main_rejects_publish_without_params(self) -> None:
        with patch("scripts.run_brand_pipeline.ensure_python_available"), \
             patch("scripts.run_brand_pipeline.ensure_obsidian_available") as ensure_obsidian, \
             patch("scripts.run_brand_pipeline.resolve_runtime") as resolve_runtime:
            with self.assertRaisesRegex(RuntimeError, "Publishing requires parameter extraction"):
                run_brand_pipeline.main(["--brand", "BMW", "--publish", "--skip-params"])

        ensure_obsidian.assert_not_called()
        resolve_runtime.assert_not_called()



if __name__ == "__main__":
    unittest.main()
