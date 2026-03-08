"""Collect all in-sale configurations for a list of series.

Run: browser-use python --file scripts/configs.py

Input: tmp/series-list.json (list of {series_id, name, ...})
Output: tmp/all-configs.json

Supports batching via `DONGCHEDI_CONFIGS_OFFSET`, `DONGCHEDI_CONFIGS_LIMIT`,
and `DONGCHEDI_CONFIGS_OUTPUT`.
"""
import importlib
import json
import os
import sys
from pathlib import Path

module_file = globals().get("__file__")
SKILL_DIR = Path(module_file).resolve().parent.parent if module_file else Path.cwd().resolve()
TMP_DIR = Path(os.environ.get("DONGCHEDI_TMP_DIR", str(SKILL_DIR / "tmp"))).resolve()

sys.path.insert(0, str(SKILL_DIR))
dongchedi = importlib.import_module("lib.dongchedi")
dongchedi = importlib.reload(dongchedi)
series_url = dongchedi.series_url
parse_ssr_data = dongchedi.parse_ssr_data
extract_car_configs = dongchedi.extract_car_configs
extract_series_info = dongchedi.extract_series_info
filter_recent_history_configs = dongchedi.filter_recent_history_configs
ensure_not_captcha_interstitial = dongchedi.ensure_not_captcha_interstitial

all_series = json.loads((TMP_DIR / "series-list.json").read_text("utf-8"))
offset = int(os.environ.get("DONGCHEDI_CONFIGS_OFFSET", "0"))
limit = int(os.environ.get("DONGCHEDI_CONFIGS_LIMIT", "0"))
output_name = os.environ.get("DONGCHEDI_CONFIGS_OUTPUT", "all-configs.json")
output_path = TMP_DIR / output_name
series_list = all_series[offset: offset + limit] if limit > 0 else all_series[offset:]
all_configs = []
errors = []
include_history = os.environ.get("DONGCHEDI_INCLUDE_HISTORY", "0") == "1"
history_cutoff_year = int(os.environ.get("DONGCHEDI_HISTORY_CUTOFF_YEAR", "2024"))

for i, series in enumerate(series_list):
    series_id = str(series.get("series_id", ""))
    name = series.get("name", "")
    is_target = series.get("is_target", False)
    level = series.get("level", "")
    energy_type = series.get("energy_type", "")
    brand = series.get("brand", "")

    print(f"[{i+1}/{len(series_list)}] {name} (series_id={series_id})")

    try:
        browser.goto(series_url(series_id))
        browser.wait(2)

        html = browser.html
        ensure_not_captcha_interstitial(html, f"series page {series_id}")
        ssr_data = parse_ssr_data(html)

        info = extract_series_info(ssr_data)
        if not level:
            level = info.get("level", "")
        if not energy_type:
            energy_type = info.get("energy_type", "")

        series_is_history = include_history and ("停售" in str(series.get("price_range", "")) or series.get("is_history"))
        configs = extract_car_configs(ssr_data, include_history=series_is_history)
        if series_is_history:
            configs = filter_recent_history_configs(configs, cutoff_year=history_cutoff_year)

        for config in configs:
            config.is_target = is_target
            config.level = level or config.level
            config.energy_type = energy_type or config.energy_type
            if brand:
                config.brand = brand
            all_configs.append(config.model_dump())

        print(f"  → {len(configs)} configs found")
    except Exception as e:
        print(f"  ERROR: {e}")
        errors.append({"series_id": series_id, "name": name, "error": str(e)})

output_path.write_text(
    json.dumps(all_configs, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(f"\nTotal: {len(all_configs)} configs from {len(series_list)} series ({len(errors)} errors)")
