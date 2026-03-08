"""Dongchedi data extraction and parsing logic.

All functions are pure data processing - no browser dependency.
They parse HTML or structured text extracted from dongchedi.com pages.
"""

from __future__ import annotations

import json
import re
from urllib.parse import quote

from .types import CarConfig, CarModel, ParamItem


# URL builders

def search_url(keyword: str) -> str:
    """Build dongchedi search URL."""
    encoded = quote(keyword)
    return f"https://www.dongchedi.com/search?keyword={encoded}&currTab=1&city_name=%E5%8C%97%E4%BA%AC&search_mode=sug"


def series_url(series_id: str) -> str:
    """Build dongchedi series page URL."""
    return f"https://www.dongchedi.com/auto/series/{series_id}"


def params_url(car_id: str) -> str:
    """Build dongchedi params page URL."""
    return f"https://www.dongchedi.com/auto/params-carIds-{car_id}"


# SSR data extraction

def is_captcha_interstitial(html: str) -> bool:
    """Return True when dongchedi serves the captcha middle page."""
    if not html:
        return False

    markers = (
        "验证码中间页",
        "window.ttgcaptcha",
        "verifycenter/captcha",
        "captcha/index.js",
        "rmc.bytedance.com/verifycenter",
    )
    lowered = html.lower()
    return any(marker in html or marker in lowered for marker in markers)


def ensure_not_captcha_interstitial(html: str, context: str) -> None:
    """Raise a clear error when dongchedi blocks the page behind captcha."""
    if is_captcha_interstitial(html):
        raise RuntimeError(
            f"dongchedi returned a captcha interstitial for {context}. Solve the captcha in the opened browser, then rerun the script."
        )


def parse_ssr_data(html: str) -> dict:
    """Extract __NEXT_DATA__ JSON from page HTML.

    Returns the parsed JSON object, or empty dict if not found.
    Handles pages where the JSON string itself contains a literal ``</script>``.
    """
    start_match = re.search(r'<script[^>]*id="__NEXT_DATA__"[^>]*>', html, re.DOTALL)
    if not start_match:
        return {}

    start = start_match.end()
    json_start = html.find('{', start)
    if json_start == -1:
        return {}

    depth = 0
    in_string = False
    escape = False
    for index in range(json_start, len(html)):
        char = html[index]
        if in_string:
            if escape:
                escape = False
            elif char == '\\':
                escape = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(html[json_start:index + 1])
                except json.JSONDecodeError:
                    return {}
    return {}


def extract_search_results(ssr_data: dict, include_history: bool = False) -> list[CarModel]:
    """Extract car models from search page SSR data.

    Supports both the older flat series list and the current brand-card
    structure where series are nested under display.sub_brand_list.item[].
    """
    results = []
    seen_series_ids: set[str] = set()
    try:
        items = ssr_data["props"]["pageProps"]["searchData"]["data"]
    except (KeyError, TypeError):
        return results

    def add_result(series_id: str, name: str, price: str, series_type: str, energy_type: str = "") -> None:
        if not series_id or not name or series_id in seen_series_ids:
            return
        if include_history and isinstance(price, str) and "未上市" in price:
            return
        seen_series_ids.add(series_id)
        results.append(CarModel(
            name=name,
            series_id=series_id,
            price_range=price,
            level=series_type,
            energy_type=energy_type,
        ))

    for item in items:
        display = item.get("display", {}) if isinstance(item, dict) else {}

        series_id = str(item.get("series_id", "")) if isinstance(item, dict) else ""
        name = display.get("series_name", "") if isinstance(display, dict) else ""
        price = display.get("official_price", "") if isinstance(display, dict) else ""
        series_type = display.get("series_type", "") if isinstance(display, dict) else ""
        energy_type = display.get("energy_type", "") if isinstance(display, dict) else ""
        add_result(series_id, name, price, series_type, energy_type)

        sub_brand_items = display.get("sub_brand_list", {}).get("item", []) if isinstance(display, dict) else []
        for sub_brand in sub_brand_items:
            if not isinstance(sub_brand, dict):
                continue
            series_items = sub_brand.get("series_list", {}).get("item", [])
            for series in series_items:
                if not isinstance(series, dict):
                    continue
                online_car_count = series.get("online_car_count")
                if not include_history:
                    if series.get("is_salestop"):
                        continue
                    if online_car_count is not None and int(online_car_count or 0) <= 0:
                        continue
                add_result(
                    str(series.get("series_id", "")),
                    series.get("name", ""),
                    series.get("pricelimits", ""),
                    series.get("level", ""),
                    series.get("energy_type", ""),
                )

        series_tabs = display.get("series_tabs", []) if isinstance(display, dict) else []
        for tab in series_tabs:
            if not isinstance(tab, dict):
                continue
            series_list = tab.get("series_list", [])
            if isinstance(series_list, dict):
                series_items = series_list.get("item", [])
            else:
                series_items = series_list
            for series in series_items:
                if not isinstance(series, dict):
                    continue
                online_car_count = series.get("online_car_count")
                if not include_history:
                    if series.get("is_salestop"):
                        continue
                    if online_car_count is not None and int(online_car_count or 0) <= 0:
                        continue
                add_result(
                    str(series.get("series_id", "")),
                    series.get("name", ""),
                    series.get("price", "") or series.get("pricelimits", ""),
                    series.get("level", ""),
                    series.get("energy_type", ""),
                )
    return results


def select_target_models(models: list[CarModel], series_ids: list[str] | None = None) -> list[CarModel]:
    """Select confirmed target models from detected search results.

    When ``series_ids`` is omitted, keep all detected models in their original order.
    When provided, preserve the caller's order and validate that every series id exists.
    """
    if not series_ids:
        return list(models)

    index = {model.series_id: model for model in models}
    selected = []
    for series_id in series_ids:
        if series_id not in index:
            raise ValueError(f"Unknown series_id: {series_id}")
        selected.append(index[series_id])
    return selected


def infer_brand_name(model_name: str) -> str:
    """Infer a brand-like prefix from a series name for note metadata."""
    if not model_name:
        return ""

    first_token = model_name.split()[0]

    match = re.match(r'^([\u4e00-\u9fff]+)', first_token)
    if match:
        return match.group(1)

    match = re.match(r'^([A-Za-z]+)', first_token)
    if match:
        return match.group(1)

    return first_token


def build_series_list_entries(
    target_models: list[CarModel],
    competitors_data: dict,
) -> list[dict]:
    """Merge targets and competitors into the series-list format used by configs.py."""
    entries = []
    seen_series_ids: set[str] = set()

    def add_entry(model: CarModel, is_target: bool) -> None:
        if model.series_id in seen_series_ids:
            return
        seen_series_ids.add(model.series_id)
        entries.append({
            "series_id": model.series_id,
            "name": model.name,
            "brand": infer_brand_name(model.name),
            "level": model.level,
            "energy_type": model.energy_type,
            "is_target": is_target,
        })

    for model in target_models:
        add_entry(model, True)

    for payload in competitors_data.values():
        competitors = payload.get("competitors", {}) if isinstance(payload, dict) else {}
        for tier in ("A", "B", "C"):
            for raw_model in competitors.get(tier, []):
                model = raw_model if isinstance(raw_model, CarModel) else CarModel(**raw_model)
                add_entry(model, False)

    return entries


def extract_car_configs(ssr_data: dict, include_history: bool = False) -> list[CarConfig]:
    """Extract in-sale car configurations from series page SSR data.

    Path: props.pageProps.carModelsData.tab_list[] where tab_key="online_all"
    Supports both the legacy flat config entries and the current nested
    structure where config fields live under ``entry.info``.
    """
    configs = []
    try:
        page_props = ssr_data["props"]["pageProps"]
        tab_list = page_props["carModelsData"]["tab_list"]
    except (KeyError, TypeError):
        return configs

    selected_tabs = []
    if include_history:
        selected_tabs = [tab for tab in tab_list if isinstance(tab, dict)]
    else:
        online_tab = None
        for tab in tab_list:
            if tab.get("tab_key") == "online_all":
                online_tab = tab
                break
        if online_tab:
            selected_tabs = [online_tab]
        elif tab_list:
            selected_tabs = [tab_list[0]]
        else:
            return configs

    for tab in selected_tabs:
        for entry in tab.get("data", []):
            if not isinstance(entry, dict) or str(entry.get("type")) != "1115":
                continue

            payload = entry.get("info") if isinstance(entry.get("info"), dict) else entry

            car_id = str(payload.get("car_id", payload.get("id", "")))
            car_name = payload.get("car_name", "") or payload.get("name", "")
            price = str(payload.get("price", "") or payload.get("official_price_str", "") or payload.get("official_price", ""))
            year = str(payload.get("year", payload.get("car_year", "")) or "")
            series_name = payload.get("series_name", "")
            series_id = str(payload.get("series_id", ""))
            brand_name = payload.get("brand_name", "")

            if car_id and car_name:
                configs.append(CarConfig(
                    car_id=car_id,
                    car_name=car_name,
                    price=price,
                    year=year,
                    series_name=series_name,
                    series_id=series_id,
                    brand_name=brand_name,
                    brand=brand_name,
                ))
    return configs


def filter_recent_history_configs(configs: list[CarConfig], cutoff_year: int) -> list[CarConfig]:
    """Keep only configs whose model year is on/after the cutoff year."""
    kept = []
    for config in configs:
        try:
            year = int(str(config.year).strip()[:4])
        except (TypeError, ValueError):
            continue
        if year >= cutoff_year:
            kept.append(config)
    return kept


def extract_series_info(ssr_data: dict) -> dict:
    """Extract series-level info (level, energy_type, price) from SSR data.

    Returns dict with keys: level, energy_type, price_range, name.
    Supports both the older ``seriesInfo`` structure and newer page-level
    fallbacks such as ``seriesName``, ``seriesHomeHead`` and ``overviewData``.
    """
    info = {"level": "", "energy_type": "", "price_range": "", "name": ""}
    try:
        page_props = ssr_data["props"]["pageProps"]
    except (KeyError, TypeError):
        return info

    series_info = page_props.get("seriesInfo", {}) if isinstance(page_props, dict) else {}
    if isinstance(series_info, dict):
        info["name"] = series_info.get("series_name", "") or info["name"]
        info["level"] = series_info.get("series_type", "") or info["level"]
        info["energy_type"] = series_info.get("energy_type", "") or info["energy_type"]
        info["price_range"] = series_info.get("official_price", "") or info["price_range"]

    info["name"] = info["name"] or page_props.get("seriesName", "")

    series_home_head = page_props.get("seriesHomeHead", {})
    if isinstance(series_home_head, dict):
        info["level"] = info["level"] or series_home_head.get("series_type", "")
        info["price_range"] = info["price_range"] or series_home_head.get("sub_title", "") or series_home_head.get("official_price", "")

    overview_data = page_props.get("overviewData", {})
    if isinstance(overview_data, dict):
        info["energy_type"] = info["energy_type"] or overview_data.get("energy_type", "")
        info["level"] = info["level"] or overview_data.get("series_type", "")
        info["price_range"] = info["price_range"] or overview_data.get("official_price", "")

    return info


def extract_competitors(ssr_data: dict) -> list[CarModel]:
    """Extract competitor recommendations from series page SSR data.

    Path: props.pageProps.sameLevelData (rcm_compared_series_item)
    """
    competitors = []
    try:
        page_props = ssr_data["props"]["pageProps"]
        same_level = page_props.get("sameLevelData", {})

        if not isinstance(same_level, dict):
            return competitors

        items = same_level.get("rcm_compared_series_item", [])
        if not isinstance(items, list):
            return competitors

        for item in items:
            series_id = str(item.get("series_id", ""))
            name = item.get("series_name", "")
            price = item.get("official_price", "")
            level = item.get("series_type", "")
            energy = item.get("energy_type", "")

            if series_id and name:
                competitors.append(CarModel(
                    name=name,
                    series_id=series_id,
                    price_range=price,
                    level=level,
                    energy_type=energy,
                ))
    except (KeyError, TypeError):
        pass
    return competitors


# Params page parsing


def _normalize_param_value(raw_value) -> str:
    """Normalize parameter values from dongchedi rawData structures."""
    if raw_value is None:
        return ""
    if isinstance(raw_value, dict):
        value = raw_value.get("value")
        if value:
            return str(value).strip()
        icon_type = raw_value.get("icon_type")
        icon_map = {1: "标配", 2: "选配", 3: "无"}
        if icon_type in icon_map:
            return icon_map[icon_type]
        return ""
    if isinstance(raw_value, (str, int, float)):
        return str(raw_value).strip()
    return ""


def extract_params_from_ssr(ssr_data: dict) -> list[ParamItem]:
    """Extract structured params from params-page SSR rawData.

    The current dongchedi params page exposes `pageProps.rawData.properties`
    as the ordered parameter definition list and `pageProps.rawData.car_info[0].info`
    as the value mapping for the current trim.
    """
    params = []
    try:
        raw_data = ssr_data["props"]["pageProps"]["rawData"]
        properties = raw_data["properties"]
        car_info = raw_data["car_info"][0]["info"]
    except (KeyError, TypeError, IndexError):
        return params

    current_category = "基本信息"
    seen = set()

    for item in properties:
        if not isinstance(item, dict):
            continue

        item_type = item.get("type")
        text = (item.get("text") or "").strip()
        key = item.get("key") or ""

        if item_type in {0, 2, 4, 6}:
            if text:
                current_category = text
            continue

        if item_type == 1:
            value = _normalize_param_value(car_info.get(key))
            if text and value:
                dedupe_key = (current_category, text, value)
                if dedupe_key not in seen:
                    seen.add(dedupe_key)
                    params.append(ParamItem(category=current_category, name=text, value=value))
            continue

        if item_type == 3:
            sub_list = item.get("sub_list")
            if isinstance(sub_list, list) and sub_list:
                for sub_item in sub_list:
                    if not isinstance(sub_item, dict):
                        continue
                    sub_name = (sub_item.get("text") or "").strip()
                    sub_key = sub_item.get("key") or ""
                    value = _normalize_param_value(car_info.get(sub_key))
                    if sub_name and value:
                        dedupe_key = (current_category, sub_name, value)
                        if dedupe_key not in seen:
                            seen.add(dedupe_key)
                            params.append(ParamItem(category=current_category, name=sub_name, value=value))
            else:
                value = _normalize_param_value(car_info.get(key))
                if text and value:
                    dedupe_key = (current_category, text, value)
                    if dedupe_key not in seen:
                        seen.add(dedupe_key)
                        params.append(ParamItem(category=current_category, name=text, value=value))

    return params


def parse_params_text(text: str) -> list[ParamItem]:
    """Parse parameters from the body.innerText of a dongchedi params page.

    The text is structured with category headers followed by parameter rows.
    Each row has a parameter name and value separated by whitespace.

    Category detection: lines that are short, standalone, and followed by
    param-value pairs are treated as category headers.

    Known categories include: 基本信息, 车身, 发动机, 电动机, 变速箱,
    底盘转向, 车轮制动, 主动安全, 被动安全, 辅助驾驶, 外部配置,
    内部配置, 座椅配置, 多媒体配置, 灯光配置, 玻璃/后视镜, 空调/冰箱
    """
    if not text or not text.strip():
        return []

    lines = text.split("\n")
    params = []
    current_category = "基本信息"

    # Known category names for reliable detection
    known_categories = {
        "基本信息", "车身", "发动机", "电动机", "变速箱", "底盘转向",
        "车轮制动", "主动安全", "被动安全", "辅助驾驶", "外部配置",
        "内部配置", "座椅配置", "多媒体配置", "灯光配置", "玻璃/后视镜",
        "空调/冰箱", "选装包", "电池/充电", "油耗/续航",
    }

    # Skip header noise lines
    skip_patterns = [
        "对比", "询底价", "获取底价", "经销商报价", "车主价格",
        "添加", "关注", "收藏",
    ]

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check if this is a known category header
        if line in known_categories:
            current_category = line
            continue

        # Skip noise lines
        if any(p in line for p in skip_patterns) and len(line) < 10:
            continue

        # Try to split into name-value pairs
        # Common separators: tab, multiple spaces
        parts = re.split(r"\t+", line)
        if len(parts) == 2:
            name, value = parts[0].strip(), parts[1].strip()
            if name and value:
                params.append(ParamItem(
                    category=current_category,
                    name=name,
                    value=value,
                ))
                continue

        # Try splitting by multiple spaces (>=2)
        parts = re.split(r"\s{2,}", line)
        if len(parts) == 2:
            name, value = parts[0].strip(), parts[1].strip()
            if name and value and len(name) > 1:
                params.append(ParamItem(
                    category=current_category,
                    name=name,
                    value=value,
                ))

    return params


# Competitor classification

def _parse_price_range(price_str: str) -> tuple[float, float]:
    """Parse price range string like '19.99-28.99万' into (min, max) floats."""
    nums = re.findall(r"(\d+\.?\d*)", price_str)
    if len(nums) >= 2:
        return float(nums[0]), float(nums[-1])
    elif len(nums) == 1:
        v = float(nums[0])
        return v, v
    return 0.0, 0.0


def _price_overlap(a_range: str, b_range: str, tolerance: float = 2.0) -> bool:
    """Check if two price ranges overlap within tolerance (万)."""
    a_min, a_max = _parse_price_range(a_range)
    b_min, b_max = _parse_price_range(b_range)
    return a_min - tolerance <= b_max and b_min - tolerance <= a_max


def classify_competitor(target: CarModel, candidate: CarModel) -> str:
    """Classify a competitor as A/B/C tier.

    A: price ±2万 + same level + same energy type
    B: partial overlap (same level different energy, or same price different level)
    C: cross-dimension but overlapping user base
    """
    same_level = target.level == candidate.level
    same_energy = target.energy_type == candidate.energy_type
    price_close = _price_overlap(target.price_range, candidate.price_range)

    if same_level and price_close and same_energy:
        return "A"
    elif (same_level and price_close) or (same_level and same_energy) or (price_close and same_energy):
        return "B"
    else:
        return "C"
