# Skills Directory

Store every repository skill in this directory. Use `_template/` as the base scaffold for new skills.

## Rules

- One skill per subdirectory: `skills/<skill-name>/`
- Each skill must include a `SKILL.md`
- Keep implementation files local to that skill directory
- Avoid imports or runtime dependencies across sibling skills
- Put temporary outputs inside the skill's own `tmp/` directory

## Current Skills

- `dongchedi-scraper/`
- `_template/` — starter scaffold for new skills

Use `../scripts/new-skill.sh <skill-name>` to create a new skill from `_template/`.
