"""Discover competitors for target models.

Run: browser-use python --file scripts/competitors.py

Input: tmp/target-models.json (list of CarModel dicts)
Output: tmp/competitors.json
"""
import importlib
import json
import os
import sys
from pathlib import Path

module_file = globals().get("__file__")
SKILL_DIR = Path(module_file).resolve().parent.parent if module_file else Path.cwd().resolve()
TMP_DIR = Path(os.environ.get("DONGCHEDI_TMP_DIR", str(SKILL_DIR / "tmp"))).resolve()
TMP_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(SKILL_DIR))
dongchedi = importlib.import_module("lib.dongchedi")
dongchedi = importlib.reload(dongchedi)
series_url = dongchedi.series_url
parse_ssr_data = dongchedi.parse_ssr_data
extract_competitors = dongchedi.extract_competitors
extract_series_info = dongchedi.extract_series_info
ensure_not_captcha_interstitial = dongchedi.ensure_not_captcha_interstitial
classify_competitor = dongchedi.classify_competitor
from lib.types import CarModel

targets = [CarModel(**m) for m in json.loads((TMP_DIR / "target-models.json").read_text("utf-8"))]
result = {}

for target in targets:
    print(f"\n--- {target.name} (series_id={target.series_id}) ---")

    browser.goto(series_url(target.series_id))
    browser.wait(3)

    html = browser.html
    ensure_not_captcha_interstitial(html, f"series page {target.series_id}")
    ssr_data = parse_ssr_data(html)

    info = extract_series_info(ssr_data)
    if not target.level and info["level"]:
        target.level = info["level"]
    if not target.energy_type and info["energy_type"]:
        target.energy_type = info["energy_type"]
    if not target.price_range and info["price_range"]:
        target.price_range = info["price_range"]

    competitors = extract_competitors(ssr_data)
    print(f"  Found {len(competitors)} recommended competitors")

    classified = {"A": [], "B": [], "C": []}
    seen_ids = set()

    for comp in competitors:
        if comp.series_id in seen_ids:
            continue
        seen_ids.add(comp.series_id)
        tier = classify_competitor(target, comp)
        classified[tier].append(comp.model_dump())

    total = sum(len(v) for v in classified.values())
    print(f"  Classified: A={len(classified['A'])}, B={len(classified['B'])}, C={len(classified['C'])}, total={total}")

    result[target.name] = {
        "target": target.model_dump(),
        "competitors": classified,
    }

(TMP_DIR / "competitors.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(f"\nSaved competitors for {len(result)} models to {TMP_DIR / 'competitors.json'}")
