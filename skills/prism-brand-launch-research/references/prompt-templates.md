# Prompt Templates

Four prompt blocks for `prism-brand-launch-research`. Execute in order. Substitute variables in `<角括号>` before use.

---

## Block 1: Discovery Prompt（事件发现）

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

Use for each event in the inventory that meets Round 2 criteria (see `search-strategy.md`). Goal: extract all 7 analysis fields from the source article.

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

## Block 3: Synthesis Prompt（战略综合）

Use after completing deep reads for all key events. Goal: produce the strategic analysis report draft.

```
以下是 <品牌名> 从 <开始日期> 至 <结束日期> 的发布事件深读结果：

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

## Block 4: Write-Back Prompt（写入 Obsidian）

Use after user confirms the strategic analysis draft. Provides the exact obsidian-cli command patterns.

```
请按以下顺序将内容写入 Obsidian：

步骤 A：写方法笔记（已在 Step 2 完成，如需更新则覆盖）
路径: 汽车/发布会研究/<品牌名>/00-分析方法与口径.md
命令: obsidian write "汽车/发布会研究/<品牌名>/00-分析方法与口径.md" --content "<内容>"

步骤 B：写时间线（无需确认，直接写入）
路径: 汽车/发布会研究/<品牌名>/01-发布会时间线.md
命令: obsidian write "汽车/发布会研究/<品牌名>/01-发布会时间线.md" --content "<内容>"

步骤 C：在用户确认战略分析草稿后，写入战略报告
路径: 汽车/发布会研究/<品牌名>/02-战略演进分析.md
命令: obsidian write "汽车/发布会研究/<品牌名>/02-战略演进分析.md" --content "<内容>"

每步写入后，执行一次读取验证：
obsidian read "汽车/发布会研究/<品牌名>/<文件名>.md"

确认写入内容与预期一致后继续下一步。
如果写入失败，报告错误原因，不要静默跳过。
```
