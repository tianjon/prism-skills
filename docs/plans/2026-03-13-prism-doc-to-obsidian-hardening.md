# Prism Doc To Obsidian Hardening Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Harden `prism-doc-to-obsidian` so directory imports recurse deterministically, MinerU assets are preserved into the vault, and long note writes are chunked and verified through `obsidian-cli`.

**Architecture:** Keep a two-stage backend. `convert_recursive.py` discovers supported source files recursively, runs MinerU once per direct-parent batch, and emits a manifest that preserves `source_rel_path -> markdown -> assets` mappings. `import_to_obsidian.py` consumes the manifest plus target-root rules, rewrites image embeds, copies binary assets into stable `images/` folders, writes note bodies through `obsidian-cli`, and verifies both note content and attachment existence.

**Tech Stack:** Python 3.10+, standard library `unittest`, MinerU CLI, Obsidian CLI

---

### Task 1: Add the failing tests

**Files:**
- Modify: `skills/prism-doc-to-obsidian/tests/test_conversion.py`
- Modify: `skills/prism-doc-to-obsidian/tests/test_obsidian_import.py`

**Step 1: Write a discovery/collision test**

Cover two source files with the same stem under different directories and assert the manifest keeps separate output roots and markdown paths.

**Step 2: Write a no-op rewrite test**

Assert markdown without image links is returned unchanged and reports no referenced assets.

**Step 3: Write a broken-link import test**

Assert importing a manifest entry whose markdown references a missing image fails before reporting success.

**Step 4: Write a long-write verification test**

Assert `write_obsidian_note()` issues `create`, the required number of `append inline` calls, then `read`, and fails when the read-back content differs.

**Step 5: Run the focused test module**

Run: `python3 -m unittest skills.prism-doc-to-obsidian.tests.test_conversion skills.prism-doc-to-obsidian.tests.test_obsidian_import`
Expected: FAIL on the newly added assertions before implementation changes.

### Task 2: Implement manifest-driven conversion helpers

**Files:**
- Modify: `skills/prism-doc-to-obsidian/lib/conversion.py`
- Modify: `skills/prism-doc-to-obsidian/scripts/convert_recursive.py`

**Step 1: Expand manifest metadata**

Include deterministic source/output relationships needed by the import stage, including note target defaults and stable asset directories.

**Step 2: Tighten generated markdown resolution**

Make collision handling explicit so same-named source files under different parents cannot resolve to the same converted output by accident.

**Step 3: Keep convert script thin**

Use the library helpers to discover files, batch by direct parent, run MinerU, build the manifest, and fail if any discovered source file is missing from the manifest.

**Step 4: Re-run the focused conversion tests**

Run: `python3 -m unittest skills.prism-doc-to-obsidian.tests.test_conversion`
Expected: PASS

### Task 3: Implement deterministic Obsidian import

**Files:**
- Modify: `skills/prism-doc-to-obsidian/lib/obsidian_import.py`
- Modify: `skills/prism-doc-to-obsidian/scripts/import_to_obsidian.py`

**Step 1: Build import-plan helpers**

Create helpers that derive note target paths, image folder paths, and asset validations from manifest entries and `--target-root`.

**Step 2: Rewrite markdown embeds and preserve assets**

Rewrite `![](images/...)` to `![[images/...]]`, copy binary assets into the planned vault `images/` folder, and fail if any referenced asset is absent.

**Step 3: Add chunked write read-back verification**

Write note bodies through `obsidian create` plus `obsidian append inline`, then `obsidian read` and compare the full content.

**Step 4: Support deterministic reruns**

Use stable target paths and overwrite behavior so repeated imports replace the same note and attachment files.

**Step 5: Re-run the focused import tests**

Run: `python3 -m unittest skills.prism-doc-to-obsidian.tests.test_obsidian_import`
Expected: PASS

### Task 4: Update skill docs and repository docs

**Files:**
- Modify: `skills/prism-doc-to-obsidian/SKILL.md`
- Modify: `README.md`

**Step 1: Update the skill workflow**

Document the two-stage backend, new script interfaces, manifest-driven import, and the rule that binary attachments are copied through the filesystem because `obsidian-cli` is text-only.

**Step 2: Update quick-start guidance**

Point the repository README to `convert_recursive.py` and `import_to_obsidian.py` instead of ad-hoc command assembly.

**Step 3: Check the docs mention asset preservation and CLI exception**

Run: `rg -n "convert_recursive|import_to_obsidian|binary|附件|images/" skills/prism-doc-to-obsidian/SKILL.md README.md`
Expected: hits for both scripts and the binary-attachment exception

### Task 5: Verify the whole change set

**Files:**
- Verify: `skills/prism-doc-to-obsidian/lib/conversion.py`
- Verify: `skills/prism-doc-to-obsidian/lib/obsidian_import.py`
- Verify: `skills/prism-doc-to-obsidian/scripts/convert_recursive.py`
- Verify: `skills/prism-doc-to-obsidian/scripts/import_to_obsidian.py`
- Verify: `skills/prism-doc-to-obsidian/tests/test_conversion.py`
- Verify: `skills/prism-doc-to-obsidian/tests/test_obsidian_import.py`
- Verify: `skills/prism-doc-to-obsidian/SKILL.md`
- Verify: `README.md`

**Step 1: Run the targeted test suite**

Run: `python3 -m unittest skills.prism-doc-to-obsidian.tests.test_conversion skills.prism-doc-to-obsidian.tests.test_obsidian_import`
Expected: PASS

**Step 2: Inspect the git diff for the touched skill**

Run: `git diff -- skills/prism-doc-to-obsidian README.md docs/plans/2026-03-13-prism-doc-to-obsidian-hardening.md`
Expected: only the planned hardening changes appear

**Step 3: Record any remaining manual validation gaps**

Note that full MinerU and live Obsidian CLI validation still need a local manual run against a real vault.
