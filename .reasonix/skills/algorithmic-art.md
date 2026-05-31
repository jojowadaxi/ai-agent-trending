---
name: algorithmic-art
description: 用 p5.js 创建算法生成艺术（流场、粒子系统、噪声场）。触发：生成艺术/算法艺术/创意编程/p5.js。
runAs: subagent
---

# 算法生成艺术

完整手册：`read_file(".reasonix/skills/anthropic/algorithmic-art/SKILL.md")`

两阶段流程：
1. **算法哲学创作** (.md) — 4-6 段的生成艺术宣言
2. **p5.js 实现** (.html) — 自包含的交互式生成艺术

## 技术要点

- 种子随机数：`randomSeed(seed)` + `noiseSeed(seed)` 确保可复现
- 从模板开始：`read_file(".reasonix/skills/anthropic/algorithmic-art/templates/viewer.html")`
- 参数化设计：让用户可调参
- 工艺至上：算法需精心调校，非随机噪声

## 输出

单个 HTML artifact，内嵌 p5.js CDN，包含种子导航、参数滑块、操作按钮。
