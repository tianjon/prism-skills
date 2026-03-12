# Prompt Templates

Reuse these bilingual prompts during execution instead of rewriting them from scratch.

执行时优先复用这些中英双语提示词，不要从零重写。

## Environment Check / 环境检查

ZH:
先检查本机的 Python 和 Obsidian CLI 是否满足最低要求。Python 必须处于 MinerU 支持的版本范围内。Obsidian 必须支持命令行模式，且当前处于运行状态，`obsidian help` 必须成功。若 Python 或 Obsidian 不满足要求，立即停止并明确说明原因。若缺少 MinerU，则自动安装并触发模型下载。若缺少 `obsidian-markdown`、`obsidian-bases`、`obsidian-cli`，则只安装缺失项。

EN:
First verify that local Python and the Obsidian CLI satisfy the minimum requirements. Python must be within the version range supported by MinerU. Obsidian must support command-line mode, be currently running, and `obsidian help` must succeed. If Python or Obsidian does not meet the requirement, stop immediately and explain the exact reason. If MinerU is missing, install it automatically and trigger model download. If `obsidian-markdown`, `obsidian-bases`, or `obsidian-cli` is missing, install only the missing skills.

## MinerU Conversion For One File / 单文件转换

ZH:
将这个单文件输入按 MinerU 官方支持方式转换为 Markdown 和相关资源。不要立即写入 Obsidian。先整理出文档标题、主题、建议保存路径、标签、索引页归属、相关文档链接，以及图片/附件保留方案，再等待用户确认。

EN:
Convert this single input file into Markdown and related assets using the officially supported MinerU workflow. Do not write to Obsidian yet. First determine the document title, topic, proposed destination path, tags, index placement, related-note links, and the image or attachment preservation plan, then wait for user confirmation.

## MinerU Conversion For A Directory / 目录批量转换

ZH:
将这个目录中的文档逐个用 MinerU 转换为 Markdown，并保留原目录结构中的有效语义。目录输入必须递归发现受支持文件，不要假设转换器会自动递归。不要机械镜像目录，也不要立即写入 Obsidian。先基于文档内容和目录层级生成建议的 Obsidian 目录树、文件清单、分类索引、标签、引用关系，以及图片/附件保留与落位方案，然后等待用户确认。

EN:
Convert each document in this directory into Markdown with MinerU and preserve the meaningful parts of the source directory structure. For directory input, discover supported files recursively instead of assuming the converter will recurse automatically. Do not mirror the tree mechanically and do not write to Obsidian yet. First propose the Obsidian folder tree, file list, category indexes, tags, cross-note links, and the image or attachment preservation plan based on both content and source hierarchy, then wait for user confirmation.

## Write Confirmation / 写入确认

ZH:
不要立即写入 Obsidian。先展示建议的目录树、将创建或更新的文件、索引页、标签、引用关系，以及图片/附件的落位与引用改写策略。允许用户通过对话修改目录名称、文件名称、分类结构、标签和附件策略。只有在用户明确确认后，才执行写入。

EN:
Do not write to Obsidian immediately. First show the proposed folder tree, the files to create or update, the index pages, the tags, the cross-note links, and the image or attachment placement plus reference rewrite strategy. Allow the user to revise folder names, file names, category structure, tags, and attachment policy through the conversation. Only write after the user gives explicit confirmation.

## Index Maintenance / 索引维护

ZH:
写入完成后，维护长期分类索引，而不是只维护一次性导入记录。将每篇笔记连接到其分类索引，并在分类索引中回链到这些文档。若保留了图片/附件，必须校验笔记中的引用在 Obsidian 中可解析。必要时使用 `.base` 提供长期浏览视图。

EN:
After writing, maintain long-lived category indexes instead of a one-off import record. Connect each note to its category index, and link back from the category index to the note set. If images or attachments were preserved, verify their references still resolve in Obsidian after writing. Use a `.base` file only when it improves durable browsing for the category.
