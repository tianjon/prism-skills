from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path
from pathlib import PurePosixPath
from dataclasses import dataclass
from typing import Mapping, Sequence


IMAGE_LINK_RE = re.compile(r"!\[[^\]]*\]\((images/[^)]+)\)")


def rewrite_markdown_image_embeds(text: str) -> tuple[str, list[str]]:
    image_names: list[str] = []

    def replace(match: re.Match[str]) -> str:
        relative_path = match.group(1).strip()
        image_name = relative_path.split("images/", 1)[1]
        image_names.append(image_name)
        return f"![[images/{image_name}]]"

    rewritten = IMAGE_LINK_RE.sub(replace, text)
    return rewritten, image_names


def copy_referenced_assets(assets_dir: Path | None, asset_names: Sequence[str], target_images_dir: Path) -> list[Path]:
    if not asset_names:
        return []
    if assets_dir is None:
        raise FileNotFoundError("Asset directory is required when image references are present")

    assets_dir = Path(assets_dir)
    target_images_dir = Path(target_images_dir)
    target_images_dir.mkdir(parents=True, exist_ok=True)

    copied: list[Path] = []
    for asset_name in asset_names:
        source_path = assets_dir / asset_name
        if not source_path.exists():
            raise FileNotFoundError(f"Referenced asset not found: {source_path}")
        target_path = target_images_dir / asset_name
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target_path)
        copied.append(target_path)
    return copied


def copy_all_assets(assets_dir: Path, target_images_dir: Path) -> list[Path]:
    assets_dir = Path(assets_dir)
    target_images_dir = Path(target_images_dir)
    if not assets_dir.exists():
        raise FileNotFoundError(f"Asset directory does not exist: {assets_dir}")

    copied: list[Path] = []
    for source_path in sorted(
        [path for path in assets_dir.rglob("*") if path.is_file()],
        key=lambda path: path.relative_to(assets_dir).as_posix(),
    ):
        rel = source_path.relative_to(assets_dir)
        target_path = target_images_dir / rel
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target_path)
        copied.append(target_path)
    return copied


@dataclass(frozen=True)
class ImportTarget:
    source_file: str
    target_note_path: str
    target_images_dir: str


def plan_import_targets(entries: Sequence[Mapping[str, object]], *, target_root: str) -> dict[str, ImportTarget]:
    source_files = [str(entry["source_file"]) for entry in entries]

    counts: dict[tuple[str, str], int] = {}
    for source_file in source_files:
        path = PurePosixPath(source_file)
        key = (path.parent.as_posix(), path.stem)
        counts[key] = counts.get(key, 0) + 1

    prefix = PurePosixPath(target_root) if target_root else PurePosixPath(".")
    planned: dict[str, ImportTarget] = {}
    for source_file in source_files:
        path = PurePosixPath(source_file)
        stem = path.stem
        key = (path.parent.as_posix(), stem)

        if counts[key] == 1:
            dir_name = stem
        else:
            ext = path.suffix.lstrip(".").lower() or "file"
            dir_name = f"{stem}__{ext}"

        note_dir = prefix / path.parent / dir_name
        note_path = note_dir / f"{stem}.md"
        images_dir = note_dir / "images"
        planned[source_file] = ImportTarget(
            source_file=source_file,
            target_note_path=note_path.as_posix(),
            target_images_dir=images_dir.as_posix(),
        )

    return planned


def render_frontmatter(frontmatter: Mapping[str, object]) -> str:
    lines = ["---"]
    for key, value in frontmatter.items():
        if isinstance(value, Mapping):
            raise TypeError("Nested mappings are not supported in frontmatter")
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {json.dumps(item, ensure_ascii=False)}")
            continue
        if isinstance(value, bool):
            rendered = "true" if value else "false"
        elif value is None:
            rendered = "null"
        elif isinstance(value, (int, float)):
            rendered = str(value)
        else:
            rendered = json.dumps(value, ensure_ascii=False)
        lines.append(f"{key}: {rendered}")
    lines.append("---")
    return "\n".join(lines)


def build_note_content(
    body: str,
    *,
    frontmatter: Mapping[str, object] | None = None,
    preamble: str | None = None,
    related_notes: Sequence[str] | None = None,
) -> str:
    parts: list[str] = []
    if frontmatter:
        parts.append(render_frontmatter(frontmatter))
    if preamble:
        parts.append(preamble.rstrip())
    parts.append(body.rstrip())
    if related_notes:
        parts.append("## Related Notes")
        parts.extend(f"- [[{note}]]" for note in related_notes)
    return "\n\n".join(part for part in parts if part).rstrip() + "\n"


def obsidian_escape_content(text: str) -> str:
    return text.replace("\\", "\\\\").replace("\n", "\\n")


def chunk_text(text: str, chunk_size: int) -> list[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)] or [""]


def run_obsidian_cmd(command: str, *params: str, vault: str = "", timeout: int = 60) -> subprocess.CompletedProcess:
    cmd = ["obsidian", command]
    if vault:
        cmd.append(f"vault={vault}")
    cmd.extend(params)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def write_obsidian_note(
    *,
    target_path: str,
    content: str,
    vault: str = "",
    chunk_size: int = 3000,
) -> None:
    chunks = chunk_text(content, chunk_size)
    create = run_obsidian_cmd(
        "create",
        f"path={target_path}",
        f"content={obsidian_escape_content(chunks[0])}",
        "overwrite",
        "silent",
        vault=vault,
        timeout=90,
    )
    if create.returncode != 0:
        raise RuntimeError(create.stderr or create.stdout or f"Failed to create {target_path}")

    for chunk in chunks[1:]:
        append = run_obsidian_cmd(
            "append",
            f"path={target_path}",
            f"content={obsidian_escape_content(chunk)}",
            "inline",
            vault=vault,
            timeout=90,
        )
        if append.returncode != 0:
            raise RuntimeError(append.stderr or append.stdout or f"Failed to append {target_path}")

    # Read-back verification is required because large note writes can be flaky.
    read = run_obsidian_cmd(
        "read",
        f"path={target_path}",
        vault=vault,
        timeout=90,
    )
    if read.returncode != 0:
        raise RuntimeError(read.stderr or read.stdout or f"Failed to read back {target_path}")

    expected = content.replace("\r\n", "\n").rstrip("\n")
    actual = (read.stdout or "").replace("\r\n", "\n").rstrip("\n")
    if actual != expected:
        raise RuntimeError(f"Obsidian read-back mismatch for {target_path}")


def resolve_vault_path(vault: str = "") -> Path:
    result = run_obsidian_cmd("vault", "info=path", vault=vault, timeout=30)
    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout or "Failed to resolve vault path")
    path = result.stdout.strip()
    if not path:
        raise RuntimeError("Obsidian vault path is empty")
    return Path(path)


def verify_note_assets(note_path: Path, asset_names: Sequence[str], images_dir: Path) -> None:
    note_text = Path(note_path).read_text(encoding="utf-8")
    for asset_name in asset_names:
        if f"![[images/{asset_name}]]" not in note_text:
            raise RuntimeError(f"Rewritten asset reference missing in note: {asset_name}")
        if not (images_dir / asset_name).exists():
            raise RuntimeError(f"Copied asset missing from vault: {images_dir / asset_name}")
