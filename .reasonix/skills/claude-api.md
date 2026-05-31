---
name: claude-api
description: 构建/调试/优化 Claude API / Anthropic SDK 应用。触发：import anthropic/@anthropic-ai/sdk/Claude API。
runAs: subagent
---

# Claude API 开发

完整手册：`read_file(".reasonix/skills/anthropic/claude-api/SKILL.md")`

## 默认设置

- 模型：`claude-opus-4-8`
- 思考模式：`thinking: {type: "adaptive"}` 
- 流式：长输入/输出/高 max_tokens 时使用

## 语言检测

检查项目文件自动选择语言：
- `*.py` → Python (`anthropic` SDK)
- `*.ts/*.js` → TypeScript (`@anthropic-ai/sdk`)
- `*.go` → Go | `*.java` → Java | `*.rb` → Ruby | `*.cs` → C# | `*.php` → PHP
- 无 SDK → cURL/HTTP

参考代码在：`.reasonix/skills/anthropic/claude-api/{python,typescript,go,java,ruby,csharp,php,curl}/`

## API 层级

- 单次调用：分类/摘要/提取/问答
- 工作流：多步骤 + 工具调用
- Managed Agents：服务端托管的有状态 agent

## Prompt Caching

前缀匹配，稳定内容在前，最多 4 个断点。
