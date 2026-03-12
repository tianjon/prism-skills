from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from pathlib import PurePosixPath
from typing import Iterable, Sequence


DEFAULT_DISCOVERABLE_EXTENSIONS = (".pdf", ".png", ".jpg", ".jpeg")


@dataclass(frozen=True)
class ConversionBatch:
    source_path: Path
    relative_parent: Path
    files: tuple[Path, ...]


@dataclass(frozen=True)
class ManifestEntry:
    source_file: str
    source_abs_path: str
    relative_parent: str
    output_root: str
    markdown_path: str
    assets_dir: str | None
    has_assets: bool
    target_note_rel_path: str
    target_images_rel_path: str


def plan_relative_targets(source_files: Sequence[str]) -> dict[str, tuple[str, str]]:
    """Plan deterministic, collision-resistant relative targets for Obsidian import.

    The planned paths are relative to an eventual vault subpath (target root).
    """

    counts: dict[tuple[str, str], int] = {}
    for source_file in source_files:
        path = PurePosixPath(source_file)
        key = (path.parent.as_posix(), path.stem)
        counts[key] = counts.get(key, 0) + 1

    planned: dict[str, tuple[str, str]] = {}
    for source_file in source_files:
        path = PurePosixPath(source_file)
        stem = path.stem
        key = (path.parent.as_posix(), stem)

        if counts[key] == 1:
            dir_name = stem
        else:
            ext = path.suffix.lstrip(".").lower() or "file"
            dir_name = f"{stem}__{ext}"

        note_dir = path.parent / dir_name
        note_path = note_dir / f"{stem}.md"
        images_dir = note_dir / "images"
        planned[source_file] = (note_path.as_posix(), images_dir.as_posix())

    return planned


def normalize_extensions(extensions: Iterable[str]) -> tuple[str, ...]:
    normalized = []
    for ext in extensions:
        item = ext.strip().lower()
        if not item:
            continue
        if not item.startswith("."):
            item = f".{item}"
        normalized.append(item)
    if not normalized:
        raise ValueError("At least one discoverable extension is required")
    return tuple(dict.fromkeys(normalized))


def discover_supported_inputs(
    input_path: Path,
    extensions: Iterable[str] = DEFAULT_DISCOVERABLE_EXTENSIONS,
) -> list[Path]:
    input_path = Path(input_path).resolve()
    allowed = set(normalize_extensions(extensions))

    if not input_path.exists():
        raise FileNotFoundError(f"Input path does not exist: {input_path}")

    if input_path.is_file():
        if input_path.suffix.lower() not in allowed:
            raise ValueError(f"Unsupported file type: {input_path.suffix}")
        return [input_path]

    files = [
        path
        for path in input_path.rglob("*")
        if path.is_file() and path.suffix.lower() in allowed
    ]
    return sorted(files, key=lambda path: path.relative_to(input_path).as_posix())


def build_conversion_batches(input_path: Path, discovered_files: Sequence[Path]) -> list[ConversionBatch]:
    input_path = Path(input_path).resolve()
    files = tuple(Path(path).resolve() for path in discovered_files)

    if not files:
        return []

    if input_path.is_file():
        return [
            ConversionBatch(
                source_path=input_path,
                relative_parent=Path("."),
                files=(input_path,),
            )
        ]

    grouped: dict[Path, list[Path]] = {}
    for file_path in files:
        relative_parent = file_path.parent.relative_to(input_path)
        key = relative_parent if relative_parent.parts else Path(".")
        grouped.setdefault(key, []).append(file_path)

    batches = []
    for relative_parent in sorted(grouped, key=lambda path: path.as_posix()):
        source_dir = input_path if relative_parent == Path(".") else input_path / relative_parent
        batches.append(
            ConversionBatch(
                source_path=source_dir,
                relative_parent=relative_parent,
                files=tuple(sorted(grouped[relative_parent], key=lambda path: path.name)),
            )
        )
    return batches


def batch_output_root(output_root: Path, relative_parent: Path) -> Path:
    output_root = Path(output_root).resolve()
    return output_root if relative_parent == Path(".") else output_root / relative_parent


def resolve_generated_markdown(batch_output: Path, source_file: Path) -> Path:
    expected = batch_output / source_file.stem / "auto" / f"{source_file.stem}.md"
    if expected.exists():
        return expected

    candidates = [
        path
        for path in batch_output.rglob("*.md")
        if path.stem == source_file.stem and path.parent.name == "auto"
    ]
    if not candidates:
        raise FileNotFoundError(f"Converted markdown not found for {source_file}")
    if len(candidates) > 1:
        raise RuntimeError(f"Ambiguous converted markdown for {source_file}: {candidates}")
    return candidates[0]


def build_manifest_entries(
    input_path: Path,
    output_root: Path,
    discovered_files: Sequence[Path],
) -> list[ManifestEntry]:
    input_path = Path(input_path).resolve()
    output_root = Path(output_root).resolve()
    entries: list[ManifestEntry] = []

    source_file_rels = [
        (path.name if input_path.is_file() else path.relative_to(input_path).as_posix())
        for path in discovered_files
    ]
    planned_targets = plan_relative_targets(source_file_rels)

    for batch in build_conversion_batches(input_path, discovered_files):
        current_output_root = batch_output_root(output_root, batch.relative_parent)
        for source_file in batch.files:
            markdown_path = resolve_generated_markdown(current_output_root, source_file)
            assets_dir = markdown_path.parent / "images"
            source_file_rel = (
                source_file.name
                if input_path.is_file()
                else source_file.relative_to(input_path).as_posix()
            )
            target_note_rel_path, target_images_rel_path = planned_targets[source_file_rel]
            entries.append(
                ManifestEntry(
                    source_file=source_file_rel,
                    source_abs_path=str(source_file),
                    relative_parent=batch.relative_parent.as_posix(),
                    output_root=str(current_output_root),
                    markdown_path=str(markdown_path),
                    assets_dir=str(assets_dir) if assets_dir.exists() else None,
                    has_assets=assets_dir.exists(),
                    target_note_rel_path=target_note_rel_path,
                    target_images_rel_path=target_images_rel_path,
                )
            )
    return entries


def save_manifest(
    manifest_path: Path,
    *,
    input_path: Path,
    output_root: Path,
    extensions: Iterable[str],
    entries: Sequence[ManifestEntry],
) -> Path:
    manifest_path = Path(manifest_path).resolve()
    payload = {
        "version": 1,
        "input_path": str(Path(input_path).resolve()),
        "output_root": str(Path(output_root).resolve()),
        "extensions": list(normalize_extensions(extensions)),
        "entries": [asdict(entry) for entry in entries],
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest_path


def load_manifest(manifest_path: Path) -> dict:
    return json.loads(Path(manifest_path).read_text(encoding="utf-8"))
