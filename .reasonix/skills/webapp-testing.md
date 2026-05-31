---
name: webapp-testing
description: 用 Playwright 测试本地 Web 应用（截图、调试 UI、浏览器日志）。触发：测试/调试前端/浏览器自动化。
runAs: subagent
---

# Web 应用测试

完整手册：`read_file(".reasonix/skills/anthropic/webapp-testing/SKILL.md")`

## 决策树

```
静态 HTML？ → 直接读 HTML 找选择器 → 写 Playwright 脚本
动态应用？ → 服务器在运行？
  ├─ 否 → python .reasonix/skills/anthropic/webapp-testing/scripts/with_server.py --help
  └─ 是 → 先侦察后行动
```

## Playwright 脚本模板

```python
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('http://localhost:5173')
    page.wait_for_load_state('networkidle')  # 关键！
    # 你的自动化逻辑
    browser.close()
```

## 侦察-后-行动

1. 截图: `page.screenshot(path='/tmp/inspect.png', full_page=True)`
2. 看 DOM: `page.content()`
3. 找选择器: `page.locator('button').all()`
4. 执行操作

## 常见错误

❌ 在 `networkidle` 之前检查 DOM
✅ 始终先 `wait_for_load_state('networkidle')`
