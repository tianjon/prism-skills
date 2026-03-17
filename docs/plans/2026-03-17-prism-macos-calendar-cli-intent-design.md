# prism-macos-calendar-cli Intent Layer Design

## Goal

为 `prism-macos-calendar-cli` 增加一层“意图归一化器”，把用户的模糊日历请求先收敛成高确定性的结构化参数，再调用现有 `./scripts/cal` 执行。

## Background

当前 skill 的执行层已经具备稳定的确定型能力：

- `list/search/create/update/delete`
- `--range` 快捷时间窗口
- dry-run 优先、`--apply` 显式写入
- 歧义时返回结构化错误而不是猜测

缺口在于，`SKILL.md` 目前更像“参数收集说明”，缺少一套可重复执行的“模糊输入 -> 确定参数”流程。结果是 agent 可以快速执行确定命令，但对“把那个会往后挪一点”“下周找个时间安排评审”这类输入仍然缺少统一归一化逻辑。

## Architecture

采用两层结构：

1. `./scripts/cal`
   继续保持“确定执行层”定位，只接受明确参数并直接操作 Calendar.app。

2. `./scripts/cal-intent`
   新增“意图归一化层”，负责把模糊输入解析成结构化计划，再决定下一步是：
   - 直接生成确定命令
   - 先执行 `list/search` 缩小候选
   - 返回歧义并停止

`SKILL.md` 同步定义对话层工作流：先归一化、再 dry-run、最后 `--apply`。

## Normalization Model

归一化器对每次输入收集以下槽位：

- `intent`: `list | search | create | update | delete`
- `calendar_hint`
- `time_hint`
- `event_hint`
- `write_intent`

归一化结果输出统一结构：

```json
{
  "status": "resolved|needs_search|ambiguous",
  "intent": "update",
  "confidence": "high|medium|low",
  "reason": "缺少唯一 id，先搜索收敛候选",
  "next_command": "./scripts/cal events search --query 评审 --range next7 --format json",
  "resolved_args": {
    "calendar": "工作",
    "id": "",
    "uid": "",
    "query": "评审",
    "title": "",
    "start": "",
    "end": ""
  }
}
```

## Parsing Rules

### Intent Rules

- `查看/列出/看看/有哪些` -> `events list`
- `搜索/查找/找` -> `events search`
- `创建/安排/添加/新建` -> `events create`
- `修改/推迟/提前/改到/往后挪` -> `events update`
- `删除/取消` -> `events delete`

### Time Rules

- 能映射到现有快捷范围时，优先生成 `--range`
- 能确定到具体时刻时，生成 ISO `--start/--end`
- 仅能确定到宽时间窗时，不直接写入，只用于 `search/list`
- 类似“下午”“晚上”“往后一点”这类表达，默认不直接推断为最终写入时间

### Event Resolution Rules

目标优先级：

1. `id`
2. `uid`
3. 唯一搜索结果
4. 标题候选

对“那个会”“上次那个评审”这类指代，先转成 `events search`，不直接生成写入命令。

### Calendar Rules

- 显式给出日历名时，优先按名称匹配
- “默认日历”映射到 `PRISM_CALENDAR_DEFAULT`
- 如果匹配到多个同名日历，返回 `ambiguous_calendar`

## Execution Policy

### `resolved`

参数完整、日历唯一、目标唯一：

- 读操作直接生成 `./scripts/cal ...`
- 写操作先生成 dry-run 命令
- 除非显式确认，否则不自动追加 `--apply`

### `needs_search`

信息不足以直接写，但可以先缩小范围：

- 生成下一条 `events list/search`
- 如果搜索结果唯一，再生成后续 dry-run
- 如果搜索结果为空或多个，停止并返回候选/缺口

### `ambiguous`

仍存在关键歧义时停止：

- 多个日历候选
- 多个事件候选
- 时间不够确定，无法安全写入

## Safety Rules

- 所有写操作默认 dry-run
- `update/delete` 未收敛到唯一目标时不执行
- 模糊时间不自动填成最终写入参数
- 通过搜索收敛出的写操作，仍需先展示 dry-run

## Example Flows

### Example 1

输入：`明天看看会议`

输出：

- `status=resolved`
- `intent=search`
- `next_command=./scripts/cal events search --query 会议 --range tomorrow --format json`

### Example 2

输入：`明天下午两点在工作日历创建评审会`

输出：

- `status=resolved`
- `intent=create`
- 生成 dry-run：
  `./scripts/cal events create --calendar 工作 --title 评审会 --start ... --end ... --format json`

### Example 3

输入：`把那个评审往后挪一点`

输出：

- `status=needs_search`
- 先生成：
  `./scripts/cal events search --query 评审 --range next7 --format json`

### Example 4

输入：`删除下周预算会`

输出：

- `status=needs_search`
- 先搜索，再依据唯一结果生成 delete dry-run

## Files

- Modify: `skills/prism-macos-calendar-cli/SKILL.md`
- Modify: `skills/prism-macos-calendar-cli/README.md`
- Add: `skills/prism-macos-calendar-cli/scripts/cal-intent`
- Add: `skills/prism-macos-calendar-cli/tests/test_cal_intent.py`

## Testing Strategy

至少覆盖以下场景：

- 自然语言时间映射到 `--range`
- 自然语言创建请求映射到 create dry-run
- 模糊更新请求退化为 search
- 删除请求必须先收敛到唯一目标
- 同名日历返回歧义
- 默认日历提示仅影响允许的入口

## Non-Goals

- 不做通用 NLP 系统
- 不在 AppleScript 中实现自然语言理解
- 不自动执行未经确认的写操作

