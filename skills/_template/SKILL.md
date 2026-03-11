---
name: prism-your-skill-name
description: Use when the user asks for the workflow this skill owns, including the main trigger phrases and situations.
---

# Skill Name

Short summary of the skill.

## Overview

Describe the core capability in 1-3 short sentences.

## When to Use

Use this skill when the user asks to:
- do action one
- do action two
- do action three

## Hard Constraints

- Constraint one
- Constraint two

## Runtime Policy

Explain how the runtime, dependencies, or external tools are selected.

## Output Contract

Describe what persistent outputs are created or updated, and what must remain stable.

## Directory Layout

- `SKILL.md` — source of truth for runtime behavior
- `references/` — detailed prompts, schemas, or setup notes
- `lib/` — reusable logic only when code is actually needed
- `scripts/` — executable entrypoints only when prompt orchestration is not enough
- `tmp/` — disposable scratch outputs

## Workflow

### Step 1: Gather input
Describe the required input.

### Step 2: Execute

Describe the main flow. Start prompt-first and only add script execution if the skill truly needs deterministic code.

If a script exists, document it explicitly with the exact command and why the script is needed.

### Step 3: Confirm or validate
Describe what must be confirmed before writing or publishing.

## Failure Handling

- Common failure 1 — recovery guidance
- Common failure 2 — recovery guidance
