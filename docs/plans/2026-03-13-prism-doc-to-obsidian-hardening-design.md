# Prism Doc To Obsidian Hardening Design

## Goal

Harden `prism-doc-to-obsidian` so recursive document conversion is complete, MinerU-extracted assets are preserved into the vault, and long note writes are stable under `obsidian-cli`.

## Scope

- Recursively discover supported input files from either a single file or a directory.
- Run MinerU once per direct-parent batch instead of assuming MinerU will recurse correctly.
- Mirror conversion outputs under `tmp/` so same-named files from different source folders do not collide.
- Emit a manifest that preserves `source_rel_path -> markdown_path -> assets_dir -> target_note_rel_path`.
- Import notes into Obsidian from the manifest using deterministic target paths.
- Rewrite `![](images/...)` into `![[images/...]]`.
- Preserve extracted assets by default and copy them into stable vault `images/` folders.
- Chunk long note writes through `obsidian create` + `obsidian append inline`, then read back for verification.

## Non-Goals

- No new third-party Python dependencies.
- No binary attachment writes through `obsidian-cli`.
- No attempt to infer bespoke note names or folder names from document semantics inside the backend scripts.

## Architecture

### Stage 1: Recursive Conversion

`scripts/convert_recursive.py` is the orchestration entrypoint for conversion.

It uses reusable helpers in `lib/conversion.py` to:

- discover supported inputs recursively
- group source files by direct parent directory
- compute mirrored output roots under `tmp/`
- resolve the generated Markdown path for each source file
- build manifest entries with deterministic import-relative targets

The manifest is the contract between conversion and import. If a discovered file does not appear in the manifest, conversion fails.

### Stage 2: Deterministic Import

`scripts/import_to_obsidian.py` imports only from the manifest plus `--target-root`.

It uses reusable helpers in `lib/obsidian_import.py` to:

- rewrite Markdown image links to Obsidian embeds
- plan deterministic target note and `images/` paths
- copy all extracted assets into the final vault location
- validate that referenced assets exist
- write note bodies through `obsidian-cli`
- read the note back and verify the final content

Binary assets are copied directly into the vault because `obsidian-cli` only supports text content. This is the only write-path exception.

## Storage Rules

- Default note layout is per-note isolation: `<target-root>/<source-relative-parent>/<note-dir>/<stem>.md`.
- Default asset layout is `<target-root>/<source-relative-parent>/<note-dir>/images/`.
- If two source files share the same parent directory and stem, the note directory is disambiguated with `__<ext>`.
- Re-runs overwrite the same note path and asset file paths.

## Verification

Focused automated tests must cover:

- recursive discovery
- collision-free manifest generation
- embed rewrite behavior
- asset copying
- broken-reference failure
- chunked write plus read-back verification
- manifest-driven import behavior

Manual validation remains necessary for a real MinerU run and a live Obsidian vault session.
