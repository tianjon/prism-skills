---
name: your-skill-name
description: Briefly describe what this skill does, when to use it, and trigger phrases.
---

# Skill Name

Short summary of the skill's purpose.

## When to Use

Use this skill when the user asks to:
- action one
- action two
- action three

## Prerequisites

List required tools, services, environment variables, or accounts.

```bash
# example setup
cd ~/ai/prism-skills/skills/your-skill-name
```

## Directory Layout

- `SKILL.md` — source of truth for the skill workflow
- `lib/` — reusable logic
- `scripts/` — runnable entry scripts
- `tmp/` — generated scratch files

## Workflow

### Step 1: Gather input
Describe what input is required.

### Step 2: Run the main script

```bash
python3 scripts/example.py
```

### Step 3: Validate output
Explain what files or output to inspect.

## Error Handling

- Common failure 1 — how to recover
- Common failure 2 — how to recover

## Cleanup

```bash
rm -f tmp/*
```
