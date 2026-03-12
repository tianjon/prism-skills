"""Compare new scrape data with existing Obsidian notes.

Run: python3 scripts/diff.py [--vault <name>] (no browser needed)

Input: tmp/all-configs-with-params.json
Output: tmp/changes.json
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

module_file = globals().get("__file__")
SKILL_DIR = Path(module_file).resolve().parent.parent if module_file else Path.cwd().resolve()

sys.path.insert(0, str(SKILL_DIR))
from lib.markdown import config_note_path
from lib.types import CarConfig, ChangeRecord


def resolve_tmp_dir() -> Path:
    default = SKILL_DIR / "tmp"
    return Path(os.environ.get("DONGCHEDI_TMP_DIR", str(default))).resolve()


def obsidian_cmd(command: str, *params: str, vault: str = "", timeout: int = 30) -> subprocess.CompletedProcess:
    cmd = ["obsidian", command]
    if vault:
        cmd.append(f'vault={vault}')
    cmd.extend(params)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def obsidian_read_property(path: str, prop: str, vault: str = "") -> str:
    try:
        result = obsidian_cmd("property:read", f"name={prop}", f"path={path}", vault=vault, timeout=10)
        return result.stdout.strip() if result.returncode == 0 else ""
    except Exception:
        return ""


def obsidian_note_exists(path: str, vault: str = "") -> bool:
    try:
        result = obsidian_cmd("read", f"path={path}", vault=vault, timeout=10)
        return result.returncode == 0
    except Exception:
        return False


def obsidian_list_folder_notes(folder: str, vault: str = "") -> list[str]:
    try:
        result = obsidian_cmd("files", f"folder={folder}", "ext=md", vault=vault, timeout=30)
        if result.returncode != 0:
            return []
        return [line.strip() for line in result.stdout.splitlines() if line.strip().endswith('.md')]
    except Exception:
        return []


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare scraped configs with Obsidian notes")
    parser.add_argument("--vault", default="", help="Optional Obsidian vault name")
    parser.add_argument("--skip-discontinued", action="store_true", help="Skip discontinued config detection")
    args = parser.parse_args()

    tmp_dir = resolve_tmp_dir()
    configs_path = tmp_dir / "all-configs-with-params.json"
    if not configs_path.exists():
        print("ERROR: tmp/all-configs-with-params.json not found")
        sys.exit(1)

    configs = json.loads(configs_path.read_text("utf-8"))
    changes = []
    new_configs = []
    note_paths = []

    print(f"Checking {len(configs)} configs against Obsidian...")

    for i, config_dict in enumerate(configs):
        config = CarConfig(**{k: v for k, v in config_dict.items() if k in CarConfig.model_fields})
        note_path = config_note_path(config)
        note_paths.append(note_path)

        if obsidian_note_exists(note_path, vault=args.vault):
            old_price = obsidian_read_property(note_path, "price", vault=args.vault)
            if old_price and old_price != config.price and config.price:
                changes.append(ChangeRecord(
                    note_path=note_path,
                    change_type="price_change",
                    field="price",
                    old_value=old_price,
                    new_value=config.price,
                    description=f"价格变动: {old_price} → {config.price}",
                ).model_dump())
        else:
            changes.append(ChangeRecord(
                note_path=note_path,
                change_type="new_config",
                description=f"新增配置: {config.series_name} {config.car_name}",
            ).model_dump())
            new_configs.append(note_path)

        if (i + 1) % 50 == 0:
            print(f"  [{i+1}/{len(configs)}] checked")

    discontinued_count = 0
    if not args.skip_discontinued and note_paths:
        print("\nChecking for discontinued configs...")
        folders = sorted({path.rsplit("/", 1)[0] for path in note_paths})
        existing_notes = set()
        for folder in folders:
            existing_notes.update(obsidian_list_folder_notes(folder, vault=args.vault))
        new_note_paths = set(note_paths)
        for note in sorted(existing_notes - new_note_paths):
            changes.append(ChangeRecord(
                note_path=note,
                change_type="discontinued",
                description=f"可能停售: {note}",
            ).model_dump())
            discontinued_count += 1

    output = {
        "changes": changes,
        "stats": {
            "total": len(configs),
            "new": len(new_configs),
            "price_changes": len([c for c in changes if c.get("change_type") == "price_change"]),
            "discontinued": discontinued_count,
        },
    }
    (tmp_dir / "changes.json").write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\nResults:")
    print(f"  New configs: {len(new_configs)}")
    print(f"  Price changes: {output['stats']['price_changes']}")
    print(f"  Discontinued: {output['stats']['discontinued']}")
    print("  Saved to tmp/changes.json")


if __name__ == "__main__":
    main()
