"""Run the dongchedi brand pipeline end-to-end.

Example:
  python3 scripts/run_brand_pipeline.py --brand 宝马 --limit-series 3 --skip-store
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



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run dongchedi brand pipeline")
    parser.add_argument("--brand", required=True, help="品牌名，例如 宝马")
    parser.add_argument("--vault", default="", help="可选 Obsidian vault 名称")
    parser.add_argument("--limit-series", type=int, default=0, help="仅处理前 N 个车型，0 表示全部")
    parser.add_argument("--limit-configs", type=int, default=0, help="仅处理前 N 个配置，0 表示全部")
    parser.add_argument("--configs-batch-size", type=int, default=5, help="配置抓取分批大小，避免 browser-use CLI 超时")
    parser.add_argument("--with-competitors", action="store_true", help="抓取竞品并写入竞品分析")
    parser.add_argument("--include-history", action="store_true", help="补充停售/历史车型与停售配置")
    parser.add_argument("--history-window-years", type=int, default=3, help="历史车型仅保留最近 N 个年款窗口，默认 3")
    parser.add_argument("--skip-store", action="store_true", help="只抓取，不写入 Obsidian")
    parser.add_argument("--skip-params", action="store_true", help="只抓配置，不抓参数")
    parser.add_argument("--params-batch-size", type=int, default=1, help="参数抓取分批大小，避免 browser-use CLI 超时")
    parser.add_argument("--keep-session", action="store_true", help="保留 browser-use 会话，便于人工继续检查")
    parser.add_argument("--tmp-root", default=str(TMP_ROOT), help="运行目录根路径")
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
    merged = []
    for batch_path in batch_paths:
        if batch_path.exists():
            merged.extend(json.loads(batch_path.read_text("utf-8")))
    output_path.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")



def assert_non_empty_json_list(path: Path, message: str) -> list[dict]:
    if not path.exists():
        raise RuntimeError(f"{message}: missing {path}")
    payload = json.loads(path.read_text("utf-8"))
    if not isinstance(payload, list) or not payload:
        raise RuntimeError(message)
    return payload


def _browser_use_bin() -> str:
    local_bin = SKILL_DIR / ".venv" / "bin" / "browser-use"
    if local_bin.exists():
        return str(local_bin)
    return shutil.which("browser-use") or "browser-use"



def _run(cmd: list[str], env: dict[str, str]) -> None:
    print("$", " ".join(cmd))
    subprocess.run(cmd, cwd=SKILL_DIR, env=env, check=True)



def _run_configs_in_batches(browser_use: str, session_name: str, env: dict[str, str], run_dir: Path, batch_size: int) -> None:
    series_list_path = run_dir / "series-list.json"
    series_list = json.loads(series_list_path.read_text("utf-8"))
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


def _run_params_in_batches(browser_use: str, session_name: str, env: dict[str, str], run_dir: Path, batch_size: int) -> None:
    configs_path = run_dir / "all-configs.json"
    configs = json.loads(configs_path.read_text("utf-8"))
    batches = build_param_batches(len(configs), batch_size)
    batch_paths = []
    for batch_index, (offset, limit) in enumerate(batches):
        batch_env = env.copy()
        output_name = f"all-configs-with-params.batch-{batch_index}.json"
        batch_env["DONGCHEDI_PARAMS_OFFSET"] = str(offset)
        batch_env["DONGCHEDI_PARAMS_LIMIT"] = str(limit)
        batch_env["DONGCHEDI_PARAMS_OUTPUT"] = output_name
        batch_session = f"{session_name}-params-{batch_index}"
        print(f"params batch {batch_index + 1}/{len(batches)}: offset={offset}, limit={limit}, session={batch_session}")
        try:
            _run([browser_use, "--session", batch_session, "open", "https://www.dongchedi.com"], batch_env)
            _run([browser_use, "--session", batch_session, "python", "--file", "scripts/params.py"], batch_env)
        finally:
            subprocess.run([browser_use, "--session", batch_session, "close"], cwd=SKILL_DIR, env=batch_env, check=False)
        batch_paths.append(run_dir / output_name)
    merge_param_batch_outputs(batch_paths, run_dir / "all-configs-with-params.json")



def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    run_dir = create_run_dir(Path(args.tmp_root), args.brand)
    session_name = f"brand-{_slugify(args.brand)}-{datetime.now().strftime('%H%M%S')}"
    env = os.environ.copy()
    env["DONGCHEDI_TMP_DIR"] = str(run_dir)
    if args.include_history:
        env["DONGCHEDI_INCLUDE_HISTORY"] = "1"
        env["DONGCHEDI_HISTORY_CUTOFF_YEAR"] = str(datetime.now().year - args.history_window_years + 1)

    browser_use = _browser_use_bin()
    python_bin = sys.executable

    print(f"run_dir={run_dir}")
    print(f"session={session_name}")

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

        if not args.skip_params:
            _run([python_bin, "scripts/params.py"], env)
            assert_non_empty_json_list(run_dir / "all-configs-with-params.json", "empty params extracted")

        if not args.skip_store:
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
            try:
                subprocess.run([browser_use, "--session", session_name, "close"], cwd=SKILL_DIR, env=env, check=False)
            except Exception:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
