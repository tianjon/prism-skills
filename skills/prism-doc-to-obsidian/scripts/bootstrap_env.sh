#!/usr/bin/env bash
set -euo pipefail

# Bootstrap a runnable environment for this skill on machines with old system Python.
#
# Defaults:
# - Installs a uv-managed Python (if needed)
# - Creates/uses a virtualenv under $HOME/.base-env/
# - Runs `uv sync` against the active env
#
# Usage:
#   ./scripts/bootstrap_env.sh
#
# Overrides:
#   PRISM_DOC_TO_OBSIDIAN_PYTHON=3.12   # requested python version (or "3.11", ">=3.10,<3.14")
#   PRISM_DOC_TO_OBSIDIAN_VENV=~/.base-env/prism-doc-to-obsidian
#   PRISM_DOC_TO_OBSIDIAN_DOWNLOADS=never|auto  # map to UV_PYTHON_DOWNLOADS

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${ROOT_DIR}"

if ! command -v uv >/dev/null 2>&1; then
  echo "ERROR: uv is not installed or not on PATH." >&2
  echo "Install uv first, then re-run this script." >&2
  exit 1
fi

# Keep the default aligned with the skill's stated support range: 3.10 to 3.13.
PY_REQUEST="${PRISM_DOC_TO_OBSIDIAN_PYTHON:-3.11}"
VENV_DIR="${PRISM_DOC_TO_OBSIDIAN_VENV:-${HOME}/.base-env/prism-doc-to-obsidian}"

# Allow callers to prohibit Python downloads (e.g. in air-gapped CI) while keeping this script
# self-contained.
if [[ -n "${PRISM_DOC_TO_OBSIDIAN_DOWNLOADS:-}" ]]; then
  export UV_PYTHON_DOWNLOADS="${PRISM_DOC_TO_OBSIDIAN_DOWNLOADS}"
fi

echo "Project: ${ROOT_DIR}"
echo "Requested Python: ${PY_REQUEST}"
echo "Virtualenv: ${VENV_DIR}"

mkdir -p "${VENV_DIR%/*}"

python_path=""
if python_path="$(uv python find "${PY_REQUEST}" 2>/dev/null)"; then
  :
else
  echo "Python '${PY_REQUEST}' not found. Attempting to install via uv..."
  if ! uv python install "${PY_REQUEST}"; then
    echo "ERROR: uv failed to install Python '${PY_REQUEST}'." >&2
    echo "If this machine is offline or forbids downloads, preinstall a compatible Python (3.10-3.13) and set:" >&2
    echo "  PRISM_DOC_TO_OBSIDIAN_PYTHON=/path/to/python" >&2
    exit 1
  fi
  python_path="$(uv python find "${PY_REQUEST}")"
fi

if [[ ! -x "${VENV_DIR}/bin/python" ]]; then
  echo "Creating virtualenv..."
  uv venv -p "${python_path}" "${VENV_DIR}"
else
  echo "Reusing existing virtualenv."
fi

if ! "${VENV_DIR}/bin/python" - <<'PY'
import sys
major, minor = sys.version_info[:2]
ok = (major, minor) >= (3, 10) and (major, minor) <= (3, 13)
if not ok:
    raise SystemExit(f"Unsupported Python: {sys.version.split()[0]} (expected 3.10-3.13)")
print(sys.version.split()[0])
PY
then
  echo "ERROR: virtualenv Python does not meet the required range (3.10-3.13)." >&2
  exit 1
fi

echo "Syncing dependencies into the active env..."
export VIRTUAL_ENV="${VENV_DIR}"
export PATH="${VENV_DIR}/bin:${PATH}"
uv sync --active

echo "OK. Next examples:"
echo "  uv run --active python scripts/convert_recursive.py --help"
echo "  uv run --active python scripts/import_to_obsidian.py --help"

