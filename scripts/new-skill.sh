#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: scripts/new-skill.sh <skill-name>" >&2
  exit 1
fi

name="$1"

if [[ ! "$name" =~ ^[a-z0-9]+([-.][a-z0-9]+)*$ ]]; then
  echo "Error: skill name must be kebab-case-like, e.g. wechat-poster" >&2
  exit 1
fi

root_dir="$(cd "$(dirname "$0")/.." && pwd)"
template_dir="$root_dir/skills/_template"
target_dir="$root_dir/skills/$name"

if [ ! -d "$template_dir" ]; then
  echo "Error: template directory not found: $template_dir" >&2
  exit 1
fi

if [ -e "$target_dir" ]; then
  echo "Error: target already exists: $target_dir" >&2
  exit 1
fi

cp -R "$template_dir" "$target_dir"
find "$target_dir" -name '.gitkeep' -o -name '.DS_Store' | while read -r path; do
  [ -e "$path" ] && rm -f "$path"
done

python3 - "$name" "$target_dir" <<'PY'
from pathlib import Path
import sys

name = sys.argv[1]
target = Path(sys.argv[2])

replacements = {
    'your-skill-name': name,
    'Skill Name': name.replace('-', ' ').title(),
}

for path in target.rglob('*'):
    if path.is_file():
        try:
            text = path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            continue
        for src, dst in replacements.items():
            text = text.replace(src, dst)
        path.write_text(text, encoding='utf-8')
PY

mkdir -p "$target_dir/tmp"
: > "$target_dir/tmp/.gitkeep"

echo "Created skill at: skills/$name"
echo "Next: edit skills/$name/SKILL.md and skills/$name/README.md"
