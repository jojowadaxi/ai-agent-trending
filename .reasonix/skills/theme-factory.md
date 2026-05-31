---
name: theme-factory
description: 为文档/幻灯片/网页应用配色主题。10 个预设 + 可自定义。触发：主题/配色/美化/换风格。
runAs: subagent
---

# 主题工厂

完整手册：`read_file(".reasonix/skills/anthropic/theme-factory/SKILL.md")`

## 使用流程

1. 展示 `theme-showcase.pdf` 给用户看所有主题
2. 让用户选择主题
3. 从 `themes/` 目录读取对应主题文件
4. 应用到文档/幻灯片/网页

## 10 个预设主题

Ocean Depths, Sunset Boulevard, Forest Canopy, Modern Minimalist, Golden Hour, Arctic Frost, Desert Rose, Tech Innovation, Botanical Garden, Midnight Galaxy

## 自定义主题

如果没有合适的，根据用户描述创建新主题，定义配色+字体组合。
