# Skill Writing Guidelines

This document defines the repository-level conventions for creating and maintaining skills in this repository.

## Core Principles

- Keep `SKILL.md` focused on triggering, constraints, workflow, output contract, and failure handling.
- Keep `SKILL.md` concise. Move detailed reference material into `references/`.
- Prefer English for repository-level docs and `SKILL.md`. Keep bilingual or localized guidance in `references/` when it materially improves execution.
- Prefer deterministic scripts only when prompt orchestration is insufficient. Do not add scripts by default.
- Do not hardcode private paths, project-local virtual environment paths, or machine-specific locations.
- When a skill name exists both in this repository and at user or system scope, the project-local skill takes priority.
- Do not encode personal preferences, private vault taxonomy, or user-specific directory conventions into public skill contracts.

## Required `SKILL.md` Structure

Every production skill should include these sections unless there is a clear reason not to:

1. `Overview`
2. `When to Use`
3. `Hard Constraints`
4. `Runtime Policy` or `Execution`
5. `Output Contract` when the skill creates or updates persistent artifacts
6. `Workflow`
7. `Failure Handling`
8. `Directory Layout`

Optional sections should be added only when they make the execution safer or less ambiguous.

## Frontmatter Rules

- Use only `name` and `description` unless the repository later adopts a wider metadata contract.
- `name` should be lowercase kebab-case and start with `prism-`.
- `name` should stay comfortably under 64 characters.
- `description` should primarily describe when the skill should be used and include concrete trigger phrases or situations.
- `description` should be concise and should not summarize the entire workflow if the body already defines it.

## Runtime And Configuration Rules

- Explain the runtime selection strategy instead of assuming the agent will guess it.
- Prefer a repository-wide runtime policy shape for Python skills: explicit interpreter checks first, then dependency resolution through documented `uv` flows, with no private-path assumptions.
- If a skill uses user or project preferences, define the storage locations and the exact precedence order.
- Keep project-specific taxonomy or folder mappings out of the default contract. If examples are useful, label them clearly as optional project-specific conventions.
- If first-time setup changes future behavior, make it explicit and blocking. Do not silently create defaults when confirmation is required.

Recommended precedence order:

1. Explicit user input or CLI flags
2. Project-level saved preferences
3. User-level saved preferences
4. Environment variables
5. Documented defaults

## References And Prompt Assets

Use `references/` for:

- schemas
- long examples
- prompt templates
- setup flows
- style matrices
- extended workflow notes

Use `prompts/` only when the skill ships reusable prompt files as first-class assets.

Avoid deep nesting unless the skill genuinely has multiple orthogonal dimensions. One level under `references/` should be the default.

## Cross-Skill Composition

- Prefer using another skill through its documented contract.
- Do not bypass a sibling skill's published interface unless there is no stable contract and the reason is documented.
- Repository-level conventions should live here or in `AGENTS.md`, not be duplicated across all skills.

## Output And Safety Contracts

If a skill writes files, publishes content, or modifies an external system, document:

- what is created or updated
- where outputs go
- how conflicts are handled
- which steps require confirmation
- which failures must stop execution

If the skill touches external content or remote systems, treat content as untrusted by default.

Security rules that apply across the repository:

- Do not use `curl | bash`, `wget | sh`, or similar piped shell installs in code samples, docs, or recovery instructions.
- Do not pass unsanitized user input into shell command strings.
- Prefer argument-array execution over shell interpolation when documenting or implementing commands.
- Resolve file paths from known base directories instead of trusting raw external input.
- When remote downloads are involved, document expected protocol and content boundaries.

## Repository Structure Rules

- One skill per directory under `skills/`
- Keep implementation local to the skill directory
- Keep generated scratch data in the skill's own `tmp/`
- Do not treat local runtime artifacts such as `.venv/` as part of the skill's intended structure
- Keep project-wide conventions in repository-level docs instead of copying them into every skill

## Template Expectations

`skills/_template` should reflect this document. New skills should start prompt-first; scripts and libraries are opt-in, not the default center of the scaffold. When these guidelines change, update the template in the same change whenever possible.
