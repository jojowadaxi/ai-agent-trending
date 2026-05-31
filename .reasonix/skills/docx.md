---
name: docx
description: 创建、读取、编辑 Word 文档 (.docx)。触发：提到 Word/docx/报告/备忘录/信函/模板，需要格式化排版、目录、页眉页脚、批注、修订等。
runAs: subagent
---

# Word 文档处理

读取完整参考手册前，先了解核心流程。

## 快速参考

| 任务 | 方法 |
|------|------|
| 读取内容 | `pandoc document.docx -o output.md` |
| 创建新文档 | 用 `docx` npm 包 (JS) |
| 编辑已有文档 | 解包 → 编辑 XML → 重新打包 |

详细操作手册：`read_file(".reasonix/skills/anthropic/docx/SKILL.md")` 获取完整指令，包括：
- docx-js 创建文档的完整 API（表格、图片、页眉页脚、目录、列表、超链接等）
- XML 编辑参考（修订标记、批注、图片嵌入、schema 合规）
- 脚本位置：`.reasonix/skills/anthropic/docx/scripts/`

## 编辑已有文档三步法

1. **解包**: `python .reasonix/skills/anthropic/docx/scripts/office/unpack.py input.docx unpacked/`
2. **编辑 XML**: 修改 `unpacked/word/document.xml`
3. **打包**: `python .reasonix/skills/anthropic/docx/scripts/office/pack.py unpacked/ output.docx --original input.docx`

## 依赖

- pandoc, docx (`npm install -g docx`), LibreOffice
