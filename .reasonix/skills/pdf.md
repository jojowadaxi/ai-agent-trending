---
name: pdf
description: PDF 处理：读取/提取文本表格、合并、拆分、旋转、水印、创建、填写表单、加密/解密、OCR 扫描件。提到 .pdf 文件时触发。
runAs: subagent
---

# PDF 处理

读取完整手册：`read_file(".reasonix/skills/anthropic/pdf/SKILL.md")`

## Python 库

- **pypdf** — 基础操作（合并、拆分、旋转、元数据、加密）
- **pdfplumber** — 文本/表格提取（比 pypdf 更准）
- **reportlab** — 创建 PDF
- **pdf2image + pytesseract** — OCR 扫描件

## 常用命令

- 合并: `qpdf --empty --pages file1.pdf file2.pdf -- merged.pdf`
- 提取文本: `pdftotext -layout input.pdf output.txt`
- 提取图片: `pdfimages -j input.pdf prefix`

## 表单填写

详细步骤见 `read_file(".reasonix/skills/anthropic/pdf/forms.md")`
