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
import time
import urllib.request
from pathlib import Path

module_file = globals().get("__file__")
SKILL_DIR = Path(module_file).resolve().parent.parent if module_file else Path.cwd().resolve()
TMP_DIR = Path(os.environ.get("DONGCHEDI_TMP_DIR", str(SKILL_DIR / "tmp"))).resolve()
TMP_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(SKILL_DIR))
dongchedi = importlib.import_module("lib.dongchedi")
dongchedi = importlib.reload(dongchedi)
series_url = dongchedi.series_url
series_car_list_url = dongchedi.series_car_list_url
parse_ssr_data = dongchedi.parse_ssr_data
extract_car_configs = dongchedi.extract_car_configs
extract_series_info = dongchedi.extract_series_info
filter_recent_history_configs = dongchedi.filter_recent_history_configs
ensure_not_captcha_interstitial = dongchedi.ensure_not_captcha_interstitial


USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
DEFAULT_CITY_NAME = os.environ.get("DONGCHEDI_CITY_NAME", "北京")


def fetch_text(url: str) -> str:
    browser_obj = globals().get("browser")
    if browser_obj is not None:
        browser_obj.goto(url)
        browser_obj.wait(2)
        return browser_obj.html

    last_error = None
    for attempt in range(3):
        try:
            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept-Language": "zh-CN,zh;q=0.9",
                },
            )
            with urllib.request.urlopen(request, timeout=30) as response:
                return response.read().decode("utf-8", errors="ignore")
        except Exception as exc:
            last_error = exc
            time.sleep(1 + attempt)
    raise last_error


def fetch_html(url: str) -> str:
    return fetch_text(url)


def fetch_json(url: str) -> dict:
    body = fetch_text(url)
    payload = json.loads(body)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object from {url}")
    return payload


def wrap_car_models_data(car_models_data: dict) -> dict:
    return {"props": {"pageProps": {"carModelsData": car_models_data}}}


def dedupe_configs(configs: list) -> list:
    deduped = []
    seen = set()
    for config in configs:
        key = config.car_id or f"{config.series_id}:{config.year}:{config.car_name}"
        if key in seen:
            continue
        seen.add(key)
        deduped.append(config)
    return deduped


def extract_recent_offline_configs(car_models_data: dict, cutoff_year: int) -> list:
    if not isinstance(car_models_data, dict):
        return []
    tab_list = car_models_data.get("tab_list", [])
    if not isinstance(tab_list, list):
        return []
    offline_tabs = [
        tab
        for tab in tab_list
        if isinstance(tab, dict) and tab.get("tab_key") == "offline"
    ]
    if not offline_tabs:
        return []
    history_ssr_data = wrap_car_models_data({"tab_list": offline_tabs})
    history_configs = extract_car_configs(history_ssr_data, include_history=True)
    return filter_recent_history_configs(history_configs, cutoff_year=cutoff_year)


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
        html = fetch_html(series_url(series_id))
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

        if include_history:
            try:
                api_payload = fetch_json(series_car_list_url(series_id, DEFAULT_CITY_NAME))
                api_car_models_data = api_payload.get("data", {}) if isinstance(api_payload, dict) else {}
                if isinstance(api_car_models_data, dict):
                    api_ssr_data = wrap_car_models_data(api_car_models_data)
                    if series_is_history:
                        configs = filter_recent_history_configs(
                            extract_car_configs(api_ssr_data, include_history=True),
                            cutoff_year=history_cutoff_year,
                        )
                    else:
                        online_configs = extract_car_configs(api_ssr_data, include_history=False)
                        offline_configs = extract_recent_offline_configs(
                            api_car_models_data,
                            cutoff_year=history_cutoff_year,
                        )
                        configs = online_configs + offline_configs
                    configs = dedupe_configs(configs)
            except Exception as api_exc:
                print(f"  WARN: history api fallback skipped: {api_exc}")

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
