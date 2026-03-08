"""Search dongchedi for car models.

Run: browser-use python "KEYWORD='示例品牌'"
     browser-use python --file scripts/search.py

Input: KEYWORD variable in browser-use python namespace
Output: tmp/search-results.json
"""
import importlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

module_file = globals().get("__file__")
SKILL_DIR = Path(module_file).resolve().parent.parent if module_file else Path.cwd().resolve()
TMP_DIR = Path(os.environ.get("DONGCHEDI_TMP_DIR", str(SKILL_DIR / "tmp"))).resolve()
TMP_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(SKILL_DIR))
dongchedi = importlib.import_module("lib.dongchedi")
dongchedi = importlib.reload(dongchedi)
search_url = dongchedi.search_url
parse_ssr_data = dongchedi.parse_ssr_data
extract_search_results = dongchedi.extract_search_results
ensure_not_captcha_interstitial = dongchedi.ensure_not_captcha_interstitial

keyword = KEYWORD
include_history = os.environ.get("DONGCHEDI_INCLUDE_HISTORY", "0") == "1"

print(f"Searching dongchedi for: {keyword}")
browser.goto(search_url(keyword))
browser.wait(3)

html = browser.html
page_url = getattr(browser, "url", search_url(keyword))
page_title = getattr(browser, "title", "")

(TMP_DIR / "raw-search.html").write_text(html, encoding="utf-8")
(TMP_DIR / "search-metadata.json").write_text(
    json.dumps(
        {
            "keyword": keyword,
            "url": page_url,
            "title": page_title,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "html_length": len(html),
        },
        ensure_ascii=False,
        indent=2,
    ),
    encoding="utf-8",
)

ensure_not_captcha_interstitial(html, "search page")
ssr_data = parse_ssr_data(html)
results = extract_search_results(ssr_data, include_history=include_history)

output = [r.model_dump() for r in results]
(TMP_DIR / "search-results.json").write_text(
    json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
)
(TMP_DIR / "search-metadata.json").write_text(
    json.dumps(
        {
            "keyword": keyword,
            "url": page_url,
            "title": page_title,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "html_length": len(html),
            "result_count": len(results),
        },
        ensure_ascii=False,
        indent=2,
    ),
    encoding="utf-8",
)
print(f"Found {len(results)} models:")
for r in results:
    print(f"  - {r.name} (series_id={r.series_id}, price={r.price_range})")
