# MinerU To Obsidian Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a new `prism-doc-to-obsidian` skill that converts MinerU-supported documents to Markdown and publishes confirmed notes into the active Obsidian vault with indexes, tags, and links.

**Architecture:** Keep the implementation prompt-first. Put the operational workflow in `SKILL.md`, move detailed guidance into `references/`, and avoid Python orchestration unless a later validation step proves it necessary.

**Tech Stack:** Markdown, local skill structure, MinerU CLI, Obsidian CLI, existing Obsidian-related skills

---

### Task 1: Write design artifacts

**Files:**
- Create: `docs/plans/2026-03-11-prism-doc-to-obsidian-design.md`
- Create: `docs/plans/2026-03-11-prism-doc-to-obsidian.md`

**Step 1: Write the design document**

Document the goal, scope, non-goals, workflow, storage planning, and validation criteria.

**Step 2: Write the implementation plan**

Capture the exact files to create and the verification steps.

**Step 3: Verify both files exist**

Run: `ls docs/plans/2026-03-11-prism-doc-to-obsidian*`
Expected: both files listed

### Task 2: Create the new skill skeleton

**Files:**
- Create: `skills/prism-doc-to-obsidian/SKILL.md`
- Create: `skills/prism-doc-to-obsidian/references/install-and-checks.md`
- Create: `skills/prism-doc-to-obsidian/references/storage-planning.md`
- Create: `skills/prism-doc-to-obsidian/references/prompt-templates.md`
- Create: `skills/prism-doc-to-obsidian/tmp/.gitkeep`

**Step 1: Write the `SKILL.md`**

Include:
- frontmatter with trigger-focused description
- overview
- hard constraints
- environment checks
- dependency installation policy
- single-file and directory workflows
- confirmation-before-write rule
- index, tag, and link maintenance rules
- reference file navigation
- keep personal vault preferences out of the public contract

**Step 2: Write `references/install-and-checks.md`**

Include:
- Python and Obsidian minimum checks
- MinerU detection and install flow
- MinerU model download flow
- Obsidian skill detection and installation flow

**Step 3: Write `references/storage-planning.md`**

Include:
- folder planning rules
- topic index rules
- tag rules
- link rules
- no project-specific taxonomy in the shared contract

**Step 4: Write `references/prompt-templates.md`**

Include bilingual prompt templates for:
- environment check
- dependency installation
- single-file conversion
- directory conversion
- write confirmation
- index maintenance

**Step 5: Add `tmp/.gitkeep`**

Keep the skill layout consistent with the repository pattern.

### Task 3: Verify the skill content

**Files:**
- Verify: `skills/prism-doc-to-obsidian/SKILL.md`
- Verify: `skills/prism-doc-to-obsidian/references/install-and-checks.md`
- Verify: `skills/prism-doc-to-obsidian/references/storage-planning.md`
- Verify: `skills/prism-doc-to-obsidian/references/prompt-templates.md`

**Step 1: Check file presence**

Run: `find skills/prism-doc-to-obsidian -maxdepth 3 -type f | sort`
Expected: all planned files listed

**Step 2: Check bilingual prompt coverage**

Run: `rg -n "ZH:|EN:|中文|English" skills/prism-doc-to-obsidian`
Expected: hits in prompt references; bilingual content is not required in the main `SKILL.md`

**Step 3: Check write gating**

Run: `rg -n "confirm|确认|Do not write|不要立即写入" skills/prism-doc-to-obsidian`
Expected: clear confirmation-before-write language

**Step 4: Check for forbidden hardcoded env paths**

Run: `rg -n "~/.base-env|\\.venv|/Users/yr" skills/prism-doc-to-obsidian`
Expected: no matches
