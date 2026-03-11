# Open Source License And README Design

## Goal

Convert the repository from a non-commercial source-available posture to a standard MIT-licensed public repository and align the README with common open-source expectations.

## Scope

- Replace the custom non-commercial license with MIT
- Rewrite README so it no longer describes the project as source-available or usage-restricted
- Add the basic sections expected in a public GitHub repository
- Keep the technical installation and skill descriptions accurate

## Non-Goals

- No changes to runtime code or skill behavior
- No new automation or release tooling
- No repository restructuring outside `README.md` and `LICENSE`

## Design

### License

Use the standard MIT License text with the current copyright holder.

### README

The README should:

- describe the repository in one short opening section
- list the available skills and what each is for
- explain supported agent environments
- provide installation steps with HTTPS clone commands
- provide quick start examples for both skills
- describe the repository layout
- explain how to contribute
- link to the MIT license

### Content to remove

- all non-commercial warnings
- all source-available wording
- all usage restriction sections
- maintainer-only Git identity instructions

## Validation

- `LICENSE` starts with `MIT License`
- `README.md` no longer contains `non-commercial`, `source-available`, or `Usage Restrictions`
- `README.md` contains a `Contributing` section and a `License` section
