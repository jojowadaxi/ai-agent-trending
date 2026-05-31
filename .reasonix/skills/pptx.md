---
name: pptx
description: 创建/编辑 PowerPoint 演示文稿 (.pptx)。触发：提到 slides/deck/演示/PPT/幻灯片/演讲，无论读取还是创建。
runAs: subagent
---

# PowerPoint 处理

读取完整手册：`read_file(".reasonix/skills/anthropic/pptx/SKILL.md")`

## 快速参考

| 任务 | 方法 |
|------|------|
| 读取内容 | `python -m markitdown presentation.pptx` |
| 从模板编辑 | 读 `editing.md` |
| 从零创建 | 读 `pptxgenjs.md` |

## 编辑流程

1. 缩略图预览: `python .reasonix/skills/anthropic/pptx/scripts/thumbnail.py file.pptx`
2. 解包: `python .reasonix/skills/anthropic/pptx/scripts/office/unpack.py file.pptx unpacked/`
3. 修改 XML → 清理 → 打包

## 从零创建

使用 `pptxgenjs` (npm)，详见 `read_file(".reasonix/skills/anthropic/pptx/pptxgenjs.md")`

## 设计要点

- 选一个粗体配色方案，不要默认蓝色
- 每页必须有视觉元素（图/图标/图表），不能纯文字
- 标题 36-44pt，正文 14-16pt
- 多样化布局，不要每页相同

## QA

```bash
python -m markitdown output.pptx  # 内容检查
python .reasonix/skills/anthropic/pptx/scripts/office/soffice.py --headless --convert-to pdf output.pptx
pdftoppm -jpeg -r 150 output.pdf slide  # 视觉检查
```
