#!/usr/bin/env python3
"""prism-gpt-image-2 CLI: generate, edit, setup."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))

from lib import api, credentials  # noqa: E402


def _emit_response(payload: dict, *, save_kwargs: dict, as_json: bool) -> None:
    if as_json:
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return
    saved = api.write_results(payload, **save_kwargs)
    for path in saved:
        print(path)


def _generation_extras(args) -> dict:
    return {
        "quality": args.quality,
        "background": args.background,
        "response_format": args.response_format,
    }


def cmd_generate(args) -> None:
    api_key, base_url = credentials.resolve_credentials(interactive=args.interactive)
    payload = api.generate(
        api_key,
        base_url,
        prompt=args.prompt,
        model=args.model,
        n=args.n,
        size=args.size,
        extra=_generation_extras(args),
    )
    _emit_response(
        payload,
        save_kwargs={
            "output": Path(args.output) if args.output else None,
            "output_dir": Path(args.output_dir) if args.output_dir else None,
            "basename": "generated",
        },
        as_json=args.json,
    )


def cmd_edit(args) -> None:
    api_key, base_url = credentials.resolve_credentials(interactive=args.interactive)
    image_paths = [Path(p) for p in args.image]
    for path in image_paths:
        if not path.exists():
            raise SystemExit(f"input image not found: {path}")
    mask_path: Path | None = Path(args.mask) if args.mask else None
    if mask_path is not None and not mask_path.exists():
        raise SystemExit(f"mask file not found: {mask_path}")

    payload = api.edit(
        api_key,
        base_url,
        prompt=args.prompt,
        image_paths=image_paths,
        mask_path=mask_path,
        model=args.model,
        n=args.n,
        size=args.size,
        extra={"quality": args.quality},
    )
    _emit_response(
        payload,
        save_kwargs={
            "output": Path(args.output) if args.output else None,
            "output_dir": Path(args.output_dir) if args.output_dir else None,
            "basename": "edited",
        },
        as_json=args.json,
    )


def cmd_setup(_args) -> None:
    credentials.first_time_setup()


def _add_common_io_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--prompt", required=True, help="Text prompt.")
    parser.add_argument("--model", default=api.DEFAULT_MODEL,
                        help=f"Model id (default {api.DEFAULT_MODEL}).")
    parser.add_argument("--n", type=int, default=1, help="Number of images (default 1).")
    parser.add_argument("--size", default="1024x1024",
                        help="Image size (default 1024x1024). Use 'auto' for server default.")
    parser.add_argument("--quality", choices=["low", "medium", "high", "auto"],
                        help="Quality hint, forwarded only when set.")
    parser.add_argument("--output", help="Output file path. With n>1 the index is appended to the stem.")
    parser.add_argument("--output-dir", dest="output_dir",
                        help="Directory to write generated_*.png / edited_*.png into.")
    parser.add_argument("--json", action="store_true",
                        help="Print the raw API response to stdout instead of saving images.")
    parser.add_argument("--no-interactive", dest="interactive", action="store_false",
                        help="Fail instead of prompting if credentials are missing.")
    parser.set_defaults(interactive=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="prism-gpt-image-2",
        description="OpenAI-compatible image generation (gpt-image-2 default).",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate", help="Text-to-image generation.")
    _add_common_io_args(g)
    g.add_argument("--background", choices=["opaque", "transparent", "auto"],
                   help="Background hint (generation only), forwarded only when set.")
    g.add_argument("--response-format", dest="response_format",
                   choices=["b64_json", "url"],
                   help="Server-side response format, forwarded only when set.")
    g.set_defaults(func=cmd_generate)

    e = sub.add_parser("edit", help="Edit one or more images, optionally with a mask.")
    _add_common_io_args(e)
    e.add_argument("--image", required=True, nargs="+",
                   help="One or more source image paths.")
    e.add_argument("--mask", help="Optional mask PNG; transparent areas are inpainted.")
    e.set_defaults(func=cmd_edit)

    s = sub.add_parser("setup",
                       help="Interactive first-time credential setup.")
    s.set_defaults(func=cmd_setup)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
