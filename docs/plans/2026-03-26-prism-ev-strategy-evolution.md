# Prism EV Strategy Evolution Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a prompt-first skill for brand-wide three-electric strategy analysis from Obsidian notes, with pure EV vs range-extended EV separation and fixed Obsidian output paths.

**Architecture:** Keep the implementation documentation-first. Use `SKILL.md` as the runtime contract, references as the execution assets, and lightweight tests to enforce the prompt-first contract. Avoid analysis scripts unless prompt orchestration is proven insufficient.

**Tech Stack:** Markdown, `obsidian-cli`, Python `unittest` for contract checks

---

### Task 1: Add the new skill skeleton and failing contract tests

**Files:**
- Create: `skills/prism-ev-strategy-evolution/tests/test_skill_contract.py`
- Create: `skills/prism-ev-strategy-evolution/tests/test_references.py`

**Step 1: Write the skill contract tests**

Assert that the skill contains the required repository sections and prompt-first constraints.

**Step 2: Write the reference coverage tests**

Assert that the analysis framework, prompt templates, and Obsidian workflow references exist and contain the required concepts.

**Step 3: Run the focused test suite**

Run: `PYTHONDONTWRITEBYTECODE=1 uv run python -B -m unittest discover skills/prism-ev-strategy-evolution/tests`
Expected: FAIL before the new files are added.

### Task 2: Implement the prompt-first skill

**Files:**
- Create: `skills/prism-ev-strategy-evolution/SKILL.md`
- Create: `skills/prism-ev-strategy-evolution/README.md`
- Create: `skills/prism-ev-strategy-evolution/tmp/.gitkeep`

**Step 1: Write the runtime contract**

Document the trigger conditions, hard constraints, runtime policy, output paths, workflow, and failure handling.

**Step 2: Keep the skill reasoning-led**

Explicitly state that the skill relies on prompts, `obsidian-cli`, and agent reasoning, not fixed-rule analysis scripts.

### Task 3: Add the execution references

**Files:**
- Create: `skills/prism-ev-strategy-evolution/references/analysis-framework.md`
- Create: `skills/prism-ev-strategy-evolution/references/prompt-templates.md`
- Create: `skills/prism-ev-strategy-evolution/references/obsidian-workflow.md`

**Step 1: Add the analysis framework**

Cover brand stage, timeline, pure EV route, range-extended EV route, price/configuration, configuration/vehicle-mass, and discontinued models.

**Step 2: Add prompt templates**

Provide reusable prompts for the brand report, model report, methodology note, and stage-map note.

**Step 3: Add the Obsidian workflow**

Document the `obsidian search` -> `obsidian read` -> reasoning -> `obsidian create` / `obsidian append` loop.

### Task 4: Update repository-level docs

**Files:**
- Modify: `README.md`
- Modify: `skills/README.md`
- Create: `docs/plans/2026-03-26-prism-ev-strategy-evolution-design.md`
- Create: `docs/plans/2026-03-26-prism-ev-strategy-evolution.md`

**Step 1: List the new skill in repository indexes**

Update installation and quick-start guidance.

**Step 2: Write design and implementation plan docs**

Capture the rationale and the documentation-first implementation strategy.

### Task 5: Verify the final state

**Files:**
- Verify: `skills/prism-ev-strategy-evolution/SKILL.md`
- Verify: `skills/prism-ev-strategy-evolution/references/analysis-framework.md`
- Verify: `skills/prism-ev-strategy-evolution/references/prompt-templates.md`
- Verify: `skills/prism-ev-strategy-evolution/references/obsidian-workflow.md`
- Verify: `README.md`
- Verify: `skills/README.md`

**Step 1: Run the focused test suite**

Run: `PYTHONDONTWRITEBYTECODE=1 uv run python -B -m unittest discover skills/prism-ev-strategy-evolution/tests`
Expected: PASS

**Step 2: Inspect the git diff**

Run: `git diff -- README.md skills/README.md skills/prism-ev-strategy-evolution docs/plans/2026-03-26-prism-ev-strategy-evolution-design.md docs/plans/2026-03-26-prism-ev-strategy-evolution.md`
Expected: only prompt-first skill changes and plan docs appear

**Step 3: Record manual validation gap**

Note that live Obsidian CLI end-to-end validation against a running vault still needs a manual run.
