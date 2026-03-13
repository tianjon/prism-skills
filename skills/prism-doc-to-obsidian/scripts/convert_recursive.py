from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

module_file = globals().get("__file__")
SKILL_DIR = Path(module_file).resolve().parent.parent if module_file else Path.cwd().resolve()
sys.path.insert(0, str(SKILL_DIR))

from lib.conversion import (
    DEFAULT_DISCOVERABLE_EXTENSIONS,
    batch_output_root,
    build_conversion_batches,
    build_manifest_entries,
    discover_supported_inputs,
    normalize_extensions,
    save_manifest,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Recursively convert MinerU-supported files into Markdown")
    parser.add_argument("--input", required=True, help="Source file or directory")
    parser.add_argument("--output", required=True, help="Output root for MinerU artifacts")
    parser.add_argument("--manifest", default="", help="Optional manifest path (defaults to <output>/manifest.json)")
    parser.add_argument("--mineru-bin", default="mineru", help="MinerU executable path")
    parser.add_argument(
        "--extensions",
        default=",".join(DEFAULT_DISCOVERABLE_EXTENSIONS),
        help="Comma-separated discoverable file extensions",
    )
    parser.add_argument("--backend", default="pipeline", help="MinerU backend")
    parser.add_argument("--source", default="local", help="MinerU model source")
    parser.add_argument("--method", default="", help="Optional MinerU method")
    parser.add_argument("--lang", default="", help="Optional MinerU language hint")
    return parser


def run_mineru(
    *,
    mineru_bin: str,
    source_path: Path,
    output_path: Path,
    backend: str,
    source: str,
    method: str = "",
    lang: str = "",
) -> None:
    cmd = [
        mineru_bin,
        "-p",
        str(source_path),
        "-o",
        str(output_path),
        "-b",
        backend,
        "--source",
        source,
    ]
    if method:
        cmd.extend(["-m", method])
    if lang:
        cmd.extend(["-l", lang])
    # Avoid `capture_output=True` because MinerU can be very verbose and blow up memory on large conversions.
    output_path.mkdir(parents=True, exist_ok=True)
    log_path = output_path / "mineru.log"
    with log_path.open("a", encoding="utf-8", errors="replace") as handle:
        handle.write(f"\n\n# mineru run: {source_path}\n")
        handle.write(" ".join(cmd) + "\n")
        handle.flush()
        result = subprocess.run(cmd, stdout=handle, stderr=handle, text=True)
    if result.returncode != 0:
        # Provide only the log tail to keep exceptions readable.
        tail = ""
        try:
            with log_path.open("rb") as handle:
                handle.seek(0, 2)
                size = handle.tell()
                handle.seek(max(0, size - 8192))
                tail = handle.read().decode("utf-8", errors="replace")
        except OSError:
            tail = ""
        raise RuntimeError(f"MinerU failed for {source_path}. Log tail:\n{tail}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    input_path = Path(args.input).resolve()
    output_root = Path(args.output).resolve()
    manifest_path = Path(args.manifest).resolve() if args.manifest else output_root / "manifest.json"
    extensions = normalize_extensions(args.extensions.split(","))

    if shutil.which(args.mineru_bin) is None and not Path(args.mineru_bin).exists():
        raise RuntimeError(f"MinerU executable not found: {args.mineru_bin}")

    discovered_files = discover_supported_inputs(input_path, extensions=extensions)
    if not discovered_files:
        raise RuntimeError(f"No supported files found under {input_path}")

    for batch in build_conversion_batches(input_path, discovered_files):
        current_output_root = batch_output_root(output_root, batch.relative_parent)
        current_output_root.mkdir(parents=True, exist_ok=True)
        run_mineru(
            mineru_bin=args.mineru_bin,
            source_path=batch.source_path,
            output_path=current_output_root,
            backend=args.backend,
            source=args.source,
            method=args.method,
            lang=args.lang,
        )

    entries = build_manifest_entries(input_path, output_root, discovered_files)
    expected_sources = {
        path.name if input_path.is_file() else path.relative_to(input_path).as_posix()
        for path in discovered_files
    }
    manifest_sources = {entry.source_file for entry in entries}
    if manifest_sources != expected_sources:
        raise RuntimeError(
            "Manifest coverage mismatch: "
            f"discovered={sorted(expected_sources)} "
            f"manifest={sorted(manifest_sources)}"
        )

    manifest = save_manifest(
        manifest_path,
        input_path=input_path,
        output_root=output_root,
        extensions=extensions,
        entries=entries,
    )
    print(f"Converted {len(entries)} files")
    print(f"Manifest: {manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
