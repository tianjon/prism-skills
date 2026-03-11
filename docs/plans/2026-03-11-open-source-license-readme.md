# Open Source License And README Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the repository's restrictive license with MIT and rewrite the README so it reads like a normal public open-source repository.

**Architecture:** Keep changes focused on top-level documentation. Update `LICENSE` first, then rewrite `README.md` around clear public-facing sections, and finally verify that the old restrictive wording is gone.

**Tech Stack:** Markdown, plain text

---

### Task 1: Add design and plan documents

**Files:**
- Create: `docs/plans/2026-03-11-open-source-license-readme-design.md`
- Create: `docs/plans/2026-03-11-open-source-license-readme.md`

**Step 1: Write the design document**

Capture the goal, scope, non-goals, target README structure, and validation criteria.

**Step 2: Write the implementation plan**

Describe the files to update and the verification commands.

### Task 2: Replace the license

**Files:**
- Modify: `LICENSE`

**Step 1: Replace the current custom license with MIT**

Use the standard MIT License text.

**Step 2: Verify the new header**

Run: `sed -n '1,20p' LICENSE`
Expected: starts with `MIT License`

### Task 3: Rewrite the README

**Files:**
- Modify: `README.md`

**Step 1: Remove restrictive language**

Delete non-commercial, source-available, and usage restriction language.

**Step 2: Add public repository sections**

Ensure the README includes:

- project overview
- available skills
- supported agent environments
- requirements
- installation
- quick start
- repository structure
- contributing
- license

**Step 3: Keep examples accurate**

Retain working installation examples and skill entrypoints.

### Task 4: Verify the final state

**Files:**
- Verify: `README.md`
- Verify: `LICENSE`

**Step 1: Check for removed restrictive wording**

Run: `rg -n "non-commercial|source-available|Usage Restrictions|Personal Research" README.md LICENSE`
Expected: no matches

**Step 2: Check README section coverage**

Run: `rg -n "^## (Available Skills|Installation|Quick Start|Repository Structure|Contributing|License)$" README.md`
Expected: all sections found

**Step 3: Check MIT license header**

Run: `rg -n "^MIT License$" LICENSE`
Expected: one match
