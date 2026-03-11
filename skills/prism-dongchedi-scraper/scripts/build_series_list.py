"""Build tmp/series-list.json from confirmed targets and optional competitors.

Run: python3 scripts/build_series_list.py

Input: tmp/target-models.json, tmp/competitors.json (optional)
Output: tmp/series-list.json
"""
import json
import os
import sys
from pathlib import Path

module_file = globals().get("__file__")
SKILL_DIR = Path(module_file).resolve().parent.parent if module_file else Path.cwd().resolve()
TMP_DIR = Path(os.environ.get("DONGCHEDI_TMP_DIR", str(SKILL_DIR / "tmp"))).resolve()

sys.path.insert(0, str(SKILL_DIR))
from lib.dongchedi import build_series_list_entries, infer_brand_name
from lib.types import CarModel



def _targets_only_entries(target_models: list[CarModel]) -> list[dict]:
    return [
        {
            "series_id": model.series_id,
            "name": model.name,
            "brand": infer_brand_name(model.name),
            "price_range": model.price_range,
            "level": model.level,
            "energy_type": model.energy_type,
            "is_target": True,
            "is_history": "停售" in str(model.price_range),
        }
        for model in target_models
    ]



def main() -> None:
    target_path = TMP_DIR / "target-models.json"
    competitors_path = TMP_DIR / "competitors.json"

    if not target_path.exists():
        raise FileNotFoundError(f"{target_path} not found. Prepare target models first.")

    target_models = [CarModel(**item) for item in json.loads(target_path.read_text("utf-8"))]

    if competitors_path.exists():
        competitors_data = json.loads(competitors_path.read_text("utf-8"))
        entries = build_series_list_entries(target_models, competitors_data)
    else:
        competitors_data = {}
        entries = _targets_only_entries(target_models)

    output_path = TMP_DIR / "series-list.json"
    output_path.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Built {len(entries)} series entries -> {output_path}")
    if not competitors_data:
        print("  - competitors.json missing, fell back to target-only series list")
    for entry in entries:
        role = "target" if entry["is_target"] else "competitor"
        print(f"  - [{role}] {entry['name']} (series_id={entry['series_id']})")


if __name__ == "__main__":
    main()
