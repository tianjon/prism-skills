"""Markdown formatting for Obsidian notes."""

from __future__ import annotations

from datetime import datetime

from .types import CarConfig, CarModel, ChangeRecord, ParamItem


def _safe_segment(value: str, fallback: str) -> str:
    cleaned = (value or "").strip().replace("/", "-").replace("\\", "-").replace(":", "-")
    return cleaned or fallback


def _brand_segment(config: CarConfig) -> str:
    return _safe_segment(config.brand or config.brand_name, "未分类品牌")


def _series_segment(config: CarConfig) -> str:
    return _safe_segment(config.series_name, "未命名车型")


def _trim_display(config: CarConfig) -> str:
    base_name = (config.car_name or "").strip()
    year = (config.year or "").strip()
    if year:
        year_prefix = f"{year}款"
        if not base_name.startswith(year_prefix) and not base_name.startswith(year):
            base_name = f"{year_prefix} {base_name}".strip()
    return base_name or "未命名款型"


def _trim_segment(config: CarConfig) -> str:
    return _safe_segment(_trim_display(config), "未命名款型")


def config_current_note_path(config: CarConfig) -> str:
    """Generate the current-state note path for a car configuration."""
    return f"汽车/品牌库/{_brand_segment(config)}/{_series_segment(config)}/当前款型/{_trim_segment(config)}.md"



def config_snapshot_note_path(config: CarConfig, update_month: str) -> str:
    """Generate the month-scoped snapshot note path for a car configuration."""
    month = _safe_segment(update_month, datetime.now().strftime("%Y-%m"))
    return f"汽车/品牌库/{_brand_segment(config)}/{_series_segment(config)}/更新记录/{month}/{_trim_segment(config)}.md"



def series_overview_note_path(config: CarConfig) -> str:
    """Generate the overview note path for a series."""
    return f"汽车/品牌库/{_brand_segment(config)}/{_series_segment(config)}/00-车型总览.md"



def monthly_changelog_note_path(config: CarConfig, update_month: str) -> str:
    """Generate the month summary note path for a series."""
    month = _safe_segment(update_month, datetime.now().strftime("%Y-%m"))
    return f"汽车/品牌库/{_brand_segment(config)}/{_series_segment(config)}/更新记录/{month}/00-本月更新摘要.md"



def competitor_index_note_path(target: CarModel, brand: str, update_month: str) -> str:
    """Generate the competitor index note path for a series in a month archive."""
    brand_segment = _safe_segment(brand, "未分类品牌")
    series_segment = _safe_segment(target.name, "未命名车型")
    month = _safe_segment(update_month, datetime.now().strftime("%Y-%m"))
    return f"汽车/品牌库/{brand_segment}/{series_segment}/更新记录/{month}/竞品分析.md"



def config_current_note_name(config: CarConfig) -> str:
    """Generate the display name for the current-state config note."""
    return _trim_segment(config)



def config_snapshot_note_name(config: CarConfig, update_month: str) -> str:
    """Generate the display name for the month snapshot config note."""
    return f"{update_month}-{_trim_segment(config)}"



def _sanitize_tag(value: str) -> str:
    """Normalize tags for Obsidian compatibility."""
    normalized = str(value).strip()
    normalized = normalized.replace(" ", "")
    normalized = normalized.replace("/", "-")
    normalized = normalized.replace("(", "").replace(")", "")
    return normalized


def _sanitize_table_cell(value: str) -> str:
    """Escape markdown table-breaking characters inside cell content."""
    normalized = str(value).replace("\r\n", "\n").replace("\r", "\n")
    normalized = normalized.replace("|", "\\|")
    normalized = normalized.replace("\n", "<br>")
    return normalized


def format_config_note(
    config: CarConfig,
    params: list[ParamItem],
    changes: list[ChangeRecord] | None = None,
) -> str:
    """Format a full Markdown note for a car configuration.

    Includes YAML frontmatter, change callouts (if any), and parameter table.
    """
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    update_month = now.strftime("%Y-%m")
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S CST")

    is_discontinued = any(c.change_type == "discontinued" for c in (changes or []))

    tags = ["汽车", "参数配置"]
    if config.series_name:
        tags.append(config.series_name)
    tags.append("懂车帝")
    if config.brand:
        tags.append(config.brand)
    if config.energy_type:
        tags.append(config.energy_type)
    if config.level:
        tags.append(config.level)
    if is_discontinued:
        tags.append("停售")

    tags = [_sanitize_tag(t) for t in tags if str(t).strip()]
    tags_yaml = "\n".join(f"  - {t}" for t in tags)

    model_url = f"https://www.dongchedi.com/auto/series/{config.series_id}/model-{config.car_id}" if config.series_id and config.car_id else ""
    source_url = f"https://www.dongchedi.com/auto/params-carIds-{config.car_id}"
    community_url = f"https://www.dongchedi.com/community/{config.series_id}" if config.series_id else ""
    score_url = f"https://www.dongchedi.com/auto/series/score/{config.series_id}-x-x-x-x-x" if config.series_id else ""
    title = f"{config.series_name} {_trim_display(config)} 参数配置"

    frontmatter = f"""---
title: "{title}"
tags:
{tags_yaml}
source: "{source_url}"
created: {today}
updated: {today}
update_month: "{update_month}"
price: "{config.price}"
brand: "{_brand_segment(config)}"
model: "{config.series_name}"
trim: "{_trim_display(config)}"
model_year: "{config.year}"
level: "{config.level}"
energy_type: "{config.energy_type}"
---"""

    callout_parts: list[str] = []
    if is_discontinued:
        callout_parts.append(format_discontinued_callout())
    if changes:
        # Avoid duplicating the discontinued note: the warning callout above is more explicit.
        change_items = [c for c in changes if c.change_type != "discontinued"]
        if change_items:
            callout_parts.append(format_change_callout(change_items, today))
    callout = ("\n" + "\n\n".join(callout_parts) + "\n") if callout_parts else ""

    if params:
        table_rows = "\n".join(
            f"| {_sanitize_table_cell(p.category)} | {_sanitize_table_cell(p.name)} | {_sanitize_table_cell(p.value)} |" for p in params
        )
        table = f"""| 参数分类 | 参数项 | 参数值 |
|---|---|---|
{table_rows}"""
    else:
        table = "*参数数据暂未获取*"

    body = f"""{frontmatter}
{callout}
# {title}

- 固定链接: [车型首页]({model_url}) · [参数配置]({source_url}) · [车友圈]({community_url}) · [懂车分(口碑)]({score_url})
- 抓取时间: {timestamp}
- 更新月份: {update_month}
- 品牌: {_brand_segment(config)}
- 车型: {config.series_name}
- 款型: {_trim_display(config)}
- 指导价: {config.price}

## 参数表

{table}
"""
    return body



def format_series_overview_note(config: CarConfig, current_note_names: list[str], update_month: str) -> str:
    """Format a series overview note aggregating current trims and month snapshot links."""
    today = datetime.now().strftime("%Y-%m-%d")
    current_links = "\n".join(f"- [[{name}]]" for name in sorted(current_note_names)) or "- 暂无款型"
    brand = _brand_segment(config)
    series_name = _series_segment(config)
    series_home_url = f"https://www.dongchedi.com/auto/series/{config.series_id}" if config.series_id else ""
    params_url = f"https://www.dongchedi.com/auto/params-carIds-x-{config.series_id}" if config.series_id else ""
    community_url = f"https://www.dongchedi.com/community/{config.series_id}" if config.series_id else ""
    score_url = f"https://www.dongchedi.com/auto/series/score/{config.series_id}-x-x-x-x-x" if config.series_id else ""
    return f"""---
title: "{brand} {series_name} 车型总览"
tags:
  - 汽车
  - 品牌库
  - {brand}
  - {series_name}
created: {today}
updated: {today}
update_month: "{update_month}"
---

# {brand} {series_name} 车型总览

- 固定链接: [车型首页]({series_home_url}) · [参数配置]({params_url}) · [车友圈]({community_url}) · [懂车分(口碑)]({score_url})
- 品牌: {brand}
- 车型: {series_name}
- 最近更新月份: {update_month}

## 当前款型

{current_links}

## 月度归档

- [[00-本月更新摘要]]
"""


def format_change_callout(changes: list[ChangeRecord], date: str = "") -> str:
    """Format an Obsidian callout block for detected changes."""
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    lines = [f"> [!tip] 数据更新 {date}"]
    for c in changes:
        if c.change_type == "price_change":
            lines.append(f"> - 价格: {c.old_value} → {c.new_value}")
        elif c.change_type == "param_added":
            lines.append(f"> - 新增参数: {c.field}")
        elif c.change_type == "param_removed":
            lines.append(f"> - 移除参数: {c.field}")
        elif c.change_type == "param_changed":
            lines.append(f"> - {c.field}: {c.old_value} → {c.new_value}")
        elif c.change_type == "discontinued":
            lines.append(f"> - 该配置已停售")
        else:
            lines.append(f"> - {c.description}")

    return "\n".join(lines)



def format_discontinued_callout() -> str:
    """Format a callout for a discontinued configuration."""
    date = datetime.now().strftime("%Y-%m-%d")
    return f"""> [!warning] 停售提醒 {date}
> 该配置已从懂车帝在售列表中移除，可能已停产或更新换代。"""



def format_competitor_index(
    target: CarModel,
    competitors: dict[str, list[CarModel]],
    config_notes: dict[str, list[str]] | None = None,
) -> str:
    """Format a competitor analysis index note.

    Args:
        target: The target car model
        competitors: Dict with keys "A", "B", "C" mapping to lists of CarModel
        config_notes: Optional dict mapping series_name to list of note filenames for wikilinks
    """
    today = datetime.now().strftime("%Y-%m-%d")

    frontmatter = f"""---
title: "{target.name} 竞品分析"
tags:
  - 汽车
  - 竞品分析
  - {target.name}
created: {today}
updated: {today}
---"""

    body = f"""{frontmatter}

# {target.name} 竞品分析

- 价格区间: {target.price_range}
- 级别: {target.level}
- 能源类型: {target.energy_type}
"""

    tier_labels = {
        "A": ("A 类竞品（直接竞品）", "价格±2万 + 同级别 + 同能源类型"),
        "B": ("B 类竞品（间接竞品）", "部分维度重叠"),
        "C": ("C 类竞品（潜在竞品）", "跨维度但目标用户重叠"),
    }

    for tier in ["A", "B", "C"]:
        models = competitors.get(tier, [])
        label, desc = tier_labels[tier]

        body += f"""
## {label}

> {desc}

| 车型 | 价格区间 | 级别 | 能源类型 | 配置笔记 |
|------|---------|------|---------|---------|
"""
        for m in models:
            links = ""
            if config_notes and m.name in config_notes:
                link_list = [f"[[{n}]]" for n in config_notes[m.name][:3]]
                links = " ".join(link_list)
                if len(config_notes[m.name]) > 3:
                    links += " ..."
            body += f"| {m.name} | {m.price_range} | {m.level} | {m.energy_type} | {links} |\n"

    if config_notes and target.name in config_notes:
        body += f"""
## 本车配置

"""
        for note in config_notes[target.name]:
            body += f"- [[{note}]]\n"

    return body



def format_changelog(
    date: str,
    changes: list[ChangeRecord],
    stats: dict | None = None,
) -> str:
    """Format an update changelog note."""
    frontmatter = f"""---
title: "汽车配置更新日志 {date}"
tags:
  - 汽车
  - 更新日志
  - 懂车帝
created: {date}
---"""

    body = f"""{frontmatter}

# 汽车配置更新日志 {date}

"""

    if stats:
        body += f"""## 统计

| 项目 | 数量 |
|------|------|
| 总配置数 | {stats.get('total', 0)} |
| 成功抓取 | {stats.get('success', 0)} |
| 新增配置 | {stats.get('new', 0)} |
| 更新配置 | {stats.get('updated', 0)} |
| 未变化 | {stats.get('unchanged', 0)} |
| 停售配置 | {stats.get('discontinued', 0)} |

"""

    if changes:
        price_changes = [c for c in changes if c.change_type == "price_change"]
        new_configs = [c for c in changes if c.change_type == "new_config"]
        discontinued = [c for c in changes if c.change_type == "discontinued"]
        param_changes = [c for c in changes if c.change_type.startswith("param_")]

        if price_changes:
            body += "## 价格变动\n\n"
            for c in price_changes:
                note_name = c.note_path.rsplit("/", 1)[-1].replace(".md", "")
                body += f"- [[{note_name}]]: {c.old_value} → {c.new_value}\n"
            body += "\n"

        if new_configs:
            body += "## 新增配置\n\n"
            for c in new_configs:
                note_name = c.note_path.rsplit("/", 1)[-1].replace(".md", "")
                body += f"- [[{note_name}]]\n"
            body += "\n"

        if discontinued:
            body += "## 停售配置\n\n"
            for c in discontinued:
                note_name = c.note_path.rsplit("/", 1)[-1].replace(".md", "")
                body += f"- [[{note_name}]]\n"
            body += "\n"

        if param_changes:
            body += f"## 参数变更 ({len(param_changes)} 项)\n\n"
            for c in param_changes[:20]:
                note_name = c.note_path.rsplit("/", 1)[-1].replace(".md", "")
                body += f"- [[{note_name}]]: {c.description}\n"
            if len(param_changes) > 20:
                body += f"- ... 及其他 {len(param_changes) - 20} 项变更\n"
            body += "\n"
    else:
        body += "*本次更新无变化*\n"

    return body



def config_note_path(config: CarConfig) -> str:
    """Backward-compatible alias for the current-state note path."""
    return config_current_note_path(config)



def config_note_name(config: CarConfig) -> str:
    """Backward-compatible alias for the current-state note display name."""
    return config_current_note_name(config)
