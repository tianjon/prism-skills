---
name: prism-doc-to-obsidian
description: Use when converting MinerU-supported documents into Markdown and saving them into Obsidian with confirmed folder planning, indexes, tags, and cross-note links.
---

# Document To Obsidian

Convert MinerU-supported documents into Markdown, then save confirmed results into the active Obsidian vault.

## Overview

This is a prompt-first skill. Prefer existing CLIs and installed skills over custom orchestration scripts.

Use this skill to:

- ingest one document into Obsidian
- ingest a directory of MinerU-supported documents into Obsidian
- maintain topic indexes, tags, and cross-note links during import

## When to Use

Use this skill when the user asks to:

- convert a file into Obsidian notes
- import a directory of documents into Obsidian
- use MinerU to extract Markdown before storing documents in Obsidian
- maintain category indexes or `.base` views while importing documents

## Hard Constraints

- All final Obsidian writes must go through `obsidian-cli`.
- Do not write to Obsidian before showing the proposed folder structure and file list.
- The user must be able to revise folder names, note names, tags, and category placement through the conversation.
- Support both single-file input and directory input.
- Follow MinerU's supported input formats instead of maintaining a separate hardcoded format list.
- Do not hardcode private paths or project-local virtual environment paths.

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
- whether a `.base` file is needed

After confirmation, the skill writes notes into the active vault and updates long-lived category indexes instead of creating one-off batch-only records.

## Workflow

### Step 1: Detect input

Accept either:

- one file path
- one directory path

For directory input, preserve the meaningful parts of the source hierarchy for later storage planning.

### Step 2: Convert with MinerU

Convert the input into Markdown and related assets with MinerU. Keep intermediate outputs inside `tmp/` or another disposable working location.

### Step 3: Plan Obsidian storage

Read [references/storage-planning.md](references/storage-planning.md).

Build a storage proposal before any write.

### Step 4: Confirm with the user

Do not write yet. Present the proposal and wait for explicit confirmation.

The user may revise:

- folder names
- file names
- category placement
- index structure
- tags
- related-note links

### Step 5: Write to Obsidian

After confirmation:

- format notes according to `obsidian-markdown`
- create or update notes through `obsidian-cli`
- create or update `.base` files only when they improve long-term navigation

### Step 6: Maintain indexes and links

Maintain long-lived category indexes. Connect imported notes to their categories through tags and wikilinks, and add related-note sections where the content relationship is strong.

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
