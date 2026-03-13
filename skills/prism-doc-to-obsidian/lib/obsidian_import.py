from __future__ import annotations

import json
import hashlib
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from pathlib import PurePosixPath
from typing import Iterable, Mapping, Sequence

from lib.conversion import plan_relative_targets


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


def extract_markdown_image_asset_names(markdown_path: Path, *, encoding: str = "utf-8") -> list[str]:
    """Extract referenced MinerU image asset names without loading the full file into memory."""
    markdown_path = Path(markdown_path)
    asset_names: list[str] = []
    with markdown_path.open("r", encoding=encoding, errors="replace") as handle:
        for line in handle:
            for match in IMAGE_LINK_RE.finditer(line):
                relative_path = match.group(1).strip()
                asset_names.append(relative_path.split("images/", 1)[1])
    return asset_names


def iter_rewritten_markdown_image_embeds(markdown_path: Path, *, encoding: str = "utf-8") -> Iterable[str]:
    """Streaming alternative to `rewrite_markdown_image_embeds()` for large documents."""

    def replace(match: re.Match[str]) -> str:
        relative_path = match.group(1).strip()
        image_name = relative_path.split("images/", 1)[1]
        return f"![[images/{image_name}]]"

    markdown_path = Path(markdown_path)
    with markdown_path.open("r", encoding=encoding, errors="replace") as handle:
        for line in handle:
            yield IMAGE_LINK_RE.sub(replace, line)


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


def join_target_root(target_root: str, relative_path: str) -> str:
    root = PurePosixPath(target_root) if target_root else PurePosixPath(".")
    rel = PurePosixPath(relative_path)
    return (root / rel).as_posix()


def plan_import_targets(entries: Sequence[Mapping[str, object]], *, target_root: str) -> dict[str, ImportTarget]:
    source_files = [str(entry["source_file"]) for entry in entries]
    relative_targets = plan_relative_targets(source_files)
    planned: dict[str, ImportTarget] = {}
    for source_file in source_files:
        note_path, images_dir = relative_targets[source_file]
        note_path = join_target_root(target_root, note_path)
        images_dir = join_target_root(target_root, images_dir)
        planned[source_file] = ImportTarget(
            source_file=source_file,
            target_note_path=note_path,
            target_images_dir=images_dir,
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


def iter_text_chunks(parts: Iterable[str], *, chunk_size: int) -> Iterable[str]:
    """Chunk streaming text into ~chunk_size strings without holding the full content in memory."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    buf = ""
    for part in parts:
        if not part:
            continue
        buf += part
        while len(buf) >= chunk_size:
            yield buf[:chunk_size]
            buf = buf[chunk_size:]
    if buf:
        yield buf
    else:
        # Keep the create call deterministic even for empty content.
        yield ""


def iter_trim_trailing_whitespace(parts: Iterable[str]) -> Iterable[str]:
    """Like `"".join(parts).rstrip()` but streaming and bounded-memory."""
    pending = ""
    for part in parts:
        if not part:
            continue
        combined = pending + part
        last_non_ws = -1
        for idx in range(len(combined) - 1, -1, -1):
            if not combined[idx].isspace():
                last_non_ws = idx
                break
        if last_non_ws == -1:
            pending = combined
            continue
        yield combined[: last_non_ws + 1]
        pending = combined[last_non_ws + 1 :]
    # Drop pending suffix (equivalent to rstrip at EOF).


def iter_note_content(
    body_parts: Iterable[str],
    *,
    frontmatter: Mapping[str, object] | None = None,
    preamble: str | None = None,
    related_notes: Sequence[str] | None = None,
) -> Iterable[str]:
    """Streaming alternative to `build_note_content()`."""
    if frontmatter:
        yield render_frontmatter(frontmatter)
        yield "\n\n"
    if preamble:
        yield preamble.rstrip()
        yield "\n\n"

    for part in iter_trim_trailing_whitespace(body_parts):
        yield part

    if related_notes:
        yield "\n\n## Related Notes\n"
        for note in related_notes:
            yield f"- [[{note}]]\n"

    yield "\n"


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


def _normalize_newlines_bytes(data: bytes, *, carry: bytes) -> tuple[bytes, bytes]:
    combined = carry + data
    if not combined:
        return b"", b""
    if combined.endswith(b"\r"):
        return combined[:-1].replace(b"\r\n", b"\n"), b"\r"
    return combined.replace(b"\r\n", b"\n"), b""


def sha256_file_normalized_newlines(path: Path) -> str:
    digest = hashlib.sha256()
    carry = b""
    with Path(path).open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            normalized, carry = _normalize_newlines_bytes(chunk, carry=carry)
            if normalized:
                digest.update(normalized)
    if carry:
        digest.update(carry)
    return digest.hexdigest()


def write_obsidian_note_iter(
    *,
    target_path: str,
    content_parts: Iterable[str],
    vault: str = "",
    chunk_size: int = 3000,
    vault_root: Path | None = None,
    verify: bool = True,
) -> None:
    """Write a note from streaming content, avoiding large in-memory buffers.

    If `vault_root` is provided, verification reads the note from disk and compares SHA256
    (with CRLF normalized to LF), instead of using `obsidian read` which can be memory-heavy
    on large notes.
    """
    expected_hasher = hashlib.sha256()

    chunk_iter = iter(iter_text_chunks(content_parts, chunk_size=chunk_size))
    try:
        first_chunk = next(chunk_iter)
    except StopIteration:
        first_chunk = ""

    expected_hasher.update(first_chunk.encode("utf-8").replace(b"\r\n", b"\n"))
    create = run_obsidian_cmd(
        "create",
        f"path={target_path}",
        f"content={obsidian_escape_content(first_chunk)}",
        "overwrite",
        "silent",
        vault=vault,
        timeout=90,
    )
    if create.returncode != 0:
        raise RuntimeError(create.stderr or create.stdout or f"Failed to create {target_path}")

    for chunk in chunk_iter:
        expected_hasher.update(chunk.encode("utf-8").replace(b"\r\n", b"\n"))
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

    if not verify:
        return

    expected_hash = expected_hasher.hexdigest()

    if vault_root is not None:
        note_path = Path(vault_root) / target_path
        actual_hash = sha256_file_normalized_newlines(note_path)
        if actual_hash != expected_hash:
            raise RuntimeError(f"Obsidian on-disk mismatch for {target_path}")
        return

    # Backward compatible read-back verification.
    read = run_obsidian_cmd(
        "read",
        f"path={target_path}",
        vault=vault,
        timeout=90,
    )
    if read.returncode != 0:
        raise RuntimeError(read.stderr or read.stdout or f"Failed to read back {target_path}")

    actual_hash = hashlib.sha256((read.stdout or "").replace("\r\n", "\n").encode("utf-8")).hexdigest()
    if actual_hash != expected_hash:
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
    needles = {f"![[images/{asset_name}]]": asset_name for asset_name in asset_names}
    if needles:
        max_len = max(len(key) for key in needles)
        buf = ""
        with Path(note_path).open("r", encoding="utf-8", errors="replace") as handle:
            while needles:
                chunk = handle.read(64 * 1024)
                if not chunk:
                    break
                buf += chunk
                for needle in list(needles.keys()):
                    if needle in buf:
                        needles.pop(needle, None)
                if len(buf) > max_len * 4:
                    buf = buf[-max_len * 2 :]
        if needles:
            missing = ", ".join(sorted(needles.values()))
            raise RuntimeError(f"Rewritten asset reference missing in note: {missing}")

    for asset_name in asset_names:
        if not (images_dir / asset_name).exists():
            raise RuntimeError(f"Copied asset missing from vault: {images_dir / asset_name}")
