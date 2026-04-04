# Analysis Framework

Extraction and synthesis reference for `prism-brand-launch-research`.

## Per-Event 7-Field Extraction Table

Extract these fields for every event that passes the Round 2 deep-read threshold. Mark missing fields `待确认` — never infer or fill from adjacent events.

| Field | Chinese label | What to capture | If missing |
|-------|---------------|-----------------|------------|
| 产品角色 | Product role | See role classification below | `待确认` |
| 三电变化 | Three-electric changes | Battery capacity (kWh), range (km, CLTC), peak charge rate (kW), motor power/torque (kW/N·m) | `待确认` |
| 智驾变化 | Smart driving changes | Feature tier (L2/L2+/城市NOA/全场景NOA), hardware platform name, key OTA notes | `待确认` |
| 配置增减 | Configuration delta | Named features added or removed vs. the immediately prior trim set | `待确认` |
| 定价变化 | Pricing delta | Starting price (万元) + direction vs. prior (↑/↓/持平/全新定价) | `待确认` |
| 目标人群信号 | Audience signal | Official scenario language, color/interior options, spokespersons, co-branding | `待确认` |
| 企业战略信号 | Enterprise signal | Executive statements, brand tagline changes, launch venue scale, partner announcements | `待确认` |

## Product Role Classification

Assign exactly one role per product announced at the event. When a single event covers multiple products, each gets its own role assignment.

| Role | 中文 | Criteria |
|------|------|---------|
| Flagship | 旗舰款 | Highest trim, sets technical ceiling for the brand or series |
| Volume driver | 走量款 | Mid-range pricing targeting mainstream buyers; expected to represent highest unit sales |
| Gap filler | 补位款 | Fills a price or body-style gap in the existing lineup |
| Market test | 试水款 | New segment, body style, or powertrain the brand has not offered before |
| Limited edition | 限定款 | Capacity-constrained or time-limited release, not part of regular lineup |

## Three-Electric Change Dimensions

When extracting 三电变化, always record as delta vs. the predecessor if one exists:

- **Battery:** capacity (kWh), chemistry (LFP / NMC / other), supplier if disclosed
- **Range:** CLTC value (km); note if WLTP is given instead
- **Charging:** peak DC rate (kW), 10–80% time (min) if disclosed
- **Motor:** system power (kW), peak torque (N·m), drive configuration (FWD / RWD / AWD)
- **Range-extender (EREV only):** engine displacement, fuel tank capacity (L), fuel consumption (L/100km NEDC)

## Smart Driving Change Dimensions

- **Feature tier:** L2 / L2+ / 城市NOA / 高速NOA / 全场景NOA / 代客泊车 (VP)
- **Hardware platform:** chip name and generation (e.g., 地平线J6P, 英伟达Thor, 华为MDC)
- **Sensor suite:** camera count, lidar (yes/no + units), radar count
- **OTA:** whether the announced feature is hardware-ready OTA or requires hardware upgrade
- **Coverage:** city count or road type coverage at launch

## Strategic Synthesis: 5 Dimensions

Use these five dimensions to synthesize patterns across events into the brand-level strategic analysis. Populate only dimensions supported by event evidence.

| Dimension | 中文 | What it reveals |
|-----------|------|----------------|
| 同价做强 | Compete at price parity | Brand improves spec-per-yuan faster than segment average |
| 体验做开 | Differentiate on experience | Brand builds moats in software, interior, or ownership experience |
| 场景做准 | Own a scenario | Brand focuses product and marketing on specific use cases (family road trip, city commute, etc.) |
| 上游做稳 | Stabilize upstream | Brand verticalizes battery, chip, or motor supply to reduce cost or lock in spec advantage |
| 竞争压力应对 | Respond to competitive pressure | Brand adjusts pricing, configuration, or positioning in reaction to named competitor moves |

## Strategy Recommendation Format

Every strategy recommendation in `02-战略演进分析.md` must follow this format and be grounded in at least one specific event from the timeline:

```
【暴露点: <what the event evidence shows as a gap or risk>
 影响范围: <which products, price bands, or customer segments are affected>
 建议动作: <concrete action the brand could take>
 紧迫度: 高/中/低】
```

Urgency rules:
- **高**: Competitor has already moved; gap is visible to consumers now
- **中**: Trend is directional but gap is not yet consumer-facing
- **低**: Structural risk that requires monitoring, no immediate pressure

## Missing Data Handling

- If an event article exists but a specific field is not mentioned, mark `待确认`
- If no article can be retrieved for an event, mark all 7 fields `待确认` and note "原文不可访问"
- Do not copy values from adjacent events (e.g., same trim, prior month) to fill gaps
- A `待确认` field is always preferable to a fabricated value
