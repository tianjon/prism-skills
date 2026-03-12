# Storage Planning

## Purpose

Use this reference to decide where converted notes should live in Obsidian and how indexes, tags, and links should be maintained.

## Planning Inputs

Plan storage from both:

- document content
- source directory structure

For a directory import, do not blindly mirror the source tree. Preserve meaningful hierarchy, but reorganize when content-based grouping improves long-term navigation.

## Project-Specific Taxonomy

This skill does not enforce any fixed vault taxonomy by default.

If the current project already has a documented folder taxonomy, use it only after confirming that it applies to the current import.

## Proposed Write Plan

Before writing, produce a proposal containing:

- target folder tree
- note titles
- file paths
- files to create
- files to update
- category index notes
- tag scheme
- related-note links
- attachment folders to create or update
- asset reference rewrite plan
- optional `.base` files

## Index Strategy

Indexes are category-oriented and long-lived.

Recommended index layers:

- category root index
- optional subcategory index
- optional `.base` view for browsing

## Tag Strategy

Use stable tags. Prefer a small, reusable scheme over one-off tags.

Suggested dimensions:

- topic
- source type
- document state
- project or collection membership when needed

## Link Strategy

Every imported note should link to:

- its category index
- directly related notes when the relationship is obvious

Category indexes should link back to note members so backlinks remain useful.

## Asset Strategy

Treat MinerU-extracted assets as part of the import, not as disposable leftovers.

Planning rules:

- preserve extracted images by default unless the user explicitly chooses to omit them
- keep attachment placement stable and predictable inside the vault
- when practical, co-locate a note's assets with that note or in a clearly named sibling attachment folder
- rewrite relative asset references so they resolve after import in Obsidian
- if assets are intentionally omitted, say so explicitly in the proposal instead of silently dropping them

Verification rules:

- count notes with asset references before writing
- verify those references still resolve after writing
- verify attachment files exist at the final vault paths

## Ambiguity Handling

If classification is ambiguous, present 2-3 concrete placement options before writing.

The user can revise:

- folder placement
- note names
- category names
- tags
- index structure
- attachment placement
- asset preservation policy
