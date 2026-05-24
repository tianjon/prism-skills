"""Stdlib HTTP client for OpenAI-compatible Images API.

Targets two endpoints under the resolved base URL:
- POST {base}/images/generations  (JSON)
- POST {base}/images/edits        (multipart/form-data)
"""

from __future__ import annotations

import base64
import json
import mimetypes
import secrets
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

DEFAULT_MODEL = "gpt-image-2"
GENERATIONS_PATH = "/images/generations"
EDITS_PATH = "/images/edits"


class APIError(SystemExit):
    """Raised on HTTP or transport errors so the CLI exits cleanly."""


def _auth_headers(api_key: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "Accept": "*/*",
    }


def _post_json(
    base_url: str,
    path: str,
    api_key: str,
    payload: dict[str, Any],
    timeout: int = 180,
) -> dict[str, Any]:
    url = f"{base_url.rstrip('/')}{path}"
    body = json.dumps(payload).encode("utf-8")
    headers = _auth_headers(api_key)
    headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, method="POST", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        raise APIError(f"HTTP {exc.code} from {url}: {detail}")
    except urllib.error.URLError as exc:
        raise APIError(f"Network error to {url}: {exc.reason}")
    return json.loads(data)


def _build_multipart(
    fields: dict[str, str],
    files: list[tuple[str, Path]],
) -> tuple[bytes, str]:
    boundary = "----prism-" + secrets.token_hex(16)
    parts = bytearray()
    for key, value in fields.items():
        parts += (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{key}"\r\n\r\n'
            f"{value}\r\n"
        ).encode("utf-8")
    for key, path in files:
        ctype = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        parts += (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{key}"; filename="{path.name}"\r\n'
            f"Content-Type: {ctype}\r\n\r\n"
        ).encode("utf-8")
        parts += path.read_bytes()
        parts += b"\r\n"
    parts += f"--{boundary}--\r\n".encode("utf-8")
    return bytes(parts), boundary


def _post_multipart(
    base_url: str,
    path: str,
    api_key: str,
    fields: dict[str, str],
    files: list[tuple[str, Path]],
    timeout: int = 240,
) -> dict[str, Any]:
    body, boundary = _build_multipart(fields, files)
    url = f"{base_url.rstrip('/')}{path}"
    headers = _auth_headers(api_key)
    headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    req = urllib.request.Request(url, data=body, method="POST", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        raise APIError(f"HTTP {exc.code} from {url}: {detail}")
    except urllib.error.URLError as exc:
        raise APIError(f"Network error to {url}: {exc.reason}")
    return json.loads(data)


def generate(
    api_key: str,
    base_url: str,
    *,
    prompt: str,
    model: str = DEFAULT_MODEL,
    n: int = 1,
    size: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {"model": model, "prompt": prompt, "n": n}
    if size:
        payload["size"] = size
    if extra:
        for key, value in extra.items():
            if value is not None:
                payload[key] = value
    return _post_json(base_url, GENERATIONS_PATH, api_key, payload)


def edit(
    api_key: str,
    base_url: str,
    *,
    prompt: str,
    image_paths: list[Path],
    mask_path: Path | None = None,
    model: str = DEFAULT_MODEL,
    n: int = 1,
    size: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not image_paths:
        raise APIError("edit requires at least one --image path.")
    fields: dict[str, str] = {
        "model": model,
        "prompt": prompt,
        "n": str(n),
    }
    if size:
        fields["size"] = size
    if extra:
        for key, value in extra.items():
            if value is not None:
                fields[key] = str(value)

    files: list[tuple[str, Path]] = []
    if len(image_paths) == 1:
        files.append(("image", image_paths[0]))
    else:
        for path in image_paths:
            files.append(("image[]", path))
    if mask_path is not None:
        files.append(("mask", mask_path))

    return _post_multipart(base_url, EDITS_PATH, api_key, fields, files)


def write_results(
    payload: dict[str, Any],
    *,
    output: Path | None,
    output_dir: Path | None,
    basename: str = "image",
) -> list[Path]:
    items = payload.get("data") or []
    if not items:
        raise APIError(
            f"API response missing 'data' array: {json.dumps(payload, ensure_ascii=False)[:500]}"
        )

    targets = _plan_output_paths(len(items), output=output, output_dir=output_dir, basename=basename)
    saved: list[Path] = []
    for item, target in zip(items, targets):
        target.parent.mkdir(parents=True, exist_ok=True)
        b64 = item.get("b64_json")
        url = item.get("url")
        if b64:
            target.write_bytes(base64.b64decode(b64))
        elif url:
            try:
                with urllib.request.urlopen(url, timeout=120) as resp:
                    target.write_bytes(resp.read())
            except urllib.error.URLError as exc:
                raise APIError(f"Failed to download {url}: {exc}")
        else:
            raise APIError(f"data entry missing both b64_json and url: {item}")
        saved.append(target)
    return saved


def _plan_output_paths(
    count: int,
    *,
    output: Path | None,
    output_dir: Path | None,
    basename: str,
) -> list[Path]:
    if output is not None and output_dir is not None:
        raise APIError("Pass either --output or --output-dir, not both.")
    if output is not None:
        if output.exists() and output.is_dir():
            raise APIError(
                f"--output {output} is an existing directory; use --output-dir instead."
            )
        if count == 1:
            return [output]
        suffix = output.suffix or ".png"
        stem = output.stem
        return [output.with_name(f"{stem}_{i}{suffix}") for i in range(count)]
    if output_dir is not None:
        return [output_dir / f"{basename}_{i}.png" for i in range(count)]
    return [Path(f"{basename}_{i}.png") for i in range(count)]
