# Search Strategy

Search strategy reference for `prism-brand-launch-research`. Use with the Discovery Prompt in `prompt-templates.md`.

## Search Query Templates

Six base templates. Substitute `<品牌>` with the brand name (try both Chinese and English names if one yields sparse results) and `<年份>` with each year in the target range.

```
"<品牌> 发布会 <年份>"
"<品牌> 新车上市 <年份>"
"<品牌> 产品发布 战略 <年份>"
"<品牌> 发布会 site:autohome.com.cn"
"<品牌> 上市发布 site:dongchedi.com"
"<品牌> 发布 战略 site:36kr.com"
```

Additional queries when the first pass is sparse:

```
"<品牌> 改款 <年份>"
"<品牌> 换代 <年份>"
"<品牌> 上市 <车型名>"
"<品牌> 战略升级 <年份>"
```

## Source Priority

Higher priority sources tend to carry structured event reports with accurate dates and official pricing:

1. **汽车之家** (autohome.com.cn) — most comprehensive launch event coverage, structured spec tables
2. **懂车帝** (dongchedi.com) — strong on configuration detail and trim comparisons
3. **36氪汽车** (36kr.com) — best for strategy and enterprise-level analysis
4. **电动汽车之家** (evcar.com.cn) — strong on three-electric specifics for NEV brands
5. **品牌官网新闻页** — authoritative for dates and official language, thin on analysis
6. **其他媒体** (爱卡汽车, 易车, 汽车头条, 微信公众号) — use as supplementary corroboration

When two sources conflict on a date or spec, prefer autohome.com.cn or the brand's official press release.

## Round 2 Deep-Read Trigger Conditions

Retrieve and read the full source article when any one of these applies to an event in the coarse inventory:

1. **全新车型首发** — first appearance of a new model nameplate
2. **重大改款或换代** — generation change or mid-cycle facelift with structural changes
3. **战略、定价或人群变化** — article headline or snippet explicitly mentions strategy shift, price repositioning, or change in target audience
4. **三电或智驾有显著变化** — battery capacity ≥10% change, range ≥50 km change, new smart driving hardware platform, or new OTA feature set

Minor events (color additions, accessory packages, limited editions without mechanical changes) do not require deep reads unless the user requests comprehensive coverage.

## Information Quality Rules

Distinguish confirmed launch events from speculation before adding to the timeline:

| Signal | Classification |
|--------|---------------|
| Official launch event, press conference, or 上市发布会 with verifiable date | Confirmed — include |
| Manufacturer-issued press release or official pricing announcement | Confirmed — include |
| Media coverage of live event with photos, pricing, and configuration tables | Confirmed — include |
| Analyst prediction, spy shot report, or "预计上市" without confirmation | Exclude — not a launch event |
| Leaked configuration or pricing without official confirmation | Exclude — mark as 待确认 if directionally useful |
| Retrospective summary article covering multiple events | Use as a source index only, not as a primary event record |

## Time Period Slicing

When the date range exceeds 18 months, split queries into yearly slices to avoid search result truncation:

- For a 2022-01-01 to 2025-12-31 range, run four separate query passes: 2022, 2023, 2024, 2025
- Overlap slice boundaries by one month (e.g., December 2022 and January 2023) to avoid dropping events near year boundaries
- Record source URLs during discovery; do not wait for deep reads to capture them
