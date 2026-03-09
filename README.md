# prism-skills

一个面向本地 AI Coding Agent 的技能仓库，当前主要沉淀 `dongchedi-scraper` 等可复用 skill，供 `Codex`、`Claude Code`、`OpenCode` 等支持 `SKILL.md`/agent 约定的工具使用。

> [!IMPORTANT]
> 本项目仅限个人学习、研究、评估与非商业实验使用，不得用于任何商业目的。

## 用途限制

- 允许：个人学习、技术研究、功能评估、私有非商业实验。
- 禁止：商业销售、付费服务、咨询交付、企业内部生产使用、SaaS 托管、闭源再分发、任何直接或间接商业化行为。
- 如需商业授权，必须先取得作者的书面许可。

更完整的许可条款见根目录 `LICENSE`。

## 项目定位

本仓库是 **source-available（源码可见）研究仓库**，不是 OSI 定义下的开源项目。

当前重点 skill：

- `skills/dongchedi-scraper/`
  - 按品牌抓取懂车帝车型与配置数据
  - 提取结构化参数
  - 通过 `Obsidian-cli` 发布标准化笔记

## 仓库结构

```text
.
├── AGENTS.md
├── LICENSE
├── README.md
├── docs/
│   └── plans/
├── scripts/
│   └── new-skill.sh
└── skills/
    ├── README.md
    ├── _template/
    └── dongchedi-scraper/
```

## 设计原则

- 每个 skill 独立放在 `skills/<skill-name>/`
- 可复用逻辑放在 skill 自己的 `lib/`
- 可执行入口放在 skill 自己的 `scripts/`
- 临时产物放在 skill 自己的 `tmp/`
- `SKILL.md` 是每个 skill 的运行入口与事实来源

## 快速开始

```bash
cd skills/dongchedi-scraper
python3 scripts/run_brand_pipeline.py --brand BMW
```

运行时优先复用已经具备依赖的全局 Python；若依赖不满足，再回退到本地 `uv` 管理环境。更完整的分发与环境说明见 `skills/dongchedi-scraper/DISTRIBUTION.md`。

## 安装到 Codex

### 1. 安装 Codex CLI

官方安装方式：

```bash
npm install -g @openai/codex
```

如果你使用 Homebrew，也可以安装对应发行版本。

### 2. 克隆本仓库

```bash
git clone git@github.com:tianjon/prism-skills.git ~/src/prism-skills
```

### 3. 将本仓库的 skills 链接到 Codex skills 目录

```bash
mkdir -p ~/.codex/skills

for d in ~/src/prism-skills/skills/*; do
  [ -f "$d/SKILL.md" ] || continue
  [ "$(basename "$d")" = "_template" ] && continue
  ln -sfn "$d" ~/.codex/skills/$(basename "$d")
done
```

### 4. 验证

- 重启 `codex` 会话。
- 确认工具能发现 `dongchedi-scraper` 之类的 skill。
- 如果你维护的是本仓库开发副本，推荐保留软链接方式，便于后续更新自动生效。

## 安装到 Claude Code

### 1. 安装 Claude Code

官方安装方式：

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

兼容安装方式：

```bash
npm install -g @anthropic-ai/claude-code
```

### 2. 克隆本仓库

```bash
git clone git@github.com:tianjon/prism-skills.git ~/src/prism-skills
```

### 3. 安装 skills（兼容 skill 工作流）

```bash
mkdir -p ~/.claude/skills

for d in ~/src/prism-skills/skills/*; do
  [ -f "$d/SKILL.md" ] || continue
  [ "$(basename "$d")" = "_template" ] && continue
  ln -sfn "$d" ~/.claude/skills/$(basename "$d")
done
```

### 4. 官方 subagent 模式说明

Anthropic 官方文档当前主推的是 `subagents`，目录通常为 `~/.claude/agents/` 或项目内 `.claude/agents/`。本仓库采用的是 `SKILL.md` 结构；如果你的 Claude Code 环境只启用了官方 subagent 机制，请按需把单个 skill 转写为 Claude subagent Markdown 文件后再放入对应 `agents/` 目录。

### 5. 验证

- 运行 `claude` 并进入项目。
- 确认会话可以识别或调用你安装的 skill。
- 如果未识别，优先检查 `SKILL.md` 是否存在、软链接是否生效，以及当前环境是否使用 skills 兼容层还是官方 subagent 模式。

## 安装到 OpenCode

### 1. 安装 OpenCode

官方安装方式：

```bash
curl -fsSL https://opencode.ai/install | bash
```

### 2. 克隆本仓库

```bash
git clone git@github.com:tianjon/prism-skills.git ~/src/prism-skills
```

### 3. 将本仓库的 skills 链接到 OpenCode 目录

```bash
mkdir -p ~/.config/opencode/skills

for d in ~/src/prism-skills/skills/*; do
  [ -f "$d/SKILL.md" ] || continue
  [ "$(basename "$d")" = "_template" ] && continue
  ln -sfn "$d" ~/.config/opencode/skills/$(basename "$d")
done
```

### 4. 验证

- 重启 `opencode` 会话。
- 确认其可以发现 `~/.config/opencode/skills/` 下的技能目录。
- OpenCode 官方文档同时说明，它也能兼容读取若干其他技能目录约定；但对本仓库，优先推荐使用其原生目录 `~/.config/opencode/skills/`。

## 维护者发布前检查

如果代码需要发布到 GitHub，提交身份应使用：

```bash
git config --global user.name "tianjon"
git config --global user.email "fengyadong@gmail.com"
```

提交前可执行：

```bash
git config --global --get user.name
git config --global --get user.email
```

## License

本仓库采用自定义的 **Personal Research Non-Commercial License 1.0**。

- 允许个人研究与非商业实验
- 明确禁止商业使用
- 衍生作品仍不得脱离上述限制
- 按“现状”提供，不附带任何担保

详见 `LICENSE`。
