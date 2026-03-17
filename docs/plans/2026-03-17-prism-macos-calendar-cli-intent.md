# prism-macos-calendar-cli Intent Layer Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 为 `prism-macos-calendar-cli` 增加一层“模糊输入 -> 确定参数”的意图归一化入口，并把对话约束同步写入 skill 文档。

**Architecture:** 保持 `scripts/cal` 作为确定执行层，新增 `scripts/cal-intent` 作为前置归一化层。该入口只负责解析意图、归一化参数、生成 `resolved / needs_search / ambiguous` 三类计划，不直接绕过 `scripts/cal` 的 dry-run 与显式写入约束。

**Tech Stack:** POSIX shell / bash、现有 `scripts/cal`、unittest、SKILL/README 文档

---

### Task 1: Add Failing Tests For Intent Classification

**Files:**
- Create: `skills/prism-macos-calendar-cli/tests/test_cal_intent.py`
- Test: `skills/prism-macos-calendar-cli/tests/test_cal_intent.py`

**Step 1: Write the failing test**

覆盖最小场景：

- `明天看看会议` -> `resolved + search + --range tomorrow`
- `明天下午两点在工作日历创建评审会` -> `resolved + create + dry-run`
- `把那个评审往后挪一点` -> `needs_search`
- `删除下周预算会` -> `needs_search`

**Step 2: Run test to verify it fails**

Run:

```bash
python3 -m unittest discover -s skills/prism-macos-calendar-cli/tests -p 'test_cal_intent.py'
```

Expected: FAIL because `scripts/cal-intent` does not exist yet.

**Step 3: Write minimal implementation**

创建最小 `scripts/cal-intent`，先支持：

- 输入读取
- 规则匹配
- JSON 计划输出

**Step 4: Run test to verify it passes**

Run:

```bash
python3 -m unittest discover -s skills/prism-macos-calendar-cli/tests -p 'test_cal_intent.py'
```

Expected: PASS

### Task 2: Add Calendar And Safety Resolution Rules

**Files:**
- Modify: `skills/prism-macos-calendar-cli/scripts/cal-intent`
- Modify: `skills/prism-macos-calendar-cli/tests/test_cal_intent.py`

**Step 1: Write the failing test**

补充测试：

- `默认日历` -> 归一化成默认日历提示或 `PRISM_CALENDAR_DEFAULT`
- 同名/无法唯一确定日历 -> `ambiguous`
- 写操作默认输出 dry-run，不输出 `--apply`

**Step 2: Run test to verify it fails**

Run:

```bash
python3 -m unittest discover -s skills/prism-macos-calendar-cli/tests -p 'test_cal_intent.py'
```

Expected: FAIL on new cases.

**Step 3: Write minimal implementation**

在 `scripts/cal-intent` 增加：

- 日历槽位解析
- 歧义状态输出
- 安全策略：写操作默认 dry-run

**Step 4: Run test to verify it passes**

Run the same command and confirm PASS.

### Task 3: Add Search-First Update/Delete Flow

**Files:**
- Modify: `skills/prism-macos-calendar-cli/scripts/cal-intent`
- Modify: `skills/prism-macos-calendar-cli/tests/test_cal_intent.py`

**Step 1: Write the failing test**

新增测试：

- update/delete 在缺 `id/uid` 时，输出 `needs_search`
- 唯一候选时生成下一步 dry-run 命令模板

**Step 2: Run test to verify it fails**

Run:

```bash
python3 -m unittest discover -s skills/prism-macos-calendar-cli/tests -p 'test_cal_intent.py'
```

Expected: FAIL on selector flow.

**Step 3: Write minimal implementation**

加入规则：

- `update/delete` 未收敛到唯一 selector 时不生成可写命令
- 统一输出下一步 `events search` 命令

**Step 4: Run test to verify it passes**

Run the same command and confirm PASS.

### Task 4: Document Agent Workflow

**Files:**
- Modify: `skills/prism-macos-calendar-cli/SKILL.md`
- Modify: `skills/prism-macos-calendar-cli/README.md`

**Step 1: Write the failing test**

这里用文档校验替代代码测试，新增检查点：

- `SKILL.md` 明确“先用 `cal-intent` 归一化，再调用 `cal`”
- `README.md` 有最小示例

**Step 2: Run check to verify current docs are missing it**

Run:

```bash
rg -n "cal-intent|resolved|needs_search|ambiguous" skills/prism-macos-calendar-cli/SKILL.md skills/prism-macos-calendar-cli/README.md
```

Expected: no or incomplete matches.

**Step 3: Write minimal implementation**

补文档：

- 工作流
- 安全规则
- 示例

**Step 4: Run check to verify it passes**

Run the same `rg` command and confirm expected terms exist.

### Task 5: Final Verification

**Files:**
- Verify: `skills/prism-macos-calendar-cli/scripts/cal-intent`
- Verify: `skills/prism-macos-calendar-cli/tests/test_cal_intent.py`
- Verify: `skills/prism-macos-calendar-cli/SKILL.md`
- Verify: `skills/prism-macos-calendar-cli/README.md`

**Step 1: Run targeted tests**

```bash
python3 -m unittest discover -s skills/prism-macos-calendar-cli/tests -p 'test_*.py'
```

Expected: all calendar CLI and intent tests pass.

**Step 2: Run shell validation**

```bash
bash -n skills/prism-macos-calendar-cli/scripts/cal
bash -n skills/prism-macos-calendar-cli/scripts/cal-intent
```

Expected: both succeed with exit code 0.

**Step 3: Run diff hygiene**

```bash
git diff --check
```

Expected: no whitespace or merge-marker issues.

**Step 4: Commit**

Only if the user explicitly asks for a commit.
