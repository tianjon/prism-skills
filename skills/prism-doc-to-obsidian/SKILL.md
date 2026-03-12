---
name: prism-doc-to-obsidian
description: Use when converting MinerU-supported documents into Markdown and saving them into Obsidian with confirmed folder planning, indexes, tags, cross-note links, and preserved extracted assets.
---

# Document To Obsidian

Convert MinerU-supported documents into Markdown, then save confirmed results into the active Obsidian vault.

## Overview

This skill is confirmation-first at the conversation level, and uses a deterministic two-stage backend to avoid common import failures:

- `scripts/convert_recursive.py` converts inputs recursively and emits a manifest.
- `scripts/import_to_obsidian.py` imports from that manifest into the active vault with stable paths, asset copying, and verification.

Use this skill to:

- ingest one document into Obsidian
- ingest a directory of MinerU-supported documents into Obsidian
- maintain topic indexes, tags, cross-note links, and extracted assets during import

## When to Use

Use this skill when the user asks to:

- convert a file into Obsidian notes
- import a directory of documents into Obsidian
- use MinerU to extract Markdown before storing documents in Obsidian
- maintain category indexes or `.base` views while importing documents

## Hard Constraints

- All final Obsidian writes must go through `obsidian-cli`.
- Note bodies must be written via `obsidian-cli`. Binary attachments must be copied via the filesystem because the CLI is text-only.
- Do not write to Obsidian before showing the proposed folder structure and file list.
- The user must be able to revise folder names, note names, tags, and category placement through the conversation.
- Support both single-file input and directory input.
- For directory input, do not assume MinerU will recurse into subdirectories. Enumerate supported files recursively before conversion or convert each subdirectory explicitly.
- Follow MinerU's supported input formats instead of maintaining a separate hardcoded format list.
- Do not hardcode private paths or project-local virtual environment paths.
- Do not silently drop MinerU-extracted assets such as images. Asset preservation or removal must be explicit in the proposal and confirmed by the user.
- Final Obsidian notes must preserve or intentionally transform valid image/embed references so they resolve inside the vault after import.

## Required Skills

Use these installed skills during execution:

- `obsidian-markdown` for note formatting rules
- `obsidian-bases` for durable category views when they materially improve navigation
- `obsidian-cli` for all final vault operations

Dependency contract:

- `obsidian-markdown` governs note formatting, not final storage
- `obsidian-bases` is optional unless a durable category view materially improves navigation
- `obsidian-cli` is the required final write path

If any required Obsidian skill is missing, install only the missing skill before continuing. Prefer the local `skill-installer` workflow instead of inventing a new installer.

## Runtime Policy

Read [references/install-and-checks.md](references/install-and-checks.md) before running checks.

Minimum requirements:

- Python `3.10` to `3.13`
- Obsidian `1.12+` with CLI support enabled and the app already running
- `obsidian help` must succeed

Dependency policy:

- If MinerU is missing, install it automatically and trigger the model download flow.
- If MinerU is present but local models are missing, download the models before conversion.
- If a required Obsidian skill is missing, install it before continuing.
- Stop immediately after failed installation or failed model download.

## Output Contract

This skill always follows a confirmation-first write model.

Before any write, it must produce a proposal that includes:

- target folder tree
- files to create or update
- note titles
- category indexes to create or update
- tag scheme
- wikilink relationships
- extracted asset strategy, including where images or other attachments will live in the vault
- whether asset references will stay as Markdown links or be rewritten as Obsidian embeds
- whether a `.base` file is needed

After confirmation, the skill writes notes into the active vault and updates long-lived category indexes instead of creating one-off batch-only records.

## Workflow

### Step 1: Detect input

Accept either:

- one file path
- one directory path

For directory input:

- preserve the meaningful parts of the source hierarchy for later storage planning
- discover supported files recursively before conversion
- record which source files are expected to produce Markdown and which ones also produce extracted assets

### Step 2: Convert with MinerU

Convert the input into Markdown and related assets with MinerU. Keep intermediate outputs inside `tmp/` or another disposable working location.

Implementation guidance:

- Use `python3 scripts/convert_recursive.py --input <file-or-dir> --output <tmp-root>` to convert recursively and generate `manifest.json`.
- Treat `manifest.json` as the single source of truth for `source_rel_path -> markdown_path -> assets_dir` mapping.

Asset handling requirements during conversion:

- treat MinerU `images/` and other extracted assets as first-class outputs, not optional byproducts
- track each Markdown file together with its sibling asset directory
- if the input is a directory, verify that all recursively discovered source files were actually converted; do not stop after only the top-level directory contents

### Step 3: Plan Obsidian storage

Read [references/storage-planning.md](references/storage-planning.md).

Build a storage proposal before any write.

The storage proposal must explicitly decide:

- whether extracted assets are preserved in the vault
- the attachment folder layout for those assets
- how source Markdown asset references will be rewritten so they resolve in Obsidian

### Step 4: Confirm with the user

Do not write yet. Present the proposal and wait for explicit confirmation.

The user may revise:

- folder names
- file names
- category placement
- index structure
- tags
- related-note links
- attachment placement
- whether to preserve, omit, or partially keep extracted assets

### Step 5: Write to Obsidian

After confirmation:

- format notes according to `obsidian-markdown`
- create or update notes through `obsidian-cli`
- copy or create extracted assets into the planned vault locations
- rewrite image or attachment references so they resolve inside Obsidian after import
- create or update `.base` files only when they improve long-term navigation

Verification requirements during write:

- verify that each note with extracted assets still contains valid embed or image references after rewrite
- verify that referenced asset files exist at the final vault paths

Implementation guidance:

- Use `python3 scripts/import_to_obsidian.py --manifest <manifest.json> --target-root <vault-subpath>` to perform the deterministic import.
- The importer rewrites `![](images/...)` to `![[images/...]]`, copies extracted assets into a stable `images/` folder, and fails fast on broken asset references.

### Step 6: Maintain indexes and links

Maintain long-lived category indexes. Connect imported notes to their categories through tags and wikilinks, and add related-note sections where the content relationship is strong.

If assets were preserved, keep their placement stable so future re-imports do not break existing links.

## Prompt Assets

Read [references/prompt-templates.md](references/prompt-templates.md) and reuse those bilingual prompts instead of rewriting them from scratch.

## Failure Handling

- If Python is missing or unsupported, stop with a version-specific explanation.
- If Obsidian CLI is unavailable or Obsidian is not running, stop and tell the user what to fix.
- If MinerU installation or model download fails, report the exact failed command and stop.
- If the storage proposal is ambiguous, present 2-3 concrete options before writing.

## Directory Layout

- `SKILL.md` — source of truth for the runtime workflow
- `references/install-and-checks.md` — environment checks and install flow
- `references/storage-planning.md` — Obsidian folder planning and index rules
- `references/prompt-templates.md` — bilingual reusable prompts
- `tmp/` — disposable conversion outputs
