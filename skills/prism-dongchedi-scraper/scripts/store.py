"""Store scraped data to Obsidian vault.

Run: python3 scripts/store.py [--competitors] [--changelog] [--vault <name>]

Input: tmp/all-configs-with-params.json, tmp/changes.json (optional), tmp/competitors.json (optional)
Output: Notes created/updated in Obsidian vault
"""
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

module_file = globals().get("__file__")
SKILL_DIR = Path(module_file).resolve().parent.parent if module_file else Path.cwd().resolve()
TMP_DIR = Path(os.environ.get("DONGCHEDI_TMP_DIR", str(SKILL_DIR / "tmp"))).resolve()

sys.path.insert(0, str(SKILL_DIR))
from lib.markdown import (
    competitor_index_note_path,
    config_current_note_name,
    config_current_note_path,
    config_snapshot_note_path,
    format_changelog,
    format_competitor_index,
    format_config_note,
    format_discontinued_callout,
    format_series_overview_note,
    monthly_changelog_note_path,
    series_overview_note_path,
)
from lib.dongchedi import infer_brand_name
from lib.types import CarConfig, CarModel, ChangeRecord, ParamItem



def obsidian_cmd(command: str, *params: str, vault: str = "", timeout: int = 30) -> subprocess.CompletedProcess:
    cmd = ["obsidian", command]
    if vault:
        cmd.append(f'vault={vault}')
    cmd.extend(params)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)



def obsidian_create(path: str, content: str, vault: str = "") -> bool:
    for attempt in range(3):
        try:
            result = obsidian_cmd("create", f"path={path}", f"content={content}", "silent", "overwrite", vault=vault, timeout=90)
            if result.returncode != 0:
                continue
            verify = obsidian_cmd("read", f"path={path}", vault=vault, timeout=30)
            if verify.returncode == 0:
                return True
        except Exception as e:
            if attempt == 2:
                print(f"  Error creating {path}: {e}")
    return False


def obsidian_read(path: str, vault: str = "") -> str | None:
    try:
        result = obsidian_cmd("read", f"path={path}", vault=vault, timeout=30)
        if result.returncode != 0:
            return None
        return result.stdout
    except Exception:
        return None



def build_config_note_targets(config: CarConfig, update_month: str) -> dict[str, str]:
    current_path = config_current_note_path(config)
    snapshot_path = config_snapshot_note_path(config, update_month)
    overview_path = series_overview_note_path(config)
    return {
        "current_path": current_path,
        "current_name": config_current_note_name(config),
        "snapshot_path": snapshot_path,
        "overview_path": overview_path,
    }



def _note_link_target(path: str) -> str:
    return path[:-3] if path.endswith(".md") else path


def _ensure_frontmatter_list_tag(markdown: str, tag: str) -> str:
    """Ensure YAML frontmatter contains a list tag under `tags:`."""
    if not markdown.startswith("---\n"):
        return markdown

    end = markdown.find("\n---\n", 4)
    if end == -1:
        return markdown

    frontmatter = markdown[: end + 5]
    body = markdown[end + 5 :]

    lines = frontmatter.splitlines(keepends=True)

    # Locate the tag block in line space.
    # frontmatter is small; keep this straightforward and robust.
    tag_line_i = None
    for i, line in enumerate(lines):
        if line.strip() == "tags:":
            tag_line_i = i
            break
    if tag_line_i is None:
        return markdown

    # Collect existing tags.
    existing: set[str] = set()
    insert_at = tag_line_i + 1
    for j in range(tag_line_i + 1, len(lines)):
        stripped = lines[j].rstrip("\n")
        if stripped.startswith("  - "):
            existing.add(stripped[4:].strip())
            insert_at = j + 1
            continue
        # Stop at first non-tag line inside frontmatter.
        if stripped.startswith("---") or stripped and not stripped.startswith(" "):
            break
        if not stripped:
            # blank line inside frontmatter: still stop tags block
            break

    if tag in existing:
        return markdown

    lines.insert(insert_at, f"  - {tag}\n")
    new_frontmatter = "".join(lines)
    return new_frontmatter + body


def _ensure_discontinued_callout(markdown: str) -> str:
    callout = format_discontinued_callout().strip()
    if "停售提醒" in markdown or callout in markdown:
        return markdown

    if markdown.startswith("---\n"):
        end = markdown.find("\n---\n", 4)
        if end != -1:
            head = markdown[: end + 5]
            rest = markdown[end + 5 :].lstrip("\n")
            return f"{head}\n{callout}\n\n{rest}"

    return f"{callout}\n\n{markdown.lstrip()}"


def _rewrite_discontinued_note(markdown: str) -> str:
    updated = _ensure_frontmatter_list_tag(markdown, "停售")
    updated = _ensure_discontinued_callout(updated)
    return updated





def main() -> None:
    parser = argparse.ArgumentParser(description="Store scraped data to Obsidian")
    parser.add_argument("--vault", default="", help="Optional Obsidian vault name")
    parser.add_argument("--competitors", action="store_true", help="Generate competitor index notes")
    parser.add_argument("--changelog", action="store_true", help="Generate changelog note")
    args = parser.parse_args()

    configs_path = TMP_DIR / "all-configs-with-params.json"
    if not configs_path.exists():
        print("ERROR: tmp/all-configs-with-params.json not found")
        sys.exit(1)

    update_month = datetime.now().strftime("%Y-%m")
    configs_raw = json.loads(configs_path.read_text("utf-8"))
    changes_data = {}
    changes_path = TMP_DIR / "changes.json"
    if changes_path.exists():
        changes_data = json.loads(changes_path.read_text("utf-8"))

    changes_by_path = {}
    for item in changes_data.get("changes", []):
        note_path = item.get("note_path", "")
        changes_by_path.setdefault(note_path, []).append(ChangeRecord(**item))

    success = 0
    errors = 0
    config_notes_map: dict[str, list[str]] = {}
    series_overview_map: dict[str, dict] = {}

    print(f"Storing {len(configs_raw)} config notes to Obsidian...")
    for i, config_dict in enumerate(configs_raw):
        config_fields = {k: v for k, v in config_dict.items() if k in CarConfig.model_fields}
        config = CarConfig(**config_fields)

        params = [ParamItem(**p) for p in config_dict.get("params", [])]
        if config_dict.get("params_error") and not params:
            errors += 1
            continue

        targets = build_config_note_targets(config, update_month)
        current_path = targets["current_path"]
        snapshot_path = targets["snapshot_path"]
        current_name = targets["current_name"]
        overview_path = targets["overview_path"]

        note_changes = changes_by_path.get(current_path, [])
        content = format_config_note(config, params, note_changes if note_changes else None)

        current_ok = obsidian_create(current_path, content, vault=args.vault)
        snapshot_ok = obsidian_create(snapshot_path, content, vault=args.vault)

        if current_ok and snapshot_ok:
            success += 1
            config_notes_map.setdefault(config.series_name, []).append(_note_link_target(current_path))
            bucket = series_overview_map.setdefault(
                overview_path,
                {"config": config, "current_notes": [], "month_summary_path": monthly_changelog_note_path(config, update_month)},
            )
            bucket["current_notes"].append(current_name)
        else:
            errors += 1

        if (i + 1) % 50 == 0:
            print(f"  [{i+1}/{len(configs_raw)}] stored ({success} ok, {errors} err)")

    for overview_path, payload in series_overview_map.items():
        overview_content = format_series_overview_note(
            payload["config"],
            payload["current_notes"],
            update_month,
        )
        obsidian_create(overview_path, overview_content, vault=args.vault)
        series_changes = [
            ChangeRecord(**item)
            for item in changes_data.get("changes", [])
            if item.get("note_path", "").startswith(overview_path.rsplit("/", 1)[0] + "/")
        ]
        if args.changelog:
            month_stats = {
                "total": len(payload["current_notes"]),
                "success": len(payload["current_notes"]),
                "new": len([c for c in series_changes if c.change_type == "new_config"]),
                "updated": len([c for c in series_changes if c.change_type in {"price_change", "param_added", "param_removed", "param_changed"}]),
                "unchanged": max(len(payload["current_notes"]) - len({c.note_path for c in series_changes}), 0),
                "discontinued": len([c for c in series_changes if c.change_type == "discontinued"]),
            }
            month_summary_content = format_changelog(update_month, series_changes, month_stats)
        else:
            month_summary_content = f"# {payload['config'].brand or payload['config'].brand_name} {payload['config'].series_name} {update_month} 更新摘要\n\n"
            month_summary_content += "\n".join(f"- [[{name}]]" for name in sorted(payload["current_notes"])) or "- 暂无款型"
        obsidian_create(payload["month_summary_path"], month_summary_content, vault=args.vault)

    print(f"\nConfig notes: {success} created, {errors} errors")

    discontinued = [c for c in changes_data.get("changes", []) if c.get("change_type") == "discontinued"]
    if discontinued:
        print(f"\nRewriting {len(discontinued)} discontinued configs (overwrite mode)...")
        for item in discontinued:
            note_path = item.get("note_path", "")
            if not note_path:
                continue
            existing = obsidian_read(note_path, vault=args.vault)
            if not existing:
                continue
            rewritten = _rewrite_discontinued_note(existing)
            obsidian_create(note_path, rewritten, vault=args.vault)

    if args.competitors:
        competitors_path = TMP_DIR / "competitors.json"
        if competitors_path.exists():
            competitors_data = json.loads(competitors_path.read_text("utf-8"))
            print(f"\nCreating {len(competitors_data)} competitor index notes...")
            for model_name, data in competitors_data.items():
                target = CarModel(**data["target"])
                competitors = {tier: [CarModel(**m) for m in models] for tier, models in data["competitors"].items()}
                content = format_competitor_index(target, competitors, config_notes_map)
                note_candidates = config_notes_map.get(target.name, [])
                if note_candidates:
                    parts = note_candidates[0].split("/")
                    brand = parts[2] if len(parts) > 2 else infer_brand_name(target.name)
                else:
                    brand = infer_brand_name(target.name)
                path = competitor_index_note_path(target, brand=brand, update_month=update_month)
                if obsidian_create(path, content, vault=args.vault):
                    print(f"  Created {path}")
                else:
                    print(f"  Failed {path}")
        else:
            print("Warning: tmp/competitors.json not found, skipping competitor notes")

    if args.changelog:
        print("\nChangelog: 已按品牌/车型/月写入各车型的月度摘要")

    print("\nDone.")


if __name__ == "__main__":
    main()
