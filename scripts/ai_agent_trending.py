"""
Weekly AI Agent Trending — fetch trending AI agent repos from GitHub
and create an Issue summarizing this week's findings.
"""

import os
import json
import requests
from datetime import datetime, timedelta

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
REPO = os.environ.get("GITHUB_REPOSITORY", "owner/repo")

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
}

API = "https://api.github.com"


def search_repos(query: str, sort: str = "stars", per_page: int = 15) -> list[dict]:
    """Search GitHub repositories."""
    url = f"{API}/search/repositories"
    params = {
        "q": query,
        "sort": sort,
        "order": "desc",
        "per_page": per_page,
    }
    r = requests.get(url, headers=HEADERS, params=params, timeout=30)
    r.raise_for_status()
    return r.json().get("items", [])


def format_repo(repo: dict, rank: int) -> str:
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
            lines.append(format_repo(repo, rank))
        lines.append("")

    lines.append("---")
    lines.append(f"*由 [Weekly AI Agent Trending]({os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{REPO}/actions) 自动生成*")

    issue_body = "\n".join(lines)

    # ----- Create Issue -----
    issue_url = f"{API}/repos/{REPO}/issues"
    payload = {
        "title": f"🤖 AI Agent 每周速递 — {today}",
        "body": issue_body,
        "labels": ["ai-agent", "trending", "automated"],
    }
    r = requests.post(issue_url, headers=HEADERS, json=payload, timeout=30)

    if r.status_code == 201:
        print(f"✅ Issue created: {r.json()['html_url']}")
    else:
        print(f"❌ Failed to create issue ({r.status_code}): {r.text}")
        # Fallback: print to stdout so it appears in the Actions log
        print("\n--- ISSUE BODY BELOW ---\n")
        print(issue_body)


if __name__ == "__main__":
    main()
