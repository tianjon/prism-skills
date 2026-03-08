"""Batch extract configuration parameters.

Run: python3 scripts/params.py
     browser-use python --file scripts/params.py

Input: tmp/all-configs.json
Output: tmp/all-configs-with-params.json

This script now prefers direct HTTP fetches for params pages because dongchedi
serves SSR rawData there. When a `browser` object exists, it can still fall back
to browser fetching for compatibility.

Supports batching via `DONGCHEDI_PARAMS_OFFSET`, `DONGCHEDI_PARAMS_LIMIT`,
and `DONGCHEDI_PARAMS_OUTPUT` environment variables.
"""
import html as html_mod
import importlib
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path

module_file = globals().get("__file__")
SKILL_DIR = Path(module_file).resolve().parent.parent if module_file else Path.cwd().resolve()
TMP_DIR = Path(os.environ.get("DONGCHEDI_TMP_DIR", str(SKILL_DIR / "tmp"))).resolve()

sys.path.insert(0, str(SKILL_DIR))
dongchedi = importlib.import_module("lib.dongchedi")
dongchedi = importlib.reload(dongchedi)
params_url = dongchedi.params_url
parse_params_text = dongchedi.parse_params_text
parse_ssr_data = dongchedi.parse_ssr_data
extract_params_from_ssr = dongchedi.extract_params_from_ssr
ensure_not_captcha_interstitial = dongchedi.ensure_not_captcha_interstitial


USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"



def fetch_html(url: str) -> str:
    browser_obj = globals().get("browser")
    if browser_obj is not None:
        browser_obj.goto(url)
        browser_obj.wait(2.5)
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


all_configs = json.loads((TMP_DIR / "all-configs.json").read_text("utf-8"))
offset = int(os.environ.get("DONGCHEDI_PARAMS_OFFSET", "0"))
limit = int(os.environ.get("DONGCHEDI_PARAMS_LIMIT", "0"))
output_name = os.environ.get("DONGCHEDI_PARAMS_OUTPUT", "all-configs-with-params.json")
output_path = TMP_DIR / output_name
configs = all_configs[offset: offset + limit] if limit > 0 else all_configs[offset:]
results = []
errors = []
start_time = time.time()

print(f"Starting batch params extraction for {len(configs)} configs (offset={offset}, limit={limit or 'all'})...")

for i, config in enumerate(configs):
    car_id = config.get("car_id", "")
    car_name = config.get("car_name", "")
    series_name = config.get("series_name", "")

    try:
        html = fetch_html(params_url(car_id))
        ensure_not_captcha_interstitial(html, f"params page {car_id}")

        ssr_data = parse_ssr_data(html)
        params = extract_params_from_ssr(ssr_data)
        params_source = "ssr"

        if not params:
            body_match = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL)
            if body_match:
                body_html = body_match.group(1)
                body_html = re.sub(r'<script[^>]*>.*?</script>', '', body_html, flags=re.DOTALL)
                body_html = re.sub(r'<style[^>]*>.*?</style>', '', body_html, flags=re.DOTALL)
                body_html = re.sub(r'<br\s*/?>', '\n', body_html)
                body_html = re.sub(r'</(?:p|div|tr|li|h[1-6])>', '\n', body_html)
                body_html = re.sub(r'</t[dh]>', '\t', body_html)
                text = re.sub(r'<[^>]+>', '', body_html)
                text = html_mod.unescape(text)
            else:
                text = ""
            params = parse_params_text(text)
            params_source = "text"

        config["params"] = [p.model_dump() for p in params]
        config["params_error"] = None
        config["params_source"] = params_source
        results.append(config)

        elapsed = time.time() - start_time
        rate = (i + 1) / elapsed if elapsed > 0 else 0
        eta = (len(configs) - i - 1) / rate if rate > 0 else 0
        print(f"  [{i+1}/{len(configs)}] {series_name} {car_name} → {len(params)} params via {params_source} (ETA: {eta:.0f}s)")

    except Exception as e:
        config["params"] = []
        config["params_error"] = str(e)
        config["params_source"] = "error"
        results.append(config)
        errors.append({"car_id": car_id, "name": f"{series_name} {car_name}", "error": str(e)})
        print(f"  [{i+1}/{len(configs)}] ERROR: {series_name} {car_name}: {e}")

    if (i + 1) % 50 == 0:
        output_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  Progress saved ({i+1}/{len(configs)})")

output_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

elapsed = time.time() - start_time
print(f"\nDone. {len(results)} configs processed in {elapsed:.0f}s ({len(errors)} errors)")
if errors:
    print("Errors:")
    for e in errors:
        print(f"  - {e['name']}: {e['error']}")
