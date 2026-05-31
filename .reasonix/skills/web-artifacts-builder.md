---
name: web-artifacts-builder
description: 用 React+Tailwind+shadcn/ui 构建复杂前端 artifact。触发：复杂 Web 组件/React 应用/shadcn。
runAs: subagent
---

# Web Artifacts 构建器

完整手册：`read_file(".reasonix/skills/anthropic/web-artifacts-builder/SKILL.md")`

## 技术栈

React 18 + TypeScript + Vite + Tailwind CSS + shadcn/ui

## 流程

1. 初始化: `bash .reasonix/skills/anthropic/web-artifacts-builder/scripts/init-artifact.sh <project-name>`
2. 开发: 编辑生成的代码
3. 打包: `bash .reasonix/skills/anthropic/web-artifacts-builder/scripts/bundle-artifact.sh`
4. 输出: `bundle.html` 自包含文件

## 注意事项

- 避免 AI slop 美学（居中布局、紫色渐变、统一圆角、Inter 字体）
- 适用于需要状态管理、路由或 shadcn/ui 组件的复杂 artifact
- 简单的单文件 HTML 不需要此 skill
