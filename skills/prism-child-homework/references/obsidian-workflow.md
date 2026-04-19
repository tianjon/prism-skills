# Obsidian Workflow

本文件定义 `prism-child-homework` 在 Obsidian 中的**档案结构、文件命名、字段 schema 与 `obsidian-cli` 的实用调用范式**。所有路径相对于 `档案根目录`——由环境变量 `$CHILD_HOMEWORK_ARCHIVE_ROOT` 或档案 frontmatter 里的 `档案根目录` 字段决定，用户首次建档时指定；文档里不写死任何具体路径。环境变量约定见 `SKILL.md` 的 **Runtime Policy · 环境变量** 段。

## 档案目录结构

```
<档案根目录>/
├── 孩子档案.md                                       # 覆盖式 · 单文件
├── _索引.md                                          # 覆盖式 · 仪表盘
├── _回访队列.md                                      # 覆盖式 · 学习队列（活跃错题到期表）
│
├── 批改记录/
│   └── YYYY-MM/
│       └── YYYY-MM-DD/
│           ├── 简洁模式/
│           │   └── {UNIT_TOPIC}_{INDEX}.md          # 每次批改必产
│           ├── 完整模式/
│           │   └── {UNIT_TOPIC}_{INDEX}.md          # 每次批改必产
│           └── 数学建模/
│               └── {UNIT_TOPIC}_{INDEX}.md          # 每次批改必产（建模三步法 + 奥赛题）
│
├── 错题本/
│   └── {TOPIC}.md                                    # 按课标知识点命名；追加累积
│
├── 练习题/
│   └── {UNIT_TOPIC}/
│       └── {知识点}.md                                # 每个细分知识点一份；追加累积
│
├── 总结/
│   ├── 周报/YYYY-Www.md                              # 覆盖式
│   ├── 月报/YYYY-MM.md                               # 覆盖式
│   ├── 年报/YYYY.md                                   # 覆盖式
│   ├── 专题/{知识点}-掌握-YYYY-MM-DD.md               # 新建 · 某概念掌握时
│   └── 里程碑/反思-YYYY-MM-DD.md                      # 新建 · 反思能力跃迁时
│
└── 图片/
    ├── 原始图片/{UNIT_TOPIC}_{INDEX}_{SUBINDEX}.png   # 家长上传的作业照片原件
    ├── 错题/{UNIT_TOPIC}_{知识点}.png                 # 错题对比示意图（Gemini 生成）
    └── 核心知识点图解/{UNIT_TOPIC}_{知识点}.png       # 核心概念图（跨批次可共享）
```

## 命名约定

### 占位符

| 占位符 | 含义 | 示例 |
|---|---|---|
| `UNIT_TOPIC` | 课本单元主题（一个单元一批作业共用） | `长方体和正方体`、`分数运算` |
| `INDEX` | 当日该单元第 N 次批改 | `1`、`2` |
| `SUBINDEX` | 单次批改里的第 N 张照片 | `1`、`2`、… |
| `TOPIC` | 错题本的课标知识点名 | `体积与表面积` |
| `知识点` | 练习题 / 图片按细分知识点命名 | `体积单位`、`面积进率`、`排水法公式` |

### 关键命名原则

- **批改记录按日分子目录**：`批改记录/2026-04/2026-04-18/`；单日多批用 INDEX 区分
- **错题本按知识点一份文件**：`错题本/体积与表面积.md`——不再有"数学/"子目录层
- **练习题按知识点一份文件**：`练习题/长方体和正方体/体积单位.md`——累积所有历史中触发此知识点的练习题
- **图片按知识点 / 批次 命名**：不再用日期时间戳；跨批次可共享（同一核心概念的图解复用）
- **原始作业照片要归档**：首次进入 vault 时立即复制到 `图片/原始图片/` 目录，以防 image cache 清理

## 文件粒度与归档策略

**一次性**（每次批改产生一份新文件）：
- 批改记录：`批改记录/YYYY-MM/YYYY-MM-DD/{UNIT_TOPIC}_{INDEX}_{模式}.md`
- 原始图片：`图片/原始图片/{UNIT_TOPIC}_{INDEX}_{SUBINDEX}.png`

**累积归档**（多次批改追加到同一文件）：
- 错题本：`错题本/{TOPIC}.md`
- 练习题：`练习题/{UNIT_TOPIC}/{知识点}.md`
- 错题图：同一知识点反复触发时复用同一文件名（可能覆盖旧图）
- 核心知识点图解：跨批次共享；只在首次触发时生成，之后都引用

**覆盖式**（每次生成都覆盖）：
- 孩子档案、索引、回访队列、周/月/年报

**触发式**（满足条件时追加）：
- 专题总结（概念整体掌握时）
- 里程碑（反思能力跃迁时）

## Obsidian CLI 实用指令

### 可用命令

| 指令 | 用途 |
|---|---|
| `obsidian vault` | 查看当前 vault 名、路径、大小 |
| `obsidian help [<command>]` | 查看命令语义 |
| `obsidian read path="<相对路径>"` | 读取文件 |
| `obsidian create path="<路径>" content="..." [overwrite] [silent]` | 新建或覆盖写入（文本） |
| `obsidian search query="<kw>" [limit=N]` | 全库搜索关键字 |

### 已知不存在的指令

- **`obsidian ls` 不存在**。列目录用下列替代。

### 列目录的替代方案

```bash
# 方法 1（推荐）：搜 frontmatter 类型 tag
obsidian search query="类型: 批改记录" limit=50

# 方法 2：直接搜 vault 文件系统
#   $CHILD_HOMEWORK_VAULT_ROOT   = vault 绝对路径（未设置时由 `obsidian vault` 解析）
#   $CHILD_HOMEWORK_ARCHIVE_ROOT = 档案根目录（相对 vault 的子路径）
ls "$CHILD_HOMEWORK_VAULT_ROOT/$CHILD_HOMEWORK_ARCHIVE_ROOT/批改记录/2026-04/2026-04-18/"

# 方法 3：按 tag 搜
obsidian search query="tag:#批改/{{昵称}}" limit=50
```

### 二进制写入（图片）

obsidian-cli 不支持直接写二进制。流程：

```bash
# 1. Gemini 生成到 skill tmp/
npx bun "$BAOYU_GEMINI_CLI" --image /tmp/xxx.png ...

# 2. cp 到 vault 对应目录（绕过 obsidian-cli 是必要例外）
cp /tmp/xxx.png "$CHILD_HOMEWORK_VAULT_ROOT/$CHILD_HOMEWORK_ARCHIVE_ROOT/图片/错题/长方体和正方体_体积单位.png"
```

Markdown 文件**必须经 obsidian-cli**，图片是**必要例外**。

### 创建 vs 覆盖 vs 追加

统一用 `obsidian create path="..." content="..." [overwrite] silent`：
- **新建文件**：不加 `overwrite`
- **覆盖文件**：加 `overwrite`
- **追加文件**：`obsidian read` 读 → 内存拼接 → `obsidian create ... overwrite` 覆盖写回

## frontmatter Schema

### 通用字段

```yaml
技能: prism-child-homework
类型: 档案 | 索引 | 回访队列 | 批改记录 | 错题条目 | 练习题 | 周报 | 月报 | 年报 | 专题总结 | 里程碑
生成时间: YYYY-MM-DDTHH:MM:SS+08:00
tags:
  - 孩子作业/数学
  - <分类>/<昵称>
```

### `孩子档案.md`

```yaml
昵称: <string>
出生年月: YYYY-MM-DD            # 首选——技能每次批改自动算 年龄
年龄: <integer>                 # 由出生年月派生
当前年级: <string, 可选>
认知阶段: A | B | C | D | E     # 由年龄派生；技能每次重算覆盖
输出模式: 简洁 | 完整            # 决定批改记录形式；首次建档问
档案根目录: <string>
上次批改时间: <ISO8601>
累计批改次数: <integer>
近30天正确率: <0.00~1.00>
当前薄弱点:
  - <知识点>
根因图谱:
  <节点名>: <命中次数>
已掌握知识点:
  - <知识点>
反思成长:
  近30天平均等级: L0~L5
  近30天提问次数: <integer>
  最近一次升级: YYYY-MM-DD | 尚无
建模思维图谱:                  # 数学建模课沿五维素养追踪
  近30天:
    M1: <integer>              # 抽象
    M2: <integer>              # 推理
    M3: <integer>              # 想象
    M4: <integer>              # 归纳
    M5: <integer>              # 迁移
  累计:
    M1: <integer>
    M2: <integer>
    M3: <integer>
    M4: <integer>
    M5: <integer>
  薄弱维度:
    - <M1~M5 中低于阈值的维度>
  均衡度: 五维均衡 | 偏科:<MX>
  最近建模课: <相对路径>
回访队列指针: <相对路径>
aliases:
  - <昵称>数学档案
```

### `批改记录/…/{UNIT_TOPIC}_{INDEX}_{模式}.md`

```yaml
孩子昵称: <string>
年龄: <快照，不回填>
年级: <快照>
认知阶段: <快照>
模式: 简洁 | 完整
单元: <UNIT_TOPIC>
批次: <INDEX>
题目总数: <integer>
正确题数 / 部分正确题数 / 错误题数 / 回访题数 / 回访通过: <N/M>
本次正确率: <0.00~1.00>
主要薄弱点: <string>
根因图谱命中:
  <节点>: <N>
tags:
  - 批改/<昵称>
  - 单元/<UNIT_TOPIC>
  - 根因/<节点>
  - 层级/L<N>
关联错题本:
  - "[[<TOPIC>]]"
关联练习题目录: "[[练习题/<UNIT_TOPIC>]]"
```

### `错题本/<TOPIC>.md`

```yaml
知识点: <TOPIC>
tags:
  - 错题/<昵称>
  - 知识点/<TOPIC>
  - 根因/<节点>
```

### `练习题/<UNIT_TOPIC>/<知识点>.md`

```yaml
知识点: <string>
单元: <UNIT_TOPIC>
tags:
  - 练习/<昵称>
  - 知识点/<知识点>
  - 单元/<UNIT_TOPIC>
```

### `总结/…`

**周 / 月 / 年报**：

```yaml
覆盖范围: YYYY-Www | YYYY-MM | YYYY
起止日期: YYYY-MM-DD ~ YYYY-MM-DD
批改次数: <integer>
题目总数: <integer>
正确率: <0.00~1.00>
难度判定: 偏简单 | 刚合适 | 偏难
回顾平均等级: L0~L5
回访通过率: <0.00~1.00>
tags:
  - 周报/<昵称> | 月报/<昵称> | 年报/<昵称>
```

## 幂等性约定

| 类型 | 写入方式 |
|---|---|
| 档案 / 索引 / 回访队列 / 周月年报 | 覆盖式 |
| 批改记录 / 专题总结 / 里程碑 | 新建（时间戳天然不冲突） |
| 错题本 / 练习题 / 错题图 | 追加累积（读-拼接-覆盖） |
| 核心知识点图解 | 首次生成，之后跨批次复用 |

**特殊规则**：
- 档案正文 `<!-- 家长备注开始 -->` / `<!-- 家长备注结束 -->` 之间原样保留
- 历史批改记录的 `年龄 / 年级 / 认知阶段` 是当时快照，不因孩子年龄变化而回改
- 同一知识点反复掌握 / 失守时，专题文件用新日期后缀另写一份

## 典型执行顺序（Workflow 落地）

```
Step 1 载入：
  obsidian read path="孩子档案.md"
  → 解析出生年月 → 算年龄 → 派生认知阶段 → 查 pedagogy-by-stage.md
  → 读 输出模式（决定 Step 6 用简洁还是完整模板）

  obsidian read path="_回访队列.md"
  → 筛选到期条目

  obsidian search query="类型: 批改记录" limit=20
  → 按时间倒序取最近 5-10 份

  obsidian search query="类型: 错题条目" limit=20
  → 读所有活跃错题本 frontmatter

Step 2 解析照片（同时把原始照片 cp 到 图片/原始图片/）

Step 3-5 业务逻辑

Step 5.5 配图（Gemini Web → cp 到 图片/错题/、图片/核心知识点图解/）

Step 6 写回（三份批改文件必须同时产出）：
  create 批改记录/YYYY-MM/YYYY-MM-DD/简洁模式/{UNIT_TOPIC}_{INDEX}.md
  create 批改记录/YYYY-MM/YYYY-MM-DD/完整模式/{UNIT_TOPIC}_{INDEX}.md
  create 批改记录/YYYY-MM/YYYY-MM-DD/数学建模/{UNIT_TOPIC}_{INDEX}.md  ← 新增
  create 错题本/{TOPIC}.md（读-拼-写）
  create 练习题/{UNIT_TOPIC}/{知识点}.md（读-拼-写，按触发的知识点）
  create 孩子档案.md（覆盖；保留家长备注）
  create _索引.md（覆盖）
  create _回访队列.md（覆盖）
  条件性：create 总结/专题/… 或 总结/里程碑/…

Step 7 周月年总结（跨周期时）
```

## Markdown 里的图片嵌入

所有图片用 Obsidian 短名 wikilink：

```markdown
![[长方体和正方体_维度感知.png|600]]
![[长方体和正方体_体积单位.png|500]]
![[长方体和正方体_2_1.png|500]]
```

短名能解析是因为图片文件名全局唯一（UNIT_TOPIC + 知识点 / INDEX）。

**配图生成失败时**：对应位置用占位 callout，不留 broken link：

```markdown
> [!note] 本题配图生成失败
> 配图流水线这次没跑通，不影响讲解。家长可以手动再触发重生成。
```

## 写回前校验

每次 Step 6 写回前，技能内部校验：
- frontmatter 字段完整
- 正文不包含 `language-conversion.md` 的禁用词
- wikilink 目标能解析
- `![[*.png]]` 的图片文件实际存在于 vault（否则用失败占位）
- 历史批改记录的 `年龄` 快照不被覆盖

## 失败处理

- `obsidian-cli` 不可用或 Obsidian 未启动 → 停止告知
- 档案根目录不存在 → 首次运行化；非首次停下排查
- 图片 cp 失败 → 批改正文仍写，图片嵌入位置用失败占位
- `search` 返回超时或空 → 回退到文件系统 ls（vault 路径已知时）
