"""Credential resolution for prism-gpt-image-2.

Precedence order:
1. ANS_API_KEY + ANS_BASE_URL  (Anspire gateway)
2. OPENAI_API_KEY (+ optional OPENAI_BASE_URL, default https://api.openai.com/v1)
3. Persisted config file ~/.config/prism-gpt-image-2/env, auto-loaded into env
4. Blocking interactive setup that writes step 3
"""

from __future__ import annotations

import os
import sys
from getpass import getpass
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "prism-gpt-image-2"
CONFIG_FILE = CONFIG_DIR / "env"

DEFAULT_OPENAI_BASE_URL = "https://api.openai.com/v1"


def load_config_file() -> None:
    """Load KEY=VALUE lines from CONFIG_FILE into os.environ.

    Existing environment variables always win over file values, so users can
    override the persisted config on a single invocation by exporting the
    variable in their shell.
    """
    if not CONFIG_FILE.exists():
        return
    try:
        text = CONFIG_FILE.read_text(encoding="utf-8")
    except OSError:
        return
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def _from_anspire() -> tuple[str, str] | None:
    key = os.environ.get("ANS_API_KEY", "").strip()
    base = os.environ.get("ANS_BASE_URL", "").strip()
    if key and base:
        return key, base.rstrip("/")
    return None


def _from_openai() -> tuple[str, str] | None:
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        return None
    base = os.environ.get("OPENAI_BASE_URL", "").strip() or DEFAULT_OPENAI_BASE_URL
    return key, base.rstrip("/")


def resolve_credentials(interactive: bool = True) -> tuple[str, str]:
    """Return (api_key, base_url) following the documented precedence order."""
    load_config_file()

    found = _from_anspire() or _from_openai()
    if found:
        return found

    if not interactive:
        raise SystemExit(
            "No credentials found. Set ANS_API_KEY+ANS_BASE_URL or "
            "OPENAI_API_KEY (and optionally OPENAI_BASE_URL), or run "
            "`python3 scripts/cli.py setup` to configure interactively."
        )

    return first_time_setup()


def first_time_setup() -> tuple[str, str]:
    """Prompt the user for OpenAI base URL + API key and persist to CONFIG_FILE."""
    print(
        "First-time setup for prism-gpt-image-2.\n"
        "Configure OpenAI-compatible image generation credentials.\n"
        "(Anspire users: export ANS_BASE_URL and ANS_API_KEY in your shell instead.)\n",
        file=sys.stderr,
    )
    base_url = input(f"OpenAI base URL [{DEFAULT_OPENAI_BASE_URL}]: ").strip() or DEFAULT_OPENAI_BASE_URL
    api_key = getpass("OpenAI API key (input hidden): ").strip()
    if not api_key:
        raise SystemExit("API key cannot be empty.")
    base_url = base_url.rstrip("/")

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(
        "# prism-gpt-image-2 config — auto-loaded by the skill at startup.\n"
        "# Delete this file or rerun `python3 scripts/cli.py setup` to overwrite.\n"
        f"OPENAI_BASE_URL={base_url}\n"
        f"OPENAI_API_KEY={api_key}\n",
        encoding="utf-8",
    )
    try:
        os.chmod(CONFIG_FILE, 0o600)
    except OSError:
        pass

    os.environ["OPENAI_BASE_URL"] = base_url
    os.environ["OPENAI_API_KEY"] = api_key
    print(f"Saved credentials to {CONFIG_FILE} (chmod 600).", file=sys.stderr)
    return api_key, base_url
