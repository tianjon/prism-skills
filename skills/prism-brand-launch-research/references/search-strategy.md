# Search Strategy

Search strategy reference for `prism-brand-launch-research`. Use with the Discovery Prompt in `prompt-templates.md`.

## Tool Selection by Round

| Round | Tool | Purpose |
|-------|------|---------|
| Round 1 — Discovery | `WebSearch` | Broad search: auto news sites, press releases, official announcements |
| Round 2 — Deep read | Perplexity API (`curl`) | Deeper web search and full article extraction; uses `$PERPLEXITY_API_KEY` |
| Round 3 — Social listening | `agent-reach` (小红书 + 汽车之家/懂车帝 + B站 + 微信公众号) | Post-launch user voices, feedback, sentiment |

## Round 1: Discovery Search Query Templates

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

## Round 3: Social Listening Query Templates

Use `agent-reach` across four channels. Execute after the timeline is built; one pass per key event. Query window: 0–4 weeks after the event date.

**小红书（`xhs search`）:**
```
"<品牌> <车型名> 发布会 感受"
"<品牌> <车型名> 值不值得买 <年份>"
"<品牌> <车型名> 槽点"
```

**汽车之家论坛 + 懂车帝口碑区（Jina Reader）:**
```bash
# 汽车之家论坛帖子搜索（Exa 或 Jina）
curl -s "https://r.jina.ai/https://club.autohome.com.cn/bbs/forum-search?q=<品牌>+<车型名>&sort=time"
# 懂车帝口碑区
curl -s "https://r.jina.ai/https://www.dongchedi.com/auto/series-evaluate?keyword=<车型名>"
```

**B站（bilibili API）:**
```bash
# 搜索发布会/评测视频及评论
curl -s "https://api.bilibili.com/x/web-interface/search/all/v2?keyword=<品牌>+<车型名>+发布会&page=1"
```

**微信公众号（Exa search）:**
```
mcporter call 'exa.web_search_exa(query: "<品牌> <车型名> 发布会 评测 site:mp.weixin.qq.com", numResults: 5)'
```

Extract per event:
- 高频好评主题（≥3 posts mentioning same point）
- 高频差评主题（≥3 posts mentioning same point）
- 整体情绪倾向：正面 / 中性 / 负面
- 代表性引用（原文摘录 + 链接 + 来源平台）

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

## Sales Analysis: Obsidian Read Strategy

Sales data lives at `汽车/销量Wiki/` in Obsidian. Use `obsidian` to read; do not web-search for sales figures.

**Steps:**
1. Search the wiki for brand and model entries: `obsidian search query="<品牌> 销量" path="汽车/销量Wiki"`
2. Read relevant monthly sales notes covering the 6-month window before and after each key event date
3. Extract: 品牌总销量（月度）/ 车型销量（月度）/ 数据来源说明

**Analysis window per event:** `-6 months` to `+6 months` relative to event date

**Metrics to compare:**
- 品牌月度总销量趋势（↑/↓/持平）
- 发布车型月度销量趋势
- 发布当月与前月的环比变化
- 发布后第3个月与第6个月的趋势方向

If the wiki has no data for a model or period, mark `数据缺失` — do not estimate.
