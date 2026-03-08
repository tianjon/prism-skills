"""Prepare confirmed target models for competitor analysis.

Run:
  python3 scripts/prepare_targets.py
  python3 scripts/prepare_targets.py --series-ids 5308,10033

Input: tmp/search-results.json
Output: tmp/target-models.json
"""
import argparse
import json
import os
import sys
from pathlib import Path

module_file = globals().get("__file__")
SKILL_DIR = Path(module_file).resolve().parent.parent if module_file else Path.cwd().resolve()
TMP_DIR = Path(os.environ.get("DONGCHEDI_TMP_DIR", str(SKILL_DIR / "tmp"))).resolve()
TMP_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(SKILL_DIR))
from lib.dongchedi import select_target_models
from lib.types import CarModel


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build tmp/target-models.json from search results")
    parser.add_argument(
        "--series-ids",
        default="",
        help="Comma-separated series ids to keep, preserving the provided order. Default keeps all detected models.",
    )
    return parser.parse_args()



def main() -> None:
    args = parse_args()
    search_results_path = TMP_DIR / "search-results.json"
    if not search_results_path.exists():
        raise FileNotFoundError(f"{search_results_path} not found. Run scripts/search.py first.")

    raw_models = json.loads(search_results_path.read_text("utf-8"))
    models = [CarModel(**item) for item in raw_models]

    series_ids = [item.strip() for item in args.series_ids.split(",") if item.strip()]
    selected = select_target_models(models, series_ids or None)

    output_path = TMP_DIR / "target-models.json"
    output_path.write_text(
        json.dumps([model.model_dump() for model in selected], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Prepared {len(selected)} target models -> {output_path}")
    for model in selected:
        print(f"  - {model.name} (series_id={model.series_id}, price={model.price_range})")


if __name__ == "__main__":
    main()
