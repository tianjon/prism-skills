# Skills Directory

Store all repository skills in this directory.

## Rules

- One skill per subdirectory: `skills/<skill-name>/`
- Every skill must include a `SKILL.md`
- Keep implementation files local to the skill directory
- Avoid runtime dependencies across sibling skills
- Keep temporary outputs inside the skill's own `tmp/` directory

## Current Entries

- `dongchedi-scraper/`
- `_template/` — starter scaffold for future skills

Create a new skill with:

```bash
./scripts/new-skill.sh <skill-name>
```
