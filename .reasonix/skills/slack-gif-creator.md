---
name: slack-gif-creator
description: 创建 Slack 优化的动画 GIF（emoji/消息用）。触发：Slack GIF/做动图/动画表情。
runAs: subagent
---

# Slack GIF 制作器

完整手册：`read_file(".reasonix/skills/anthropic/slack-gif-creator/SKILL.md")`

## Slack 规范

- Emoji GIF: 128x128
- 消息 GIF: 480x480
- FPS: 10-30
- 颜色: 48-128

## 核心工作流

```python
from core.gif_builder import GIFBuilder
from PIL import Image, ImageDraw

builder = GIFBuilder(width=128, height=128, fps=10)
for i in range(12):
    frame = Image.new('RGB', (128, 128), bg_color)
    draw = ImageDraw.Draw(frame)
    # 用 PIL 绘制动画帧
    builder.add_frame(frame)
builder.save('output.gif', num_colors=48, optimize_for_emoji=True)
```

## 动画概念

震动、脉冲/心跳、弹跳、旋转、淡入淡出、滑动、缩放、粒子爆发

## 依赖

`pip install pillow imageio numpy`
脚本在 `.reasonix/skills/anthropic/slack-gif-creator/core/`
