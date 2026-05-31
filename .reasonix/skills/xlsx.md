---
name: xlsx
description: Excel/电子表格处理 (.xlsx/.csv/.tsv)：创建、读取、编辑、公式、格式化、图表、数据清洗。提到 Excel/表格时触发。
runAs: subagent
---

# Excel 处理

读取完整手册：`read_file(".reasonix/skills/anthropic/xlsx/SKILL.md")`

## 核心原则

**用公式，不要硬编码计算结果！**
- ✅ `sheet['B10'] = '=SUM(B2:B9)'`
- ❌ `sheet['B10'] = 5000`

## 库选择

- **pandas** — 数据分析、批量操作
- **openpyxl** — 公式、格式、Excel 特性

## 公式重算（必须！）

```bash
python .reasonix/skills/anthropic/xlsx/scripts/recalc.py output.xlsx
```

## 财务模型规范

- 蓝色字体 (0,0,255): 硬编码输入
- 黑色字体: 公式
- 绿色字体: 跨工作表引用
- 红色字体: 外部链接
- 黄色背景: 关键假设
- 零值显示为 "-"

## 格式

- 货币: `$#,##0`，表头标注单位
- 百分比: `0.0%`
- 负数: 用括号 (123)
- 年份: 文本格式
