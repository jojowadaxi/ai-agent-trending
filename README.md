# 🤖 Weekly AI Agent Trending

每周一早上 9:00 (北京时间) 自动抓取 GitHub 上与 AI Agent 相关的热门项目，以 Issue 形式推送到本仓库。

## 工作原理

```
每周一 9:00 CST → GitHub Actions 触发 → Python 脚本跑 → 搜 GitHub API → 创建 Issue
```

脚本会搜索：
- **AI Agent topic** — `ai-agent`、`agentic-ai`、`ai-agents`
- **Agent 框架** — 名称/描述含 "agent framework" 且近期活跃
- **Agent 工具 & MCP** — "agent memory"、"agent tool"、"mcp server"
- **本周新项目** — 7 天内新建的含 "agent" 的仓库

## 部署步骤

1. **Fork 或新建一个 GitHub 仓库**

2. **把这两个文件放进仓库：**
   ```
   your-repo/
   ├── .github/workflows/ai-agent-trending.yml
   └── scripts/ai_agent_trending.py
   ```

3. **Push 到 GitHub**

4. **启用 Actions：**
   - 进入仓库 → Settings → Actions → General
   - 确保 "Allow all actions" 已开启

5. **开启 Issues：**
   - 仓库 → Settings → General → Features → 勾选 Issues

6. **可选 — 手动触发一次测试：**
   - 进入 Actions → "Weekly AI Agent Trending" → "Run workflow"

## 自定义

| 想改什么 | 改哪里 |
|----------|--------|
| 推送时间 | `.github/workflows/ai-agent-trending.yml` 中的 `cron` |
| 搜索关键词 | `scripts/ai_agent_trending.py` 中 `main()` 里的 query |
| 结果显示条数 | 各 `search_*()` 调用的 `limit` 参数 |

## 定时规则 (cron)

当前设置：`0 1 * * 1` = 每周一 UTC 01:00 = 北京时间 09:00

修改示例：
- 每天跑：`0 1 * * *`
- 每周三：`0 1 * * 3`
- 每两周（用 cron 不支持，建议改成手动触发 + 提醒）

GitHub Actions 的 schedule 精度是 **±30 分钟**，不是精确到秒的。
