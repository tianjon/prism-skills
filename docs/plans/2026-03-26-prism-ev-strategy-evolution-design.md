# Prism EV Strategy Evolution Design

## Goal

Create a new prompt-first local skill that reads one brand's automotive notes from Obsidian, analyzes three-electric strategy evolution across all models including discontinued ones, separates pure EV and range-extended EV routes, and writes structured analysis notes back into Obsidian.

## Scope

- Add a new skill under `skills/prism-ev-strategy-evolution/`
- Keep the skill reasoning-led and prompt-first
- Use `obsidian-cli` as the required read and write path
- Cover brand-wide analysis plus per-model analysis
- Split `纯电` and `增程` as first-class analysis axes
- Explain timeline evolution, brand stages, price/configuration relationships, and configuration/vehicle-mass relationships
- Store outputs under `汽车/配置分析/三电分析/$品牌名`

## Non-Goals

- No deterministic scoring engine in v1
- No hardcoded rule parser that attempts to replace agent reasoning
- No requirement to introduce Python scripts unless prompt orchestration proves insufficient
- No bypass of Obsidian through direct filesystem writes as the default workflow

## Design

### Skill posture

The skill should behave like an analyst workflow, not a data pipeline. `SKILL.md` is the main runtime contract. Detailed analysis frames and prompts live in `references/`.

### Source and destination

Source notes come from `汽车/品牌库/$品牌名/...` through `obsidian-cli`.

Destination notes go to:

- `汽车/配置分析/三电分析/$品牌名/00-品牌三电策略总报告.md`
- `汽车/配置分析/三电分析/$品牌名/01-分析方法与口径.md`
- `汽车/配置分析/三电分析/$品牌名/车型清单与阶段映射.md`
- `汽车/配置分析/三电分析/$品牌名/车型分析/$车型名.md`

### Analysis layers

The reasoning frame should always cover:

- brand stage
- timeline evolution
- pure EV route
- range-extended EV route
- price/configuration relationship
- configuration/vehicle-mass relationship
- discontinued models as evidence of strategic migration

### Reference assets

The skill should ship:

- one main `SKILL.md`
- one analysis framework reference
- one prompt template reference
- one Obsidian workflow reference

## Validation

- `skills/prism-ev-strategy-evolution/SKILL.md` exists and follows repository skill sections
- references cover analysis axes, prompt templates, and Obsidian workflow
- repository indexes mention the new skill
- dedicated tests validate the skill contract and references
