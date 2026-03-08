---
name: your-skill-name
description: Briefly describe what the skill does, when to use it, and typical trigger phrases.
---

# Skill Name

Short summary of the skill.

## When to Use

Use this skill when the user asks to:
- do action one
- do action two
- do action three

## Prerequisites

List required tools, accounts, services, or environment variables.

## Directory Layout

- `SKILL.md` — source of truth for runtime behavior
- `lib/` — reusable logic
- `scripts/` — executable entrypoints
- `tmp/` — disposable scratch outputs

## Workflow

### Step 1: Gather input
Describe the required input.

### Step 2: Run the main script

```bash
python3 scripts/example.py
```

### Step 3: Validate output
Describe what files or outputs to inspect.

## Error Handling

- Common failure 1 — recovery guidance
- Common failure 2 — recovery guidance

## Cleanup

Keep generated artifacts inside `tmp/` and do not commit them.
