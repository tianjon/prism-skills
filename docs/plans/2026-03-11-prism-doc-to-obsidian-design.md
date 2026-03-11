# MinerU To Obsidian Design

## Goal

Create a second local skill that converts MinerU-supported documents into Markdown, plans an Obsidian destination structure, and writes confirmed results into the active vault through `obsidian-cli` while maintaining long-term indexes, tags, and cross-note links.

## Scope

- Support a single file input
- Support a directory input
- Follow MinerU's supported input formats instead of hardcoding a separate format list
- Verify local Python and Obsidian CLI requirements before work starts
- Auto-install MinerU and trigger model download when missing
- Auto-install missing `obsidian-markdown`, `obsidian-bases`, and `obsidian-cli` skills
- Propose folder structure and file list before writing anything to Obsidian
- Let the user revise the proposed structure through conversation
- Maintain topic-oriented indexes instead of batch-only indexes

## Non-Goals

- No full Python orchestration pipeline in v1
- No hardcoded private environment paths
- No direct filesystem write path that bypasses `obsidian-cli`
- No project-specific document taxonomy in the public skill contract

## Design

### Execution model

The skill is prompt-first. `SKILL.md` is the main control surface. It orchestrates existing tools and skills instead of introducing a custom runtime pipeline.

The skill uses this sequence:

1. Check Python version and Obsidian CLI availability
2. Stop if either base requirement is missing or too old
3. Check MinerU availability and install it if needed
4. Trigger MinerU model download if needed
5. Check for `obsidian-markdown`, `obsidian-bases`, and `obsidian-cli`; install missing skills
6. Convert input documents with MinerU
7. Build a proposed Obsidian folder tree and file list
8. Present the plan for user confirmation and allow conversational edits
9. Write confirmed notes into the active vault through `obsidian-cli`
10. Update topic indexes, tags, and wikilink relationships

### Obsidian write strategy

All final note creation and updates go through `obsidian-cli`.

`obsidian-markdown` governs note formatting. `obsidian-bases` is used only when a durable category view materially improves navigation. `obsidian-cli` is the required final write path.

### Storage planning

The skill does not write immediately after conversion. It first proposes:

- target folder tree
- files to create or update
- topic indexes to maintain
- tag scheme
- cross-note links

The proposal combines document content and input directory structure. Project-specific taxonomy should stay outside the public skill contract.

### Index maintenance

Indexes are topic-oriented and long-lived. Each imported note should link to its category index, and each category index should link back to the note set. Where useful, `.base` files provide durable browsable views over a category.

## Deliverables

- `skills/prism-doc-to-obsidian/SKILL.md`
- `skills/prism-doc-to-obsidian/references/install-and-checks.md`
- `skills/prism-doc-to-obsidian/references/storage-planning.md`
- `skills/prism-doc-to-obsidian/references/prompt-templates.md`
- `skills/prism-doc-to-obsidian/tmp/.gitkeep`

## Risks

- Obsidian CLI behavior depends on the desktop app being installed, new enough, enabled for CLI use, and running
- MinerU install and model download may vary by network environment
- Topic classification may be ambiguous for mixed-content directories

## Validation

- Confirm the new skill directory exists with the expected files
- Check that `SKILL.md` references the support files and keeps project-specific preferences out of the public contract
- Check that the workflow enforces confirmation before any Obsidian write
- Check that no private path or `.venv` path is hardcoded
