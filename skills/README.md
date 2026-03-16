# Skills Directory

Store all repository skills in this directory.

## Rules

- One skill per subdirectory: `skills/<skill-name>/`
- Every skill must include a `SKILL.md`
- Keep implementation files local to the skill directory
- Avoid runtime dependencies across sibling skills
- Keep temporary outputs inside the skill's own `tmp/` directory
- Follow `docs/skill-writing-guidelines.md` when adding or refactoring a skill
- Do not treat local runtime artifacts such as `.venv/` as part of a skill's intended structure

## Current Entries

- `prism-dongchedi-scraper/`
- `prism-doc-to-obsidian/`
- `prism-macos-calendar-cli/`
- `_template/` — starter scaffold for future skills

Create a new skill with:

```bash
./scripts/new-skill.sh <skill-name>
```
