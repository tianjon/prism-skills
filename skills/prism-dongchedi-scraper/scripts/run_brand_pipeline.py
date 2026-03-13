"""Run the dongchedi brand pipeline end-to-end.

The default mode is non-interactive so Codex can drive the pipeline with
explicit flags. If the required Python dependencies are missing from the active
environment, the script provisions a local `uv` runtime automatically. Prompted
confirmation is still available via `--interactive` when a human wants the
script to ask for missing options.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent.parent
TMP_ROOT = SKILL_DIR / "tmp" / "runs"
REQUIRED_MODULES = ("browser_use", "pydantic")


def _venv_bin_dir(venv_dir: Path) -> Path:
    return venv_dir / ("Scripts" if os.name == "nt" else "bin")


def _venv_executable(venv_dir: Path, name: str) -> Path:
    suffix = ".exe" if os.name == "nt" else ""
    return _venv_bin_dir(venv_dir) / f"{name}{suffix}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the dongchedi brand pipeline")
    parser.add_argument("--brand", required=True, help="Brand name, for example BMW")
    parser.add_argument("--vault", default="", help="Optional Obsidian vault name")
    parser.add_argument("--limit-series", type=int, default=0, help="Process only the first N series, 0 means all")
    parser.add_argument("--limit-configs", type=int, default=0, help="Process only the first N configs, 0 means all")
    parser.add_argument("--configs-batch-size", type=int, default=5, help="Batch size for config extraction")
    parser.add_argument("--with-competitors", action="store_true", help="Extract competitors and publish competitor notes")
    parser.add_argument("--history-window-years", type=int, default=3, help="Keep only the most recent N model years for historical models")
    parser.add_argument("--keep-session", action="store_true", help="Keep browser-use sessions open for manual inspection")
    parser.add_argument("--interactive", action="store_true", help="Prompt for omitted options instead of using CLI defaults")
    parser.add_argument("--tmp-root", default=str(TMP_ROOT), help="Root directory for run artifacts")
    return parser



def _slugify(value: str) -> str:
    cleaned = re.sub(r"[\\/:*?\"<>|]+", "-", value.strip())
    cleaned = re.sub(r"\s+", "-", cleaned)
    return cleaned or "brand"



def create_run_dir(base_dir: Path, brand: str) -> Path:
    base_dir.mkdir(parents=True, exist_ok=True)
    run_id = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{_slugify(brand)}"
    run_dir = base_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir



def trim_configs(configs_path: Path, limit: int) -> None:
    if limit <= 0:
        return
    payload = json.loads(configs_path.read_text("utf-8"))
    payload = payload[:limit]
    configs_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")



def trim_target_models(target_path: Path, limit: int) -> None:
    if limit <= 0:
        return
    payload = json.loads(target_path.read_text("utf-8"))
    payload = payload[:limit]
    target_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")



def build_param_batches(total: int, batch_size: int) -> list[tuple[int, int]]:
    if total <= 0:
        return []
    if batch_size <= 0:
        return [(0, total)]
    batches = []
    for offset in range(0, total, batch_size):
        size = min(batch_size, total - offset)
        batches.append((offset, size))
    return batches



def merge_json_list_outputs(batch_paths: list[Path], output_path: Path) -> None:
    merged = []
    for batch_path in batch_paths:
        if batch_path.exists():
            merged.extend(json.loads(batch_path.read_text("utf-8")))
    output_path.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")



def merge_param_batch_outputs(batch_paths: list[Path], output_path: Path) -> None:
    merge_json_list_outputs(batch_paths, output_path)



def assert_non_empty_json_list(path: Path, message: str) -> list[dict]:
    if not path.exists():
        raise RuntimeError(f"{message}: missing {path}")
    payload = json.loads(path.read_text("utf-8"))
    if not isinstance(payload, list) or not payload:
        raise RuntimeError(message)
    return payload



def _python_has_modules(python_executable: str) -> bool:
    code = "import browser_use, pydantic; print('OK')"
    result = subprocess.run([python_executable, "-c", code], capture_output=True, text=True)
    return result.returncode == 0 and "OK" in result.stdout


def _console_script_is_runnable(script_path: Path) -> bool:
    if not script_path.exists() or not os.access(script_path, os.X_OK):
        return False

    try:
        first_line = script_path.read_text("utf-8").splitlines()[0]
    except (IndexError, OSError, UnicodeDecodeError):
        return True

    if not first_line.startswith("#!"):
        return True

    parts = first_line[2:].strip().split()
    if not parts:
        return True

    interpreter = parts[0]
    if interpreter.endswith("/env") and len(parts) > 1:
        return shutil.which(parts[1]) is not None

    return Path(interpreter).exists()



def _select_global_python() -> str | None:
    candidates = []
    for item in (sys.executable, shutil.which("python3"), shutil.which("python")):
        if item and item not in candidates:
            candidates.append(item)
    for candidate in candidates:
        if _python_has_modules(candidate):
            return candidate
    return None



def _ensure_uv_runtime() -> tuple[str, str]:
    uv = shutil.which("uv")
    if not uv:
        raise RuntimeError(
            "Python dependencies are missing from the global environment and `uv` is not installed. "
            "Please install Python 3.11+ and uv first."
        )
    venv_dir = SKILL_DIR / ".venv"
    python_bin = _venv_executable(venv_dir, "python")
    browser_use_bin = _venv_executable(venv_dir, "browser-use")
    if not python_bin.exists():
        subprocess.run([uv, "venv", "--python", "3.11", str(venv_dir)], cwd=SKILL_DIR, check=True)
    if not _python_has_modules(str(python_bin)) or not _console_script_is_runnable(browser_use_bin):
        subprocess.run([uv, "pip", "install", "--reinstall", "--python", str(python_bin), "browser-use", "pydantic>=2.0"], cwd=SKILL_DIR, check=True)
        subprocess.run([str(browser_use_bin), "install"], cwd=SKILL_DIR, check=True)
    return str(python_bin), str(browser_use_bin)



def resolve_runtime() -> tuple[str, str]:
    global_python = _select_global_python()
    global_browser_use = shutil.which("browser-use")
    if global_python and global_browser_use and _console_script_is_runnable(Path(global_browser_use)):
        return global_python, global_browser_use
    return _ensure_uv_runtime()



def ensure_python_available() -> None:
    if shutil.which("python3") is None and not sys.executable:
        raise RuntimeError("Python is not available. Please install Python 3.11+ first.")


def ensure_obsidian_available() -> None:
    if shutil.which("obsidian") is None:
        raise RuntimeError("Obsidian CLI is not installed. Please install Obsidian and verify `obsidian help` first.")



def _prompt_bool(label: str, default: bool) -> bool:
    suffix = "Y/n" if default else "y/N"
    answer = input(f"{label} [{suffix}]: ").strip().lower()
    if not answer:
        return default
    return answer in {"y", "yes", "1", "true"}



def _prompt_int(label: str, default: int) -> int:
    answer = input(f"{label} [default: {default}]: ").strip()
    if not answer:
        return default
    return int(answer)



def _prompt_str(label: str, default: str = "") -> str:
    placeholder = default if default else "empty"
    answer = input(f"{label} [default: {placeholder}]: ").strip()
    return answer if answer else default



def resolve_options_interactively(args: argparse.Namespace, argv: list[str]) -> argparse.Namespace:
    if not sys.stdin.isatty():
        raise RuntimeError(
            "Interactive mode requires a TTY. Re-run without `--interactive` and pass explicit CLI flags instead."
        )
    if "--vault" not in argv:
        args.vault = _prompt_str("Obsidian vault name (leave empty to use the active vault)", args.vault)
    if "--limit-series" not in argv:
        args.limit_series = _prompt_int("Maximum number of series to process (0 = all)", args.limit_series)
    if "--limit-configs" not in argv:
        args.limit_configs = _prompt_int("Maximum number of configs to process (0 = all)", args.limit_configs)
    if "--configs-batch-size" not in argv:
        args.configs_batch_size = _prompt_int("Config batch size", args.configs_batch_size)
    if "--with-competitors" not in argv:
        args.with_competitors = _prompt_bool("Extract competitors as well?", False)
    if "--history-window-years" not in argv:
        args.history_window_years = _prompt_int("Historical model year window", args.history_window_years)
    if "--keep-session" not in argv:
        args.keep_session = _prompt_bool("Keep browser sessions open for manual inspection?", False)
    return args



def _run(cmd: list[str], env: dict[str, str]) -> None:
    print("$", " ".join(cmd))
    subprocess.run(cmd, cwd=SKILL_DIR, env=env, check=True)



def _run_configs_in_batches(browser_use: str, session_name: str, env: dict[str, str], run_dir: Path, batch_size: int) -> None:
    series_list = json.loads((run_dir / "series-list.json").read_text("utf-8"))
    batches = build_param_batches(len(series_list), batch_size)
    batch_paths = []
    for batch_index, (offset, limit) in enumerate(batches):
        batch_env = env.copy()
        output_name = f"all-configs.batch-{batch_index}.json"
        batch_env["DONGCHEDI_CONFIGS_OFFSET"] = str(offset)
        batch_env["DONGCHEDI_CONFIGS_LIMIT"] = str(limit)
        batch_env["DONGCHEDI_CONFIGS_OUTPUT"] = output_name
        batch_session = f"{session_name}-configs-{batch_index}"
        print(f"configs batch {batch_index + 1}/{len(batches)}: offset={offset}, limit={limit}, session={batch_session}")
        try:
            _run([browser_use, "--session", batch_session, "open", "https://www.dongchedi.com"], batch_env)
            _run([browser_use, "--session", batch_session, "python", "--file", "scripts/configs.py"], batch_env)
        finally:
            subprocess.run([browser_use, "--session", batch_session, "close"], cwd=SKILL_DIR, env=batch_env, check=False)
        batch_paths.append(run_dir / output_name)
    merge_json_list_outputs(batch_paths, run_dir / "all-configs.json")



def main(argv: list[str] | None = None) -> int:
    argv = list(argv) if argv is not None else sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(argv)
    ensure_python_available()
    if args.interactive:
        args = resolve_options_interactively(args, argv)
    # Publishing (and history inclusion) is now the default behavior for this skill.
    ensure_obsidian_available()

    python_bin, browser_use = resolve_runtime()
    run_dir = create_run_dir(Path(args.tmp_root), args.brand)
    session_name = f"brand-{_slugify(args.brand)}-{datetime.now().strftime('%H%M%S')}"
    env = os.environ.copy()
    env["DONGCHEDI_TMP_DIR"] = str(run_dir)
    # Always include historical/discontinued models. Keep the most recent N model years.
    env["DONGCHEDI_INCLUDE_HISTORY"] = "1"
    env["DONGCHEDI_HISTORY_CUTOFF_YEAR"] = str(datetime.now().year - args.history_window_years + 1)

    print(f"run_dir={run_dir}")
    print(f"session={session_name}")
    print(f"python={python_bin}")
    print(f"browser_use={browser_use}")

    try:
        _run([browser_use, "--session", session_name, "open", "https://www.dongchedi.com"], env)
        _run([browser_use, "--session", session_name, "python", f"KEYWORD = {args.brand!r}"], env)
        _run([browser_use, "--session", session_name, "python", "--file", "scripts/search.py"], env)
        assert_non_empty_json_list(run_dir / "search-results.json", "empty search results")

        _run([python_bin, "scripts/prepare_targets.py"], env)
        if args.limit_series > 0:
            trim_target_models(run_dir / "target-models.json", args.limit_series)
            print(f"trimmed target models to first {args.limit_series}")
        assert_non_empty_json_list(run_dir / "target-models.json", "empty target models")

        if args.with_competitors:
            _run([browser_use, "--session", session_name, "python", "--file", "scripts/competitors.py"], env)

        _run([python_bin, "scripts/build_series_list.py"], env)
        _run_configs_in_batches(browser_use, session_name, env, run_dir, args.configs_batch_size)
        assert_non_empty_json_list(run_dir / "all-configs.json", "empty configs extracted")

        if args.limit_configs > 0:
            trim_configs(run_dir / "all-configs.json", args.limit_configs)
            print(f"trimmed configs to first {args.limit_configs}")

        _run([python_bin, "scripts/params.py"], env)
        assert_non_empty_json_list(run_dir / "all-configs-with-params.json", "empty params extracted")

        diff_cmd = [python_bin, "scripts/diff.py"]
        if args.limit_configs > 0:
            diff_cmd.append("--skip-discontinued")
        if args.vault:
            diff_cmd.extend(["--vault", args.vault])
        _run(diff_cmd, env)

        store_cmd = [python_bin, "scripts/store.py", "--changelog"]
        if args.vault:
            store_cmd.extend(["--vault", args.vault])
        if args.with_competitors:
            store_cmd.append("--competitors")
        _run(store_cmd, env)

        print("\nPipeline completed.")
        print(f"Artifacts: {run_dir}")
        return 0
    finally:
        if not args.keep_session:
            subprocess.run([browser_use, "--session", session_name, "close"], cwd=SKILL_DIR, env=env, check=False)


if __name__ == "__main__":
    raise SystemExit(main())
