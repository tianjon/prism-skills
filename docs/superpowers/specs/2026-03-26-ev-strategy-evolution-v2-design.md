# Design: prism-ev-strategy-evolution v2 + dongchedi historical data

## Background

The current `prism-ev-strategy-evolution` skill produces analysis that explains
*configurations* rather than *decisions*. Outputs follow a rigid 14-chapter
template that reads like a structured report rather than a brand story. The
competitive benchmarking tables are mechanical. Conclusions lack the depth and
narrative that would make someone want to keep reading.

The user wants analysis that:
1. Reconstructs strategic *decisions*, not just describes parameters
2. Reads like a brand story told through key turning points
3. Uses the complete timeline — no update skipped — as the analytical foundation

A secondary discovery: `prism-dongchedi-scraper` does not capture historical
trims within active series, and its history cutoff (default 2024) drops data
from brand founding years. Strategy analysis depends on that missing data.

This document covers both skills.

---

## Part A — prism-ev-strategy-evolution v2

### Core shift

| Before | After |
|---|---|
| Subject is the car model | Subject is the brand's decision |
| Configurations are the analysis | Configurations are evidence for decisions |
| 14-chapter template | 4-part narrative structure |
| Competitive tables (领先/持平/落后) | Competitive context embedded in turning point narrative |
| Recommendations as product tickets | Open strategic questions with genuine tension |

---

### A1 — Brand report structure (replaces 14-chapter template)

**Part 0 — 品牌弧线**

One paragraph, ≤200 characters. Answers: where did the brand start, what did
they bet on, what did they pay for it, where do they stand now. A reader who
finishes this paragraph should understand the brand's core strategic fate line
without needing to read further.

**Part 1 — Turning points (3–5 chapters)**

Each chapter covers one genuine strategic turning point. Chapter title format:

```
## [YYYY]｜[action phrase]
```

Example: `## 2024｜把快充押注在走量车上，旗舰暂时按兵不动`

Each chapter has exactly four layers in this order:

| Layer | Content | Key constraint |
|---|---|---|
| 背景压力 | What changed in the competitive landscape that made this decision urgent | Must name a specific competitor move or market signal; "竞争加剧" is not acceptable |
| 决策 | What the brand did AND what they explicitly chose not to do | Both sides required; listing only the upside is incomplete |
| 配置证据 | Minimum parameters that prove the interpretation | Embedded in prose, not a standalone table; evidence must be falsifiable ("if my reading were wrong, this number would look different") |
| 代价与锁定 | What they won, what they lost, which future options became harder | Must be specific; no generic statements; this layer is the source of analytical depth |

**Part 2 — 今日处境**

Narrative paragraph first. Then one competitive position table (serves the
narrative, is not the narrative). Covers where the brand stands as the product
of all turning points.

**Part 3 — 悬而未决的赌注**

1–2 open strategic questions. Format: not a recommendation list, but a genuine
dilemma where both acting and not acting carry real costs. The question must
have two visible sides or it is not a real dilemma.

Example of an acceptable question:
> 阿维塔现在的局面是：12 旗舰纯电还在用旧平台，而自家增程版已经快了 2 倍。要么
> 在旗舰续航叙事崩塌之前推出新平台纯电，要么任由增程版从内部侵蚀市场空间。
> 问题不是他们知不知道——而是能不能在时间窗口关闭之前执行。

---

### A2 — Analytical framework

#### Turning point identification criteria

A moment qualifies as a turning point if it meets **at least one** of these:

| Type | Signal |
|---|---|
| Architecture jump | New charging platform, voltage architecture, or powertrain route introduced for the first time |
| Price band break | Entry price shifts >20%, or brand enters/exits a new segment |
| Platform split | Flagship and volume cars use different-generation platforms and sell in parallel |
| Supply chain reset | Primary supplier changes, or new vertical integration / JV supply structure appears |
| Route abandonment | All models on a powertrain route discontinued with no replacement |
| Strategic self-contradiction | A cheaper model has demonstrably better three-electric capability than a more expensive one |

The following do NOT qualify as turning points:

- Annual refreshes with incremental parameter changes
- Adding or removing a trim level
- OTA upgrades
- Price adjustments ≤10%

#### The subject of each turning point is a decision, not a vehicle

> ❌ "阿维塔06 搭载神行超充 5C，0.17h 快充，22–27 万走量区间"
>
> ✅ "2025 年，阿维塔选择让走量车先上新平台，旗舰暂时维持旧架构" — 06 is the
> evidence for this decision, not the subject of the analysis.

#### Turning point count rules

- Minimum 3, maximum 5
- Fewer than 3: evidence is too sparse; output only an evidence map with gaps noted
- More than 5 candidates: choose the 5 with the highest brand-level strategic significance; demote the rest to background context within the nearest turning point

---

### A3 — Workflow (5 steps, strict order)

Steps must be executed in sequence. Step N cannot start until step N−1 is complete.

```
Step 1  Full read        Read all trim notes for all models including discontinued
Step 2  Per-model timeline  Build a timeline for each model with all versions annotated
Step 3  Brand timeline   Merge all model timelines into one chronological brand record
Step 4  Pattern recognition  Answer 4 pattern questions against the complete timeline
Step 5  Write report     Derive turning points from patterns; write brand story
```

#### Step 1 — Full read

Primary data source is the trim-level configuration note for each model version.
The `上市时间` field in each note is the backbone of the timeline.

```bash
# Current trims
obsidian read path="汽车/品牌库/$品牌名/$车型名/当前款型/*.md"

# Overview (for discontinuation signals)
obsidian read path="汽车/品牌库/$品牌名/$车型名/00-车型总览.md"

# Enumerate all notes under brand root to catch archived models
obsidian search query="汽车/品牌库/$品牌名" limit=300
```

Update record folders (`更新记录/`) should be read if they exist and contain
content. They are supplementary; not a required source.

Coverage check before proceeding: can you answer "how many models has this brand
ever sold, and how many times was each model refreshed?" If not, continue reading.

#### Step 2 — Per-model timeline prompt

```
为 [车型名] 建立完整时间轴。

包含：所有上市/改款/停售节点。
每个节点只记录实质变化的字段（未变动字段不列出）。
每个节点打一个标注：
  技术进步 / 配置重分配 / 降价防御 / 路线调整 / 停售

格式：
[YYYY-MM] 事件标题
  变化内容：[仅发生变化的字段]
  标注：[类型]
  备注：[供应商变化、路线新增/删除等额外信息，如有]
```

Annotation definitions:

| Label | Meaning |
|---|---|
| 技术进步 | Parameters improved without proportional cost penalty (longer range, faster charging, same or lighter weight) |
| 配置重分配 | Capability moved between trims without net increase (flagship spec pushed down; or spec removed from entry and added to high trim) |
| 降价防御 | Price cut without configuration change, or configuration upgrade with large simultaneous price cut |
| 路线调整 | Powertrain route added, removed, or redefined |
| 停售 | Note discontinuation date and whether a replacement model exists |

#### Step 3 — Brand timeline

Merge all per-model timelines into a single document sorted by date. Write to:

```
汽车/配置分析/三电分析/$品牌名/品牌完整时间线.md
```

This file records facts only. No analysis. It is the single source of truth for
all subsequent analysis and the brand report.

#### Step 4 — Pattern recognition prompt

```
基于 [品牌名] 品牌完整时间线，依次回答以下4个问题。
每个问题必须以具体事件为支撑，不允许泛化表述。

1. 频率模式
   哪些时期改款密集（≥3款车型在6个月内同时调整）？
   哪些时期静默（>12个月无实质改款）？
   密集期前后，竞争格局发生了什么变化？

2. 方向一致性
   是否有某个时期，多数车型同时朝同一方向变化（同时降价、同时推增程、
   同时换供应商、同时刷新平台）？
   这种同向变化说明品牌做了什么品牌级决策？

3. 内部矛盾
   是否有车型的变化方向与同期其他车型相反？
   （例：旗舰维持旧平台，走量车升级新平台）
   矛盾暴露了什么约束或摇摆？

4. 停售规律
   哪类车型最先退出（路线/价格段/车身形态）？
   停售之后有没有同定位替代车型？
   停售节点是否与竞品动作或自身新车发布重合？
```

#### Step 5 — Brand story writing prompt

```
基于模式识别结论，写品牌三电策略演进报告。

第一步：从模式中提炼3-5个转折点。
转折点必须是品牌级战略选择，不是单车型产品调整。
选完后说明为什么选这几个，并说明排除了哪些候选。

第二步：按以下结构写报告。

--- Part 0 品牌弧线 ---
一段话，200字以内。
说清：从哪里出发 → 赌了什么 → 付出什么代价 → 今天站在哪里。
读完这段话，读者已经知道这个品牌最核心的一条战略命运线。

--- Part 1 转折点（每个单独一章）---
章节标题：## [YYYY]｜[动作短语]

每章四层，顺序不能打乱：
  背景压力：此前竞争格局发生了什么，是什么让这个决策变得紧迫？
            必须提到具体竞品动作或市场变化；"竞争加剧"不算。
  决策：品牌做了什么，同时放弃了什么。两面都要写。
  配置证据：用最少的参数证明判断，嵌在叙事里，不单独成表。
            证据要有区分力——如果解读错了，这个数字会是什么样？
  代价与锁定：赢了什么，输掉了什么，未来哪条路因此变得更难走？
             必须具体；不能泛化。

--- Part 2 今日处境 ---
先写一段叙述，再附竞争位置表（表服务于叙事，不是主角）。

--- Part 3 悬而未决的赌注 ---
1-2个开放式战略问题。
不是建议，是困境。问题必须有两面：做和不做各有代价。
```

---

### A4 — Per-model notes (simplified)

Per-model notes become supporting references, not primary analysis.

**Purpose:** Provide the complete configuration record for one model that the
brand report can reference. Not a standalone analytical document.

**Structure:**

1. 车型角色一句话（在品牌故事中扮演什么角色）
2. 完整配置时间轴（从 Step 2 直接引用，带标注）
3. 关键配置参数表（当前在售款型，供查阅用）

No per-model competitive benchmarking section. Competitive context lives in the
brand report's turning point layers.

---

### A5 — Output contract changes

| File | Change |
|---|---|
| `00-品牌三电策略总报告.md` | Full rewrite to 4-part turning point structure |
| `品牌完整时间线.md` | **New** — replaces 车型清单与阶段映射 |
| `01-分析方法与口径.md` | Keep; update coverage-standard description |
| `车型分析/$车型名.md` | Simplified to role statement + timeline + param table |

---

## Part B — prism-dongchedi-scraper historical data

Three problems identified. Two require code changes; one requires documentation only.

### B1 — Historical trims not fetched for active series (code change)

**Current behavior** (`configs.py`):

```python
series_is_history = include_history and (
    "停售" in str(series.get("price_range", "")) or series.get("is_history")
)
configs = extract_car_configs(ssr_data, include_history=series_is_history)
if series_is_history:
    configs = filter_recent_history_configs(configs, cutoff_year=history_cutoff_year)
```

Historical trims are only fetched when the *series itself* is marked discontinued.
Discontinued trims within an active series are never fetched.

**Fix:**

```python
configs = extract_car_configs(ssr_data, include_history=include_history)
if include_history:
    configs = filter_recent_history_configs(configs, cutoff_year=history_cutoff_year)
```

`DONGCHEDI_INCLUDE_HISTORY` is already set to `"1"` by default in
`run_brand_pipeline.py`, so this fix activates for all pipeline runs.

### B2 — History cutoff too recent (code change)

**Current behavior** (`run_brand_pipeline.py`):

```python
env["DONGCHEDI_HISTORY_CUTOFF_YEAR"] = str(
    datetime.now().year - args.history_window_years + 1
)
# history_window_years default = 3 → cutoff = 2024
```

Brands that launched in 2022 lose their founding-year data.

**Fix:** Support `--history-window-years 0` to mean no cutoff.

```python
if args.history_window_years > 0:
    env["DONGCHEDI_HISTORY_CUTOFF_YEAR"] = str(
        datetime.now().year - args.history_window_years + 1
    )
# else: do not set DONGCHEDI_HISTORY_CUTOFF_YEAR
```

In `configs.py`, the `filter_recent_history_configs` call needs to handle the
missing env var:

```python
history_cutoff_year = int(os.environ.get("DONGCHEDI_HISTORY_CUTOFF_YEAR", "0"))
# 0 means no cutoff
```

And `filter_recent_history_configs` must pass through all configs when
`cutoff_year=0`.

**EV strategy analysis should use `--history-window-years 0`.**

### B3 — Fully discontinued series not discoverable (documentation only)

Dongchedi search returns only currently listed series. A series that has been
fully removed from the platform cannot be found automatically.

**No code change.** Document the workaround in `SKILL.md`:

When running the pipeline for EV strategy analysis, manually seed discontinued
series using `--series-seed-file`. Set `is_history: true` in the seed entry so
the pipeline fetches historical trims.

```json
[
  {
    "series_id": "1234",
    "name": "品牌 早期型号",
    "price_range": "停售",
    "level": "中型车",
    "energy_type": "纯电动",
    "brand": "品牌名",
    "is_history": true
  }
]
```

---

## Non-goals

- Do not change the dongchedi scraper's default `--history-window-years` (keep 3
  to avoid breaking routine brand monitoring runs)
- Do not redesign the per-model note format beyond what is described in A4
- Do not add scoring or deterministic rules to the ev-strategy skill
- Do not change the Obsidian path conventions

---

## Validation

- [ ] `prism-ev-strategy-evolution/SKILL.md` updated with new workflow and prompts
- [ ] `references/analysis-framework.md` updated with turning point criteria and
      4-layer structure
- [ ] `references/prompt-templates.md` updated with Step 2–5 prompts
- [ ] `references/obsidian-workflow.md` updated to reflect 5-step order
- [ ] `dongchedi-scraper/scripts/configs.py` fix applied and tested
- [ ] `dongchedi-scraper/scripts/run_brand_pipeline.py` `--history-window-years 0`
      support added and tested
- [ ] `dongchedi-scraper/SKILL.md` documents the seed-file workaround for
      discontinued series
- [ ] Existing analysis outputs in Obsidian are NOT retroactively modified by
      this change (new structure applies to future runs only)
