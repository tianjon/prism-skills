"""Run the post-competitor pipeline and publish notes to Obsidian.

Run: python3 scripts/publish_competitor_analysis.py [--vault <name>]

Requires: tmp/target-models.json and tmp/competitors.json already prepared.
Outputs: tmp/series-list.json, tmp/all-configs.json, tmp/all-configs-with-params.json,
         tmp/changes.json, and Obsidian notes.
"""
import argparse
import subprocess
import sys
from pathlib import Path

module_file = globals().get("__file__")
SKILL_DIR = Path(module_file).resolve().parent.parent if module_file else Path.cwd().resolve()


def run_step(label: str, command: list[str]) -> None:
    print(f"\n=== {label} ===")
    result = subprocess.run(command, cwd=SKILL_DIR)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish competitor analysis results to Obsidian")
    parser.add_argument("--vault", default="", help="Optional Obsidian vault name")
    args = parser.parse_args()

    run_step("Build series-list", [sys.executable, "scripts/build_series_list.py"])
    run_step("Open browser", [".venv/bin/browser-use", "open", "https://www.dongchedi.com"])
    run_step("Collect configs", [".venv/bin/browser-use", "python", "--file", "scripts/configs.py"])
    run_step("Collect params", [".venv/bin/browser-use", "python", "--file", "scripts/params.py"])

    diff_cmd = [sys.executable, "scripts/diff.py"]
    store_cmd = [sys.executable, "scripts/store.py", "--competitors", "--changelog"]
    if args.vault:
        diff_cmd.extend(["--vault", args.vault])
        store_cmd.extend(["--vault", args.vault])

    run_step("Diff against Obsidian", diff_cmd)
    run_step("Store to Obsidian", store_cmd)
    run_step("Close browser", [".venv/bin/browser-use", "close"])


if __name__ == "__main__":
    main()
