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


def _format_repo_qq_detailed(repo: dict, rank: int) -> str:
    """Format a single repo for QQ markdown — name, stars, lang, description."""
    name = repo["full_name"]
    stars = repo["stargazers_count"]
    lang = repo.get("language") or "—"
    desc = (repo.get("description") or "").strip()
    if len(desc) > 80:
        desc = desc[:77] + "..."
    return f"{rank}. **{name}** ⭐{stars:,}  {lang}  \n  {desc}"


def _build_qq_markdown(results: list[tuple[str, list[dict]]], issue_url: str) -> str:
    """Build a detailed QQ markdown message with all categories."""
    today = datetime.utcnow().strftime("%m/%d")
    lines = [f"# 🤖 AI Agent 每周速递 — {today}", ""]

    # ── TOP 5 总榜 ──
    all_repos = []
    for _, repos in results:
        all_repos.extend(repos)
    seen = set()
    unique = []
    for repo in sorted(all_repos, key=lambda r: r["stargazers_count"], reverse=True):
        if repo["full_name"] not in seen:
            seen.add(repo["full_name"])
            unique.append(repo)

    lines.append("## 🔥 TOP 5 总榜")
    lines.append("")
    for rank, repo in enumerate(unique[:5], 1):
        lines.append(_format_repo_qq_detailed(repo, rank))
    lines.append("")

    # ── 分类详情 ──
    for label, repos in results:
        if not repos:
            continue
        lines.append(f"## {label}")
        lines.append("")
        for rank, repo in enumerate(repos[:5], 1):
            lines.append(_format_repo_qq_detailed(repo, rank))
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
