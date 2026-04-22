# Obsidian 调用范式

这份文档规定 `prism-guwen-tutor` 如何通过 `obsidian-cli` 技能（命令入口 `obsidian`）读写 vault。

## 前置检查

运行时先按顺序确认：

1. `obsidian --help` 能正常返回 → 说明 CLI 可用。
2. `obsidian vault` 能返回当前 vault 根路径 → 说明 Obsidian 正在运行且 vault 已打开。
3. 环境变量 `GUWEN_TUTOR_VAULT_ROOT` 如有设置，检查其与 `obsidian vault` 查询结果是否一致；不一致时提醒用户但以环境变量为准。
4. `GUWEN_TUTOR_BASE_PATH` 默认 `教育/教材/语文/古文诗词/`，如果在当前 vault 下不存在，停下来询问用户正确的基准路径。

若任一步失败，停止执行并告知用户。

## 路径表示规则

- 所有 `obsidian` 子命令接收的路径都是**相对 vault 根的相对路径**。
- 文件系统操作（`cp` / `ls`）使用**绝对路径**，组合规则：`"$GUWEN_TUTOR_VAULT_ROOT/<相对路径>"`。
- 中文路径在 shell 里统一用双引号包住。
- 文件名里的 `-详解.md` 后缀是**硬约定**，不要写成 `_详解.md` 或其他变体。

## 读原文

```bash
obsidian read path="教育/教材/语文/古文诗词/古诗/必修上/07-登高.md"
```

返回的内容同时包含 frontmatter 和正文。从 frontmatter 提取：

- `标题`（字符串，可空）
- `作者`（字符串，可空）
- `朝代`（字符串，可空）
- `年级`（字符串，对应 7/8/9 年级上下 / 必修 X / 选择性必修 X 等）
- `类型`（`古诗 / 词 / 文言文`，可空）

任一字段缺失时从正文 H1 标题或文件名回填。

## 搜索候选

### 按作者搜索

```bash
obsidian search query="作者: 杜甫" path="教育/教材/语文/古文诗词/"
```

或搜整个 vault 的 frontmatter：

```bash
obsidian search query="作者: 杜甫" scope=frontmatter
```

（具体支持的 flag 以 `obsidian search --help` 为准；若不支持 `scope=frontmatter`，退回到 `query="作者: 杜甫"` 再在结果里过滤 frontmatter 命中。）

### 按作品名搜索

```bash
obsidian search query="标题: 春望" path="教育/教材/语文/古文诗词/"
```

命中 0 时退回到文件名模糊搜：

```bash
obsidian ls path="教育/教材/语文/古文诗词/" | grep -i "春望"
```

（实际用 Grep 工具执行 `obsidian ls` 的输出；不要拼 shell。）

### 目录递归

```bash
obsidian ls path="教育/教材/语文/古文诗词/古诗/必修上/" recursive=true
```

或直接在文件系统里 `ls "$GUWEN_TUTOR_VAULT_ROOT/教育/教材/语文/古文诗词/古诗/必修上/"`。过滤规则：

- 保留 `.md` 结尾
- 排除 `-详解.md` 结尾
- 排除 `.` 开头的隐藏文件

## 写详解

### 新建（默认）

```bash
obsidian create path="<原目录>/<原 stem>-详解.md" content="<完整 Markdown>" silent
```

- `content` 是完整的详解 Markdown，包含 frontmatter。
- `silent` 表示不在 Obsidian 界面弹出新标签。

### 覆盖（`--force`）

```bash
obsidian create path="<原目录>/<原 stem>-详解.md" content="<完整 Markdown>" overwrite silent
```

### 大文件后备方案

当 `content` 过大（经验值 > 800 行）导致 `obsidian create` 失败：

1. 先把内容写到 `tmp/<stem>-详解.md`。
2. 用文件系统 `cp` 放到 vault 对应目录：
   ```bash
   cp "<skill 目录>/tmp/<stem>-详解.md" "$GUWEN_TUTOR_VAULT_ROOT/<原目录>/<原 stem>-详解.md"
   ```
3. 写完通知 Obsidian 刷新（通常 Obsidian 会自动检测，但若出现"未同步"告警可让用户手动点一下）。

## 和 `obsidian-markdown` 的协作

写回 vault 前必须通过 `obsidian-markdown` 校准排版：

- callout 类型标准化（`[!example]` 原文、`[!info]` 作者此刻、`[!tip]` 手法、`[!quote]` 普遍经验、`[!question]` 钩子和延伸）
- `==高亮==` 语法
- wikilink 短名化（`[[07-登高]]` 而不是 `[[教育/教材/语文/古文诗词/古诗/必修上/07-登高]]`）
- inline code 和 tag 格式

调用方式参考 `obsidian-markdown` 技能自身的说明；通常是把 Markdown 传入，拿回校准后的版本再走 `obsidian create`。

## 常见故障

| 症状 | 原因 | 处理 |
|---|---|---|
| `obsidian read` 返回空 | 文件路径拼错 / 大小写不匹配 | 先 `obsidian ls` 列父目录确认 |
| `obsidian create` 失败但无明显错误 | content 过大 | 走大文件后备方案 |
| `obsidian search` 搜不到 | vault 索引未建完 / query 语法错误 | 等索引完成或改为文件系统 `ls + grep` |
| 写入后 Obsidian 未显示新文件 | 视图未刷新 | 让用户切到别的文件再切回来，或按 F5 |
| 中文路径 `cp` 报错 | shell 未识别 UTF-8 | 确保 `LANG` 设为 `zh_CN.UTF-8` 或 `en_US.UTF-8` |

## 禁止事项

- **禁止**直接修改原文件。
- **禁止**跨 skill 调用 `baoyu-*` 或其他写外部系统的 skill（本 skill 只产出 Markdown）。
- **禁止**在 vault 外部创建 mirror / backup——所有产物只进 vault 的指定兄弟位置。
- **禁止**用 `obsidian append` 追加到原文件；原文件保持只读。
