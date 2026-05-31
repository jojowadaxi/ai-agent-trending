"""
Weekly AI Agent Trending — fetch trending AI agent repos from GitHub,
create an Issue, and push summary via Server酱 (WeChat) + QQ Bot.
"""

import os
import json
import requests
from datetime import datetime, timedelta

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
REPO = os.environ.get("GITHUB_REPOSITORY", "owner/repo")

# Server酱 SendKey（从 GitHub Secrets 读取）
SCT_SENDKEY = os.environ.get("SCT_SENDKEY", "")

# QQ Bot 配置（从 GitHub Secrets 读取）
QQ_APPID = os.environ.get("QQ_APPID", "")
QQ_SECRET = os.environ.get("QQ_SECRET", "")
QQ_OPENID = os.environ.get("QQ_OPENID", "")  # 接收消息的 QQ 用户 openid

QQ_API = "https://api.sgroup.qq.com"

GH_HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
}

GH_API = "https://api.github.com"


def search_repos(query: str, sort: str = "stars", per_page: int = 15) -> list[dict]:
    """Search GitHub repositories."""
    url = f"{GH_API}/search/repositories"
    params = {
        "q": query,
        "sort": sort,
        "order": "desc",
        "per_page": per_page,
    }
    r = requests.get(url, headers=GH_HEADERS, params=params, timeout=30)
    r.raise_for_status()
    return r.json().get("items", [])


def format_repo_md(repo: dict, rank: int) -> str:
    """Format a single repo as a markdown table row."""
    name = repo["full_name"]
    url = repo["html_url"]
    stars = repo["stargazers_count"]
    desc = (repo.get("description") or "").replace("\n", " ").strip()
    if len(desc) > 100:
        desc = desc[:97] + "..."
    lang = repo.get("language") or "—"
    pushed = repo.get("pushed_at", "")[:10]
    return f"| {rank} | [{name}]({url}) | ⭐ {stars:,} | {lang} | {pushed} | {desc} |"


def format_repo_wx(repo: dict) -> str:
    """Format a single repo for WeChat message (compact markdown)."""
    name = repo["full_name"]
    stars = repo["stargazers_count"]
    url = repo["html_url"]
    desc = (repo.get("description") or "").strip()
    if len(desc) > 60:
        desc = desc[:57] + "..."
    return f"- ⭐{stars:,} [{name}]({url})  \n  {desc}"


# ── Server酱 推送 ──────────────────────────────────────────

def send_wechat_summary(top_repos: list[dict], issue_url: str) -> bool:
    """Send weekly summary to WeChat via Server酱."""
    if not SCT_SENDKEY:
        print("⚠️ SCT_SENDKEY not configured, skipping WeChat notification.")
        return False

    today = datetime.utcnow().strftime("%m/%d")
    lines = []
    for i, repo in enumerate(top_repos[:10], 1):
        lines.append(f"{i}. {format_repo_wx(repo)}")

    title = f"🤖 AI Agent 每周速递 — {today}"
    body = "\n\n".join(lines)
    body += f"\n\n👉 [查看详情]({issue_url})"

    try:
        r = requests.post(
            f"https://sctapi.ftqq.com/{SCT_SENDKEY}.send",
            data={"title": title, "desp": body},
            timeout=15,
        )
        if r.status_code == 200:
            print("✅ WeChat message sent!")
            return True
        else:
            print(f"❌ Server酱 send failed ({r.status_code}): {r.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Server酱 error: {e}")
        return False


# ── QQ Bot 推送 ────────────────────────────────────────────

def _get_qq_access_token() -> str | None:
    """获取 QQ Bot access_token，失败返回 None。"""
    if not QQ_APPID or not QQ_SECRET:
        print("⚠️ QQ_APPID / QQ_SECRET not configured, skipping QQ notification.")
        return None
    try:
        r = requests.post(
            "https://bots.qq.com/app/getAppAccessToken",
            json={"appId": QQ_APPID, "clientSecret": QQ_SECRET},
            timeout=15,
        )
        r.raise_for_status()
        token = r.json()["access_token"]
        print(f"✅ QQ access_token obtained: {token[:10]}...")
        return token
    except Exception as e:
        print(f"❌ Failed to get QQ access_token: {e}")
        return None


# ── 中文标签映射 ──────────────────────────────────────────

# (关键词列表, 中文标签, emoji)
_TAG_RULES: list[tuple[list[str], str]] = [
    (["agent framework", "multi-agent", "agent orchestration", "agent team",
      "agent harness", "agent swarm", "agentic framework"], "Agent框架"),
    (["mcp server", "mcp client", "mcp ", "model context protocol"], "MCP工具"),
    (["knowledge graph", "code graph", "codegraph", "understand-anything",
      "knowledge base", "codebase graph"], "知识图谱"),
    (["security", "cybersecurity", "vulnerability", "pentest",
      "owasp", "attack", "defend"], "安全"),
    (["plugin", "skill", "extension", "harness", "addon"], "插件/技能"),
    (["video", "短视频", "video generation", "short video"], "视频生成"),
    (["markdown", "markitdown", "document convert", "office",
      "pdf", "docx", "converter"], "文档工具"),
    (["voice", "speech", "audio", "tts", "stt", "voice ai"], "语音AI"),
    (["governance", "compliance", "policy", "zero-trust"], "治理"),
    (["tutorial", "from scratch", "engineering", "learn it",
      "build it", "ship it"], "教程"),
    (["terminal", "cli ", "command line", "terminal agent"], "终端工具"),
    (["censorship", "uncensored", "uncensor", "heretic"], "审查移除"),
    (["cursor", "claude code", "codex", "copilot", "gemini cli",
      "coding agent", "code agent", "ai coding"], "编码助手"),
    (["taste", "slop", "writing style", "prose"], "文本优化"),
    (["memory", "context", "long-term", "persistent"], "记忆/上下文"),
]


def _tag_repo(repo: dict) -> str:
    """Assign a Chinese tag to a repo based on description + name keywords."""
    text = ((repo.get("description") or "") + " " + repo["full_name"]).lower()
    for keywords, tag in _TAG_RULES:
        for kw in keywords:
            if kw in text:
                return tag
    return "其他"


def _score_repo(repo: dict) -> float:
    """Score a repo for curation (0-100). Stars + recency + relevance."""
    stars = repo.get("stargazers_count", 0) or 0
    # diminishing returns: 100 stars → 25, 10000 stars → 63
    score = min(80, stars ** 0.35 * 5)

    # recency bonus (pushed in last 30 days)
    pushed = repo.get("pushed_at", "")
    if pushed:
        try:
            pushed_dt = datetime.fromisoformat(pushed.replace("Z", "+00:00"))
            days_ago = (datetime.utcnow().replace(tzinfo=pushed_dt.tzinfo) - pushed_dt).days
            if days_ago <= 7:
                score += 15
            elif days_ago <= 30:
                score += 8
        except ValueError:
            pass

    # created this week bonus
    created = repo.get("created_at", "")
    if created:
        try:
            created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
            days_ago = (datetime.utcnow().replace(tzinfo=created_dt.tzinfo) - created_dt).days
            if days_ago <= 7:
                score += 20
            elif days_ago <= 14:
                score += 10
        except ValueError:
            pass

    # agent relevance bonus
    text = ((repo.get("description") or "") + " " + repo["full_name"]).lower()
    agent_keywords = ["agent", "agentic", "mcp", "llm", "ai "]
    hits = sum(1 for kw in agent_keywords if kw in text)
    score += hits * 3

    return min(100, score)


def _format_curated_repo(repo: dict, rank: int) -> str:
    """Format one curated repo with Chinese tag and score signal."""
    name = repo["full_name"]
    stars = repo.get("stargazers_count", 0) or 0
    score = _score_repo(repo)
    tag = _tag_repo(repo)

    # visual signal
    signal = "🔥" if score >= 70 else ("⚡" if score >= 50 else "📌")

    # description — trim and use as-is (English is OK, tag is Chinese)
    desc = (repo.get("description") or "").strip()
    if len(desc) > 70:
        desc = desc[:67] + "..."

    return (f"{rank}. {signal} **{name}**  [{tag}]  ⭐{stars:,}\n"
            f"  {desc}")


def _build_qq_markdown(results: list[tuple[str, list[dict]]], issue_url: str) -> str:
    """Build curated QQ markdown: scored, tagged, only top picks."""
    today = datetime.utcnow().strftime("%m/%d")
    lines = [f"# 🤖 AI Agent 每周速递 — {today}", ""]

    # ── 收集 + 去重 + 评分 ──
    all_repos: list[dict] = []
    seen = set()
    for _, repos in results:
        for repo in repos:
            if repo["full_name"] not in seen:
                seen.add(repo["full_name"])
                all_repos.append(repo)

    scored = sorted(all_repos, key=lambda r: _score_repo(r), reverse=True)

    # ── 精选推荐 (top 8) ──
    lines.append("## 🏆 精选推荐")
    lines.append("")
    for rank, repo in enumerate(scored[:8], 1):
        lines.append(_format_curated_repo(repo, rank))
    lines.append("")

    # ── 值得关注 (next 6) ──
    if len(scored) > 8:
        lines.append("## 👀 值得关注")
        lines.append("")
        for rank, repo in enumerate(scored[8:14], 1):
            lines.append(_format_curated_repo(repo, rank))
        lines.append("")

    # ── 本周新项目 ──
    week_ago = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
    new_this_week = [
        r for r in all_repos
        if (r.get("created_at") or "")[:10] >= week_ago
    ]
    if new_this_week:
        new_sorted = sorted(new_this_week, key=lambda r: r.get("stargazers_count", 0) or 0, reverse=True)
        lines.append("## 🆕 本周新项目")
        lines.append("")
        for rank, repo in enumerate(new_sorted[:5], 1):
            name = repo["full_name"]
            stars = repo.get("stargazers_count", 0) or 0
            desc = (repo.get("description") or "").strip()
            if len(desc) > 60:
                desc = desc[:57] + "..."
            lines.append(f"{rank}. **{name}** ⭐{stars:,}\n  {desc}")
        lines.append("")

    lines.append("---")
    lines.append(f"👉 [查看完整 Issue]({issue_url})")

    return "\n".join(lines)


def send_qq_summary(results: list[tuple[str, list[dict]]], issue_url: str) -> bool:
    """Send detailed weekly summary to QQ via QQ Bot C2C (主动消息，每月限4条)."""
    if not QQ_OPENID:
        print("⚠️ QQ_OPENID not configured, skipping QQ notification.")
        return False

    token = _get_qq_access_token()
    if not token:
        return False

    markdown_content = _build_qq_markdown(results, issue_url)

    try:
        r = requests.post(
            f"{QQ_API}/v2/users/{QQ_OPENID}/messages",
            json={
                "msg_type": 2,  # markdown
                "markdown": {"content": markdown_content},
            },
            headers={
                "Authorization": f"QQBot {token}",
                "Content-Type": "application/json",
            },
            timeout=15,
        )
        if r.status_code == 200:
            print("✅ QQ message sent!")
            return True
        else:
            print(f"❌ QQ send failed ({r.status_code}): {r.text[:300]}")
            return False
    except Exception as e:
        print(f"❌ QQ error: {e}")
        return False


def search_topic(topic: str, label: str, limit: int = 15) -> list[dict]:
    """Search repos by topic."""
    return search_repos(f"topic:{topic}", per_page=limit)


def search_keyword(keyword: str, label: str, limit: int = 15) -> list[dict]:
    """Search repos by keyword, excluding the topic to reduce overlap."""
    return search_repos(f'"{keyword}" in:name,description', per_page=limit)


def main():
    results: list[tuple[str, list[dict]]] = []

    # 1. AI Agent 相关 topic
    for topic in ["ai-agent", "agentic-ai", "ai-agents"]:
        repos = search_topic(topic, topic)
        if repos:
            results.append((f"Topic: `{topic}` (按 Stars 排序)", repos[:10]))

    # 2. Agent 框架
    frameworks = search_repos(
        '"agent framework" in:name,description stars:>100 pushed:>2025-01-01',
        per_page=10,
    )
    if frameworks:
        results.append(("新兴 Agent 框架 (名称/描述含 'agent framework', >100 stars, 今年活跃)", frameworks))

    # 3. Agent 记忆 / 工具
    agent_tools = search_repos(
        '("agent memory" OR "agent tool" OR "mcp server") in:name,description stars:>50 pushed:>2025-06-01',
        per_page=10,
    )
    if agent_tools:
        results.append(("Agent 工具 & 记忆 & MCP (>50 stars, 近期活跃)", agent_tools))

    # 4. 本周新星 — created in last 7 days, most stars
    week_ago = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
    new_repos = search_repos(
        f"agent in:name,description created:>{week_ago}",
        sort="stars",
        per_page=10,
    )
    if new_repos:
        results.append(("🆕 本周新项目 (含 'agent', 按 Stars 排序)", new_repos))

    # ----- Build Issue Body -----
    today = datetime.utcnow().strftime("%Y-%m-%d")
    lines = [
        f"# 🤖 AI Agent Trending — {today}",
        "",
        f"每周自动抓取 GitHub 上与 AI Agent 相关的热门/新晋项目。",
        "",
    ]

    for i, (label, repos) in enumerate(results):
        lines.append(f"## {label}")
        lines.append("")
        lines.append("| # | 仓库 | Stars | 语言 | 最近更新 | 简介 |")
        lines.append("|---|------|-------|------|----------|------|")
        for rank, repo in enumerate(repos, 1):
            lines.append(format_repo_md(repo, rank))
        lines.append("")

    lines.append("---")
    lines.append(f"*由 [Weekly AI Agent Trending]({os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{REPO}/actions) 自动生成*")

    issue_body = "\n".join(lines)

    # ----- Create Issue -----
    issue_url = f"{GH_API}/repos/{REPO}/issues"
    payload = {
        "title": f"🤖 AI Agent 每周速递 — {today}",
        "body": issue_body,
        "labels": ["ai-agent", "trending", "automated"],
    }
    r = requests.post(issue_url, headers=GH_HEADERS, json=payload, timeout=30)

    if r.status_code == 201:
        issue_url_html = r.json()["html_url"]
        print(f"✅ Issue created: {issue_url_html}")
    else:
        print(f"❌ Failed to create issue ({r.status_code}): {r.text}")
        print("\n--- ISSUE BODY BELOW ---\n")
        print(issue_body)

    # ----- Send WeChat notification via Server酱 -----
    all_repos = []
    for _, repos in results:
        all_repos.extend(repos)
    seen = set()
    unique = []
    for repo in sorted(all_repos, key=lambda r: r["stargazers_count"], reverse=True):
        if repo["full_name"] not in seen:
            seen.add(repo["full_name"])
            unique.append(repo)
    send_wechat_summary(unique, issue_url_html)
    send_qq_summary(results, issue_url_html)


if __name__ == "__main__":
    main()
