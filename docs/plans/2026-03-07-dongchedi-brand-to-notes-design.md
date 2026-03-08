# 懂车帝品牌抓取到笔记系统重构设计蓝图

## 目标

将当前 `dongchedi-scraper` 从一组松散脚本，重构为一条**可追溯、可验证、可恢复、可发布**的数据流水线：

- 用户只输入**品牌名**，例如“比亚迪”
- 系统自动发现该品牌在售车系
- 自动抓取每个车系下所有在售配置及参数
- 自动将结果写入笔记系统（默认 Obsidian）
- 每一步都保留**证据链**与**运行元数据**，确保“真的抓到了什么”可被证明

---

## 一、问题定义

当前 skill 可以“跑通流程”，但系统性缺陷明显：

1. **状态不可信**：`tmp/*.json` 只是文件，不代表来自本次成功抓取
2. **证据缺失**：结果文件与页面快照、抓取时间、解析版本之间没有稳定绑定
3. **脚本耦合严重**：采集、分析、发布混在一条脚本链上
4. **失败语义模糊**：空结果、验证码、页面结构变化、局部失败没有被建模
5. **参数解析脆弱**：`params.py` 目前主要依赖文本启发式，不是结构化优先策略
6. **可维护性差**：每个脚本都在重复路径解析、错误处理、文件读写和浏览器控制模式

结论：当前系统是“原型脚本集”，还不是“可长期运行的采集产品”。

---

## 二、用户视角的最终能力

### 用户输入
- 品牌名，例如：`比亚迪`

### 系统输出
- 品牌总览笔记
- 每个车系的索引笔记
- 每个配置的参数笔记
- 一份本次抓取运行摘要
- 可选：抓取失败/异常笔记

### 成功标准
- 给定品牌名后，系统在单次运行内完成从“品牌搜索”到“笔记落地”的闭环
- 每份结果都能追溯到本次抓取的 URL、时间、页面快照、解析版本
- 若中途失败，可判断失败位置并支持从上一步恢复，而不是整条链路重跑

---

## 三、方案选型

### 方案 A：保留脚本链，仅补日志与元数据

**做法**
- 继续保留 `search.py / configs.py / params.py / store.py`
- 只是在每一步输出更多 `metadata.json`

**优点**
- 改动最小
- 短期见效快

**缺点**
- 架构问题不解决
- 状态模型依然混乱
- 后续维护成本持续上升

**适用性**
- 只适合临时止血，不适合作为目标形态

### 方案 B：重构为“阶段化流水线 + 显式运行状态”

**做法**
- 保留脚本入口，但底层重构为统一的运行模型
- 引入 `run_id`、阶段快照、解析适配器、发布层
- 所有中间产物都绑定一次抓取运行

**优点**
- 不推翻现有 skill 入口
- 兼顾落地速度和架构清晰度
- 最适合当前仓库演进

**缺点**
- 需要一轮中等规模重构
- 要补测试和产物 schema

**适用性**
- 推荐方案

### 方案 C：重做为单一 CLI/服务化应用

**做法**
- 完全放弃现有多脚本结构
- 新做 `app/`、`pipeline/`、`storage/`、`publish/`
- 统一成一个命令或服务

**优点**
- 架构最整洁
- 长远扩展性最好

**缺点**
- 重写成本高
- 当前 skill 资产复用率低
- 容易超出需求

**适用性**
- 只有在后续要支持多站点、多输出目标时才值得做

### 推荐

采用 **方案 B：阶段化流水线 + 显式运行状态**。

原因：
- 它保留当前仓库与 skill 的使用方式
- 它能解决你指出的“并没有真的抓下来数据”的结构性问题
- 它不会为了架构纯洁性而过度重写

---

## 四、目标架构

### 4.1 分层架构

将系统拆成五层：

1. **入口层（Entry）**
   - 负责接收品牌名参数、选择模式、触发流水线
   - 只做命令编排，不做解析逻辑

2. **采集层（Capture）**
   - 负责访问懂车帝页面
   - 保存页面 HTML 快照、URL、标题、抓取时间、浏览器会话信息
   - 产物是“页面快照”，不是业务结果

3. **解析层（Extract）**
   - 从页面快照中提取结构化数据
   - 以页面适配器为核心，例如：
     - `SearchPageAdapter`
     - `SeriesPageAdapter`
     - `ParamsPageAdapter`

4. **领域层（Domain/Pipeline）**
   - 负责从品牌到车系、从车系到配置、从配置到参数的业务流程
   - 负责数据聚合、去重、恢复、重试和运行状态推进

5. **发布层（Publish）**
   - 负责把最终数据写入笔记系统
   - 不参与抓取和解析

### 4.2 目录建议

建议将 `skills/dongchedi-scraper/` 重构为：

```text
skills/dongchedi-scraper/
  SKILL.md
  lib/
    adapters/
      search_page.py
      series_page.py
      params_page.py
    capture/
      browser_session.py
      snapshots.py
    domain/
      models.py
      run_state.py
      pipeline.py
    publish/
      obsidian_writer.py
      note_renderers.py
    storage/
      artifacts.py
      manifests.py
    utils/
      paths.py
      errors.py
  scripts/
    run_brand_pipeline.py
    inspect_run.py
    retry_failed_step.py
  tests/
    ...
  tmp/
    runs/
      <run_id>/
        manifest.json
        steps/
        snapshots/
        outputs/
```

---

## 五、核心设计理念

### 5.1 “结果不是事实，观测才是事实”

系统中的一等公民应当是：
- 页面快照
- 抓取时间
- URL
- 解析器版本
- 本次运行 ID

而不是某个脱离上下文的 `search-results.json`。

### 5.2 每一步都必须是“可证明”的

任何结构化结果都必须带来源：
- 来自哪个页面
- 来自哪次运行
- 由哪个解析器版本生成

### 5.3 空结果必须有语义

空结果不应统一解释为“没搜到”，而要区分：
- 搜索确实为空
- 验证码阻断
- 页面结构变更
- 解析规则失效
- 抓取未完成

### 5.4 发布与抓取分离

Obsidian 只是输出目标，不是采集流程的一部分。
抓取成功和发布成功必须是两件独立可判断的事。

---

## 六、运行模型

### 6.1 Run 概念

引入 `ScrapeRun`：

```json
{
  "run_id": "20260307-byd-001",
  "input": {"brand": "比亚迪"},
  "status": "running",
  "started_at": "2026-03-07T10:00:00+08:00",
  "current_step": "extract_series_configs",
  "steps": [...],
  "stats": {...}
}
```

### 6.2 Step 概念

每一步都有自己的状态：
- `pending`
- `running`
- `succeeded`
- `failed`
- `partial`
- `skipped`

### 6.3 Snapshot 概念

每次页面访问都生成快照对象：

```json
{
  "snapshot_id": "search-byd-001",
  "run_id": "20260307-byd-001",
  "step": "search_brand",
  "url": "https://www.dongchedi.com/search?...",
  "title": "懂车帝 - 说真的还得懂车帝",
  "fetched_at": "2026-03-07T10:00:12+08:00",
  "html_path": "tmp/runs/.../snapshots/search-byd-001.html",
  "html_length": 726508,
  "page_type": "search"
}
```

### 6.4 Output Artifact 概念

每一步的结果不是裸 JSON，而是 Artifact：

```json
{
  "artifact_type": "brand_series_list",
  "run_id": "20260307-byd-001",
  "source_snapshot_ids": ["search-byd-001"],
  "parser_version": "search_page:v2",
  "record_count": 48,
  "data": [...]
}
```

---

## 七、品牌名到笔记的标准流水线

### Step 1：品牌搜索
- 输入：品牌名
- 行为：打开搜索页，搜索品牌
- 保存：HTML 快照、metadata、search artifact
- 输出：品牌候选车系列表

### Step 2：目标车系筛选
- 默认保留“在售车系”
- 过滤停售、概念车、无在售配置车系
- 输出：标准化 `BrandSeriesList`

### Step 3：抓取车系页
- 对每个车系访问 `series_url(series_id)`
- 保存车系页快照
- 解析在售配置、车系属性、价格区间、能源类型
- 输出：`SeriesConfigsArtifact`

### Step 4：抓取参数页
- 对每个配置访问参数页
- 优先提取结构化源
- 失败时才退回 DOM 结构提取，最后才退回文本启发式
- 输出：`ConfigParamsArtifact`

### Step 5：汇总品牌数据集
- 聚合品牌、车系、配置、参数
- 去重、校验、补全元数据
- 输出：`BrandDatasetArtifact`

### Step 6：渲染笔记
- 生成：
  - 品牌总览笔记
  - 车系索引笔记
  - 配置参数笔记
  - 本次抓取摘要笔记
- 输出：渲染后的 Markdown / Obsidian 页面内容

### Step 7：发布到笔记系统
- 调用 `obsidian` 相关接口写入笔记
- 记录发布成功/失败状态
- 输出：发布报告

---

## 八、参数抓取的重构原则

这是本项目最关键的一段。

### 当前问题
- 当前 `params.py` 主要依赖 HTML 转文本，再猜分类和键值对
- 这会丢掉结构边界，解析质量不稳定

### 新原则
参数抓取按以下优先级进行：

1. **SSR / 内嵌 JSON**
2. **前端初始化 State**
3. **XHR/API 响应数据**
4. **DOM 结构提取**
5. **纯文本启发式解析（最后兜底）**

### 为什么这样做
- 越靠前，信息损失越少
- 越靠后，越容易受展示层变更影响

### 设计要求
对每个配置参数结果记录：
- `source_kind`: `ssr | state | xhr | dom | text`
- `confidence`: `high | medium | low`
- `parser_version`
- `raw_snapshot_id`

这样笔记层也能标明“这份参数可信度如何”。

---

## 九、笔记系统输出设计

默认输出到 Obsidian，目录建议如下：

```text
汽车/
  品牌库/
    比亚迪/
      比亚迪-总览.md
      车系/
        秦L DM.md
        海鸥.md
      配置/
        秦L DM/
          2025款 DM-i 120KM领先型.md
          ...
      抓取记录/
        2026-03-07-抓取摘要.md
        2026-03-07-异常报告.md
```

### 品牌总览笔记
内容包括：
- 品牌名
- 本次抓取时间
- 车系总数
- 配置总数
- 参数抓取成功率
- 车系列表索引
- 异常摘要

### 车系笔记
内容包括：
- 车系基础信息
- 在售配置列表
- 每个配置笔记链接
- 数据来源和抓取时间

### 配置参数笔记
内容包括：
- 配置名称、价格、年度、车系、品牌
- 参数分组表
- 参数抓取来源等级
- 本次抓取时间
- 原始页面链接

### 抓取摘要笔记
内容包括：
- `run_id`
- 输入品牌名
- 各阶段耗时
- 成功/失败统计
- 页面阻断或结构变更记录

---

## 十、错误模型

定义统一错误类型：

- `CaptchaBlockedError`
- `PageShapeChangedError`
- `NoResultsFoundError`
- `SnapshotMissingError`
- `ArtifactSchemaError`
- `PartialExtractionError`
- `PublishFailedError`

### 原则
- 错误必须带上下文：`run_id / step / url / series_id / car_id`
- 错误必须可归因到某个阶段
- 错误必须决定：是否可重试、是否可继续下游

---

## 十一、测试策略

### 单元测试
- 解析器级测试
- 模型验证测试
- Artifact schema 测试
- 笔记渲染测试

### 夹具测试
- 保存真实搜索页、车系页、参数页 HTML 作为 fixtures
- 验证页面结构变化时，测试能第一时间失败

### 集成测试
- 从 `BrandPipeline` 输入品牌名开始
- 使用本地 fixtures 跑完整链路
- 验证最终输出的笔记和运行摘要

### 冒烟测试
- 用真实浏览器跑一个小品牌/一个车系
- 确认真实环境仍可抓取

---

## 十二、迁移策略

### 阶段 1：先建运行模型，不改用户入口
- 保留现有 `scripts/*.py`
- 在底层补 `run_id`、snapshot、artifact、manifest
- 优先修复“结果不可证伪”的问题

### 阶段 2：重构参数抓取
- 把 `params.py` 拆为 capture + adapter + extractor
- 引入结构化优先策略

### 阶段 3：重构发布层
- 将 Obsidian 输出逻辑独立成 writer
- 让发布层只消费 `BrandDatasetArtifact`

### 阶段 4：收口为单入口
- 新增统一入口：`scripts/run_brand_pipeline.py`
- 用户只需输入品牌名

---

## 十三、MVP 范围

本次重构蓝图建议的 MVP 只做：

1. 输入品牌名
2. 自动发现品牌在售车系
3. 自动抓取在售配置
4. 自动抓取配置参数
5. 自动输出到 Obsidian
6. 每一步保存快照与元数据
7. 失败可定位到具体阶段

**明确不做**：
- 竞品 A/B/C 智能分析
- 多站点支持
- Web UI
- 云端任务调度
- 增量同步优化

---

## 十四、蓝图结论

这次重构不是“把几个脚本改干净”，而是把 skill 从“脚本集合”升级为“有观测链、状态模型、发布契约的数据流水线”。

其核心转变是：
- 从“有没有 JSON 文件”
- 转为“能否证明这批数据来自本次有效抓取”

对你的目标“输入品牌名，在笔记中输出抓取的参数配置信息”来说，这套蓝图已经把：
- 输入
- 采集
- 解析
- 聚合
- 发布
- 可追溯性

全部收敛到一条可执行的架构路径上。
