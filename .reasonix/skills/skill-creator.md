---
name: skill-creator
description: 创建、改进和评估 Skill。触发：写 skill/创建 skill/优化 skill/测试 skill。
runAs: subagent
---

# Skill 创建器

完整手册：`read_file(".reasonix/skills/anthropic/skill-creator/SKILL.md")`

## 核心循环

1. **理清意图**：skill 做什么？何时触发？输出格式？
2. **撰写草稿**：SKILL.md（name + description + 指令）
3. **写测试用例**：2-3 个真实用户 prompt
4. **运行评估**：有 skill vs 无 skill 对比
5. **定性 + 定量评审**
6. **改进 → 重复**

## Skill 结构

```
skill-name/
├── SKILL.md (必须)
│   ├── YAML frontmatter (name, description)
│   └── Markdown 指令
└── 可选资源
    ├── scripts/     - 可执行脚本
    ├── references/  - 参考文档
    └── assets/      - 模板/字体/图标
```

## 渐进加载

1. 元数据（name + description）— 始终在上下文中
2. SKILL.md 正文 — skill 触发时加载（< 500 行）
3. 打包资源 — 按需加载

## 描述优化

写完 skill 后，运行 `scripts/run_loop` 自动优化触发描述。
