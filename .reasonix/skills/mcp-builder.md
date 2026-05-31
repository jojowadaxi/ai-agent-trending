---
name: mcp-builder
description: 构建高质量的 MCP (Model Context Protocol) Server。触发：MCP server/工具集成/API 封装。
runAs: subagent
---

# MCP Server 构建器

完整手册：`read_file(".reasonix/skills/anthropic/mcp-builder/SKILL.md")`

## 四阶段流程

1. **深度调研**：理解 MCP 协议 + API 文档
2. **实现**：TypeScript (推荐) 或 Python
3. **审查测试**：代码质量 + MCP Inspector
4. **创建评估**：10 道复杂问答测试

## 推荐技术栈

- TypeScript + Streamable HTTP（远程）或 stdio（本地）
- Zod 定义工具 schema
- 参考：`.reasonix/skills/anthropic/mcp-builder/reference/`

## 工具设计原则

- 描述清晰，命名一致（前缀模式如 `github_create_issue`）
- 返回聚焦数据，支持分页
- 错误消息具有可操作性
