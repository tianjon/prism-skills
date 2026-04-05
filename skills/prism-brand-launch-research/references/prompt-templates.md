# Prompt Templates

Seven prompt blocks for `prism-brand-launch-research`. Execute in order. Substitute variables in `<角括号>` before use.

| Block | Round | Tool | Output dir |
|-------|-------|------|------------|
| Block 1 | Round 1 — Discovery | `WebSearch` | — |
| Block 2 | Round 2 — Deep read | Perplexity API (`curl`) | — |
| Block 3 | Round 3 — Social listening | `agent-reach` (小红书 + 汽车之家/懂车帝 + B站 + 微信公众号) | — |
| Block 4 | Sales analysis | `obsidian` (`汽车/销量Wiki/`) | — |
| Block 5 | Strategic synthesis | Reasoning only | — |
| Block 6 | Write-back (Markdown) | `obsidian` | `汽车/发布会研究/<品牌>/` |
| Block 7 | Wiki build | `obsidian` | `汽车/发布会Wiki/<品牌>/` |

---

## Block 1: Discovery Prompt（事件发现）

**Tool: `WebSearch`**

Use after writing the methodology note. Goal: build a coarse event inventory covering the full date range.

```
目标品牌: <品牌名>
时间范围: <开始日期> 至 <结束日期>

请按以下步骤搜索该品牌在此时间范围内的所有发布会与上市事件：

1. 对每个年份执行以下搜索（时间跨度超过 18 个月时按年分片）：
   - "<品牌> 发布会 <年份>"
   - "<品牌> 新车上市 <年份>"
   - "<品牌> 产品发布 战略 <年份>"
   - "<品牌> 发布会 site:autohome.com.cn"
   - "<品牌> 上市发布 site:dongchedi.com"

2. 如果以上结果偏少（少于 3 条），追加以下查询：
   - "<品牌> 改款 <年份>"
   - "<品牌> 换代 <年份>"
   - "<品牌> 战略升级 <年份>"

3. 对每条搜索结果判断：
   - 是官方发布会、上市活动、或媒体对现场发布的报道 → 纳入清单
   - 是预测稿、spy shot、"预计上市" → 排除
   - 是回顾性汇总文章 → 仅用于提取事件线索，不作为主记录

4. 输出事件粗清单，每条包含：
   - 事件 ID（E001, E002, ...）
   - 日期（YYYY-MM-DD 或 YYYY-MM）
   - 事件名称
   - 涉及产品名称
   - 信源 URL（至少 1 条）

如果某条没有可验证的信源 URL，标注"信源待确认"但仍保留该事件。
```

---

## Block 2: Deep-Read Prompt（深读提取）

**Tool: Perplexity API via `curl`（使用环境变量 `$PERPLEXITY_API_KEY`）**

Use for each event in the inventory that meets Round 2 criteria (see `search-strategy.md`). Goal: extract all 7 analysis fields via Perplexity's deep web search.

Before running: verify `$PERPLEXITY_API_KEY` is set — if missing, stop and ask the user to run:
```
export PERPLEXITY_API_KEY="<your-key>"
```

**Perplexity 调用模板（每个事件执行一次）：**

```bash
curl -s -X POST "https://api.perplexity.ai/chat/completions" \
  -H "Authorization: Bearer $PERPLEXITY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "sonar-pro",
    "messages": [
      {
        "role": "user",
        "content": "请深度搜索并阅读以下汽车发布事件的原始报道，提取 7 个字段（见下方格式）。\n\n事件: <事件名称>（<日期>）\n信源参考: <URL>\n品牌: <品牌名>\n\n<粘贴下方提取格式>"
      }
    ]
  }'
```

提取字段格式（粘贴进 content）：

```
事件: <事件名称>（<日期>）
信源: <URL>

请阅读以上链接的原文，提取以下 7 个字段。
字段缺失时标注"待确认"，不要从其他事件推断填充。

提取结果格式：

产品角色: <旗舰款 / 走量款 / 补位款 / 试水款 / 限定款>
三电变化:
  电池容量: <kWh，与上代相比 ±X kWh 或"全新车型">
  续航（CLTC）: <km>
  峰值充电功率: <kW>
  电机功率/扭矩: <kW / N·m>，驱动形式: <前驱/后驱/四驱>
智驾变化:
  功能级别: <L2 / L2+ / 城市NOA / 全场景NOA / 等>
  硬件平台: <芯片名称与代际>
  OTA说明: <硬件预埋/软件升级 或 待确认>
配置增减: <相比上代新增或删除的命名配置项，无则"无变化"或"待确认">
定价变化: <起售价（万元），方向 ↑/↓/持平/全新定价>
目标人群信号: <官方场景描述、配色/内饰倾向、代言人、联名等>
企业战略信号: <高管表态、品牌 slogan 变化、发布会规格、战略合作等>
信源质量: <高/中/低，原因一句话>
```

---

## Block 3: Social Listening Prompt（用户声音分析）

**Tool: `agent-reach`（平台：小红书 + 汽车之家/懂车帝 + B站 + 微信公众号）**

Use after building the event timeline. Execute once per key launch event. Query window: 0–4 weeks after event date.

```
目标品牌: <品牌名>
车型: <车型名>
事件日期: <YYYY-MM-DD>
搜索窗口: 发布后 0–4 周

请按以下顺序在 4 个平台搜索，每个平台至少执行 2 个查询：

【平台 1】小红书（xhs search）
- xhs search "<品牌> <车型名> 发布会 感受"
- xhs search "<品牌> <车型名> 值不值得买 <年份>"
- xhs search "<品牌> <车型名> 槽点"

【平台 2】汽车之家论坛 + 懂车帝口碑（Jina Reader）
- curl -s "https://r.jina.ai/https://club.autohome.com.cn/bbs/forum-search?q=<品牌>+<车型名>&sort=time"
- curl -s "https://r.jina.ai/https://www.dongchedi.com/auto/series-evaluate?keyword=<车型名>"

【平台 3】B站（bilibili API）
- curl -s "https://api.bilibili.com/x/web-interface/search/all/v2?keyword=<品牌>+<车型名>+发布会&page=1"
  （取 video 类型结果，再用 Jina Reader 读取评论区代表性评论）

【平台 4】微信公众号（Exa search）
- mcporter call 'exa.web_search_exa(query: "<品牌> <车型名> 发布会 评测 site:mp.weixin.qq.com", numResults: 5)'

请汇总提取：

## 高频好评主题
（每项需 ≥3 条帖子/评论提及，附代表性原文引用 + 链接 + 来源平台）
- 主题 1: <内容>
  引用: "<原文摘录>" [来源](<URL>)（平台：<小红书/汽车之家/懂车帝/B站/微信>）
- ...

## 高频差评主题
（每项需 ≥3 条帖子/评论提及，附代表性原文引用 + 链接 + 来源平台）
- 主题 1: <内容>
  引用: "<原文摘录>" [来源](<URL>)（平台：<小红书/汽车之家/懂车帝/B站/微信>）
- ...

## 整体情绪倾向
<正面 / 中性 / 负面>，理由一句话

## 数据说明
搜索平台: 小红书 / 汽车之家 / 懂车帝 / B站 / 微信公众号
执行日期: <today's date>
覆盖帖子量: <大约条数>
如果某平台无相关内容，注明"无相关内容"而非跳过。
```

---

## Block 4: Sales Analysis Prompt（销量趋势分析）

**Tool: `obsidian`（读取 `汽车/销量Wiki/`）**

Use after the event timeline is finalized. Goal: compare brand total and model-specific monthly sales in the 6-month window before and after each key launch event.

```
目标品牌: <品牌名>
关键发布事件:
  - E001: <车型名>，发布日期 <YYYY-MM-DD>
  - E002: <车型名>，发布日期 <YYYY-MM-DD>
  （列出所有深读事件）

步骤：

1. 读取销量数据
   obsidian search query="<品牌名> 销量" path="汽车/销量Wiki"
   对每个命中路径执行 obsidian read，收集月度销量数据。
   目标数据范围：各事件日期前后各 6 个月。

2. 对每个关键事件输出以下结构：

### <车型名>（<发布日期>）

**品牌月度总销量**

| 月份 | 销量（辆） | 环比 |
|------|-----------|------|
| <发布前6月> | ... | ... |
| ...（共13行，前6 + 发布月 + 后6）|

**车型月度销量**

| 月份 | 销量（辆） | 环比 |
|------|-----------|------|
| <同上> | ... | ... |

**趋势判断**
- 品牌总量: ↑ / ↓ / 持平（发布后3个月均值 vs 发布前3个月均值）
- 车型销量: ↑ / ↓ / 持平（同上）
- 关键拐点: <如有，描述具体月份与幅度>

3. 如果某月数据缺失，标注"数据缺失"，不要估算。
4. 如果某车型在 Wiki 中无记录，标注"Wiki 无记录"。
```

---

## Block 5: Synthesis Prompt（战略综合）

Use after completing deep reads, social listening, and sales analysis for all key events. Goal: produce the strategic analysis report draft.

```
以下是 <品牌名> 从 <开始日期> 至 <结束日期> 的发布事件深读结果、用户声音分析摘要和销量趋势分析摘要：

<粘贴所有完成深读的事件字段提取结果>

请根据以上证据生成战略演进分析报告，结构如下：

## 一、品牌阶段划分
按战略转折点将时间线分成 2-4 个阶段，每个阶段给出：阶段名称、时间范围、标志性事件、核心特征。

## 二、产品线演进脉络
描述车型序列如何扩张、收缩或重组。区分主动战略选择与市场压力下的被动调整。

## 三、三电与智驾能力提升轨迹
分两个子节：
- 三电轨迹：电池容量/续航/充电速率的趋势线，是否有代际跃升？
- 智驾轨迹：功能级别和硬件平台的演进，OTA 节奏与竞品对比。

## 四、改款换代规律
改款周期（月数）、改款幅度（外观/配置/三电/智驾各自的变化程度）、换代方向。

## 五、人群策略变更
目标用户如何随时间漂移？从哪些信号可以看出（价格带、配色、场景描述、代言人）？

## 六、企业战略洞察
品牌战略的关键转折点及背后逻辑。从高管表态、发布会规格、品牌 slogan 变化等企业层面信号提炼。

## 七、策略建议
每条建议格式：
【暴露点: <gap>
 影响范围: <products/segments>
 建议动作: <concrete action>
 紧迫度: 高/中/低】

建议数量：3-5 条，按紧迫度降序排列。每条必须引用至少一个具体事件作为证据。

注意：
- 有证据的结论才写，无证据的字段标"待确认"
- 不做跨品牌竞品对比（除非用户在本次会话中提供了竞品数据）
```

---

## Block 6: Write-Back Prompt（写入 Markdown 目录）

Writes plain markdown to `汽车/发布会研究/<品牌>/`. Use after user confirms the strategic analysis draft. Wiki build follows in Block 7.

```
请按以下顺序将内容写入 Obsidian：

步骤 A：写方法笔记（已在 Step 2 完成，如需更新则覆盖）
路径: 汽车/发布会研究/<品牌名>/00-分析方法与口径.md
命令: obsidian create path="汽车/发布会研究/<品牌名>/00-分析方法与口径.md" content="<内容>" overwrite

步骤 B：写时间线（无需确认，直接写入）
路径: 汽车/发布会研究/<品牌名>/01-发布会时间线.md
命令: obsidian create path="汽车/发布会研究/<品牌名>/01-发布会时间线.md" content="<内容>" overwrite

步骤 C：写用户声音分析（无需确认，直接写入）
路径: 汽车/发布会研究/<品牌名>/03-用户声音分析.md
命令: obsidian create path="汽车/发布会研究/<品牌名>/03-用户声音分析.md" content="<内容>" overwrite

步骤 D：写销量趋势分析（无需确认，直接写入）
路径: 汽车/发布会研究/<品牌名>/04-销量趋势分析.md
命令: obsidian create path="汽车/发布会研究/<品牌名>/04-销量趋势分析.md" content="<内容>" overwrite

步骤 E：在用户确认战略分析草稿后，写入战略报告
路径: 汽车/发布会研究/<品牌名>/02-战略演进分析.md
命令: obsidian create path="汽车/发布会研究/<品牌名>/02-战略演进分析.md" content="<内容>" overwrite

每步写入后，执行一次读取验证：
obsidian read path="汽车/发布会研究/<品牌名>/<文件名>.md"

确认写入内容与预期一致后继续下一步。
如果写入失败，报告错误原因，不要静默跳过。
```

---

## Block 7: Wiki Build Prompt（构建 Wiki 目录）

**Tool: `obsidian`** — writes to `汽车/发布会Wiki/<品牌>/`

Use immediately after Block 6 completes. Input: the 5 markdown files already in memory (or re-read from `汽车/发布会研究/<品牌>/`). No user confirmation required.

```
以下是已写入 Markdown 目录的 5 个文件内容。
请依次构建 Wiki 版本并写入 汽车/发布会Wiki/<品牌名>/。

Wiki 构建规则（对每个文件执行）：

1. 在文件顶部插入 YAML frontmatter：
   ---
   brand: <品牌名>
   date_range_start: <YYYY-MM-DD>
   date_range_end: <YYYY-MM-DD>
   generated: <今日日期>
   type: <见下表>
   ---

   type 对应关系：
   00-分析方法与口径 → methodology
   01-发布会时间线   → launch-timeline
   02-战略演进分析   → strategy-analysis
   03-用户声音分析   → user-voice
   04-销量趋势分析   → sales-analysis

2. 将车型名转换为 wikilink：
   <车型名> → [[汽车/品牌库/<品牌名>/<车型名>|<车型名>]]
   （仅替换事件条目和分析段落中的车型名，不替换 URL 中的内容）

3. 将 04-销量趋势分析 中的月份数据行添加 wikilink：
   <YYYY-MM> → [[汽车/销量Wiki/<品牌名>/<YYYY-MM>|<YYYY-MM>]]

4. 在 02-战略演进分析 的引言段落末尾追加交叉引用：
   > 时间线参考：[[汽车/发布会Wiki/<品牌名>/01-发布会时间线|发布会时间线]]
   > 销量数据：[[汽车/发布会Wiki/<品牌名>/04-销量趋势分析|销量趋势分析]]

5. 不替换外部 URL（http://、https:// 开头的链接保持原样）。
6. 悬空 wikilink 是允许的（品牌库或销量Wiki中对应笔记不存在时，Obsidian 会显示红色，属预期行为）。

写入顺序与命令：

步骤 W-A：
obsidian create path="汽车/发布会Wiki/<品牌名>/00-分析方法与口径.md" content="<wiki版内容>" overwrite
obsidian read path="汽车/发布会Wiki/<品牌名>/00-分析方法与口径.md"

步骤 W-B：
obsidian create path="汽车/发布会Wiki/<品牌名>/01-发布会时间线.md" content="<wiki版内容>" overwrite
obsidian read path="汽车/发布会Wiki/<品牌名>/01-发布会时间线.md"

步骤 W-C：
obsidian create path="汽车/发布会Wiki/<品牌名>/03-用户声音分析.md" content="<wiki版内容>" overwrite
obsidian read path="汽车/发布会Wiki/<品牌名>/03-用户声音分析.md"

步骤 W-D：
obsidian create path="汽车/发布会Wiki/<品牌名>/04-销量趋势分析.md" content="<wiki版内容>" overwrite
obsidian read path="汽车/发布会Wiki/<品牌名>/04-销量趋势分析.md"

步骤 W-E：
obsidian create path="汽车/发布会Wiki/<品牌名>/02-战略演进分析.md" content="<wiki版内容>" overwrite
obsidian read path="汽车/发布会Wiki/<品牌名>/02-战略演进分析.md"

验证：确认每个 wiki 文件顶部有 YAML frontmatter，正文中车型名已转换为 [[wikilink]] 格式。
如写入失败，报告错误原因，不要静默跳过。
```
