# Skill Template

Use this directory as the base scaffold for a new skill.

## Included Files

- `SKILL.md` — skill metadata and runtime contract
- `references/` — detailed prompts, schemas, or setup notes when needed
- `lib/` — reusable implementation logic only when code is actually needed
- `scripts/` — executable entry scripts only when prompt orchestration is not enough
- `tmp/` — local scratch outputs

## Suggested Workflow

1. Rename the directory in kebab-case with a `prism-` prefix, for example `skills/prism-wechat-poster/`
2. Read `docs/skill-writing-guidelines.md`
3. Update `SKILL.md` metadata and the required sections
4. Start prompt-first; add `scripts/` or `lib/` only if the skill truly needs deterministic code
5. Add only the files the skill actually needs
6. Keep setup and runtime policy inside the new skill's `SKILL.md`
