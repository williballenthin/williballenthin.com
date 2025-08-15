#!/usr/bin/env python3
# /// script
# dependencies = [
#    "rich>=13.0.0",
#    "requests>=2.31.0",
# ]
# ///

import os
import json
import logging
import sqlite3
import argparse
import requests
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from rich.console import Console
from rich.logging import RichHandler

logger = logging.getLogger(__name__)


@dataclass
class PluginActivity:
    repository: str
    name: str
    commits: List[Dict[str, Any]]
    releases: List[Dict[str, Any]]
    new_plugin: bool = False


def log_rate_limit_status(response: requests.Response) -> None:
    """Log GraphQL rate limit status"""
    remaining = response.headers.get("x-ratelimit-remaining")
    limit = response.headers.get("x-ratelimit-limit")
    if remaining and limit:
        logger.debug("GraphQL rate limit: %s/%s points remaining", remaining, limit)


def handle_rate_limit_response(response: requests.Response, attempt: int = 1) -> bool:
    """Handle rate limit responses with exponential backoff"""
    if response.status_code in [403, 429]:
        retry_after = response.headers.get("retry-after")
        if retry_after:
            wait_time = int(retry_after)
            logger.warning("Rate limited. Waiting %d seconds", wait_time)
        else:
            wait_time = min(2 ** attempt, 60)
            logger.warning("Rate limited (attempt %d). Waiting %d seconds", attempt, wait_time)
        
        time.sleep(wait_time)
        return attempt < 5
    
    return False


def get_plugins_from_database(db_path: str) -> List[Dict[str, Any]]:
    """Read plugins from the SQLite database"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT org, repository, created_at, added_at
        FROM repositories
        ORDER BY added_at DESC
    """)
    
    plugins = []
    for row in cursor.fetchall():
        plugins.append({
            'org': row['org'],
            'repository': row['repository'],
            'full_name': f"{row['org']}/{row['repository']}",
            'created_at': row['created_at'],
            'added_at': row['added_at']
        })
    
    conn.close()
    return plugins


def build_prefilter_query(repositories: List[str]) -> str:
    """Build a GraphQL query to fetch pushedAt timestamps for multiple repositories"""
    query_parts = ["query("]
    variables_parts = []
    query_body_parts = []
    
    for i, repo in enumerate(repositories):
        owner, name = repo.split('/', 1)
        alias = f"repo{i}"
        
        variables_parts.extend([
            f"${alias}Owner: String!",
            f"${alias}Name: String!"
        ])
        
        query_body_parts.append(f"""
        {alias}: repository(owner: ${alias}Owner, name: ${alias}Name) {{
          nameWithOwner
          pushedAt
        }}""")
    
    query_parts.append(", ".join(variables_parts))
    query_parts.append(") {")
    query_parts.extend(query_body_parts)
    query_parts.append("""
      rateLimit {
        remaining
        limit
      }
    }""")
    
    return "".join(query_parts)


def build_batch_variables(repositories: List[str]) -> Dict[str, str]:
    """Build variables for the batch GraphQL query"""
    variables = {}
    
    for i, repo in enumerate(repositories):
        owner, name = repo.split('/', 1)
        alias = f"repo{i}"
        variables[f"{alias}Owner"] = owner
        variables[f"{alias}Name"] = name
    
    return variables


def fetch_repositories_timestamps_batch(token: str, repositories: List[str]) -> Dict[str, Optional[datetime]]:
    """Fetch pushedAt timestamps for multiple repositories in a single GraphQL query"""
    if not repositories:
        return {}
    
    query = build_prefilter_query(repositories)
    variables = build_batch_variables(repositories)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    attempt = 1
    while attempt <= 5:
        if attempt > 1:
            time.sleep(2)
        
        response = requests.post(
            "https://api.github.com/graphql",
            json={"query": query, "variables": variables},
            headers=headers
        )
        
        log_rate_limit_status(response)
        
        if response.status_code == 200:
            break
        elif handle_rate_limit_response(response, attempt):
            attempt += 1
            continue
        else:
            logger.error("Prefilter GraphQL request failed after retries: %s", response.text)
            return {}
    
    if response.status_code != 200:
        logger.error("Failed to fetch repository timestamps: %s", response.text)
        return {}
    
    data = response.json()
    if "errors" in data:
        logger.error("GraphQL errors in prefilter request: %s", data["errors"])
        return {}
    
    results = {}
    for i, repository in enumerate(repositories):
        alias = f"repo{i}"
        repo_data = data["data"].get(alias)
        
        if not repo_data:
            logger.warning("Repository %s not found or inaccessible", repository)
            results[repository] = None
            continue
        
        pushed_at_str = repo_data.get("pushedAt")
        if pushed_at_str:
            pushed_at = datetime.fromisoformat(pushed_at_str.replace("Z", "+00:00"))
            results[repository] = pushed_at
        else:
            results[repository] = None
    
    return results


def build_batch_query(repositories: List[str], since_date: datetime) -> str:
    """Build a GraphQL query to fetch activity for multiple repositories at once"""
    since_iso = since_date.isoformat()
    
    query_parts = ["query("]
    variables_parts = []
    query_body_parts = []
    
    for i, repo in enumerate(repositories):
        owner, name = repo.split('/', 1)
        alias = f"repo{i}"
        
        variables_parts.extend([
            f"${alias}Owner: String!",
            f"${alias}Name: String!"
        ])
        
        query_body_parts.append(f"""
        {alias}: repository(owner: ${alias}Owner, name: ${alias}Name) {{
          nameWithOwner
          object(expression: "HEAD") {{
            ... on Commit {{
              history(first: 20, since: "{since_iso}") {{
                nodes {{
                  oid
                  messageHeadline
                  committedDate
                  url
                }}
              }}
            }}
          }}
          releases(first: 20, orderBy: {{field: CREATED_AT, direction: DESC}}) {{
            nodes {{
              name
              tagName
              createdAt
              url
            }}
          }}
        }}""")
    
    query_parts.append(", ".join(variables_parts))
    query_parts.append(") {")
    query_parts.extend(query_body_parts)
    query_parts.append("""
      rateLimit {
        remaining
        limit
      }
    }""")
    
    return "".join(query_parts)


def fetch_repositories_activity_batch(token: str, repositories: List[str], since_date: datetime) -> Dict[str, Dict[str, Any]]:
    """Fetch commits and releases for multiple repositories in a single GraphQL query"""
    if not repositories:
        return {}
    
    query = build_batch_query(repositories, since_date)
    variables = build_batch_variables(repositories)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    attempt = 1
    while attempt <= 5:
        if attempt > 1:
            time.sleep(2)
        
        response = requests.post(
            "https://api.github.com/graphql",
            json={"query": query, "variables": variables},
            headers=headers
        )
        
        log_rate_limit_status(response)
        
        if response.status_code == 200:
            break
        elif handle_rate_limit_response(response, attempt):
            attempt += 1
            continue
        else:
            logger.error("Batch GraphQL request failed after retries: %s", response.text)
            return {}
    
    if response.status_code != 200:
        logger.error("Failed to fetch batch activity: %s", response.text)
        return {}
    
    data = response.json()
    if "errors" in data:
        logger.error("GraphQL errors in batch request: %s", data["errors"])
        return {}
    
    results = {}
    for i, repository in enumerate(repositories):
        alias = f"repo{i}"
        repo_data = data["data"].get(alias)
        
        if not repo_data:
            logger.warning("Repository %s not found or inaccessible", repository)
            results[repository] = {"commits": [], "releases": []}
            continue
        
        # Filter commits to only include those from the target day
        commits = []
        if repo_data["object"] and repo_data["object"]["history"]:
            end_date = since_date + timedelta(days=1)
            for commit in repo_data["object"]["history"]["nodes"]:
                commit_date = datetime.fromisoformat(commit["committedDate"].replace("Z", "+00:00"))
                if since_date <= commit_date < end_date:
                    commits.append(commit)
        
        # Filter releases to only include those created on the target day
        releases = []
        for release in repo_data["releases"]["nodes"]:
            release_date = datetime.fromisoformat(release["createdAt"].replace("Z", "+00:00"))
            if since_date <= release_date < end_date:
                releases.append(release)
        
        results[repository] = {"commits": commits, "releases": releases}
    
    return results


def generate_markdown_content(activity_data: List[PluginActivity], target_date: datetime) -> str:
    """Generate markdown content for the activity report"""
    content = []
    
    # Hugo frontmatter
    date_str = target_date.strftime('%Y-%m-%d')
    current_date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    is_draft = target_date >= current_date
    title = f"IDA Plugin Updates on {date_str}"
    
    content.append("---")
    content.append(f"title: \"{title}\"")
    content.append(f"date: {date_str}T23:59:59")
    content.append(f"draft: {str(is_draft).lower()}")
    content.append("---")
    content.append("")
    content.append(f"# {title}")
    content.append("")
    
    new_plugins = [p for p in activity_data if p.new_plugin]
    if new_plugins:
        new_plugins.sort(key=lambda p: p.name.lower())
        content.append("### New Plugins:")
        for plugin in new_plugins:
            repo_url = f"https://github.com/{plugin.repository}"
            content.append(f"  - [{plugin.name}]({repo_url})")
        content.append("")
    
    releases_data = []
    for plugin in activity_data:
        for release in plugin.releases:
            releases_data.append((plugin, release))
    
    if releases_data:
        releases_data.sort(key=lambda item: item[0].name.lower())
        content.append("### New Releases:")
        for plugin, release in releases_data:
            repo_url = f"https://github.com/{plugin.repository}"
            release_name = release.get("name") or release.get("tagName", "Unknown")
            content.append(f"  - [{plugin.name}]({repo_url}) [{release_name}]({release['url']})")
        content.append("")
    
    plugins_with_commits = [p for p in activity_data if p.commits]
    if plugins_with_commits:
        plugins_with_commits.sort(key=lambda p: p.name.lower())
        content.append("### Activity:")
        for plugin in plugins_with_commits:
            repo_url = f"https://github.com/{plugin.repository}"
            content.append(f"  - [{plugin.name}]({repo_url})")
            
            for commit in plugin.commits:
                short_hash = commit["oid"][:8]
                commit_url = commit["url"]
                message = commit["messageHeadline"]
                content.append(f"    - [{short_hash}]({commit_url}): {message}")
        content.append("")

    content.append("<style>")
    content.append("/* wider content, default is 36em, which is a better text reading width */")
    content.append("nav.container,")
    content.append("main.container {")
    content.append("  max-width: 42em;")
    content.append("}")
    content.append("")
    content.append("</style>")
    
    return "\n".join(content)




def update_draft_status(output_dir: Path, target_date: datetime) -> None:
    """Update draft status for previous days' documents"""
    content_dir = output_dir / "content" / "ida" / "plugins" / "activity"
    
    # Look for files in the last 7 days
    for days_back in range(1, 8):
        check_date = target_date - timedelta(days=days_back)
        year = check_date.strftime('%Y')
        month = check_date.strftime('%m')
        day = check_date.strftime('%d')
        
        file_path = content_dir / year / month / f"{day}.md"
        
        if file_path.exists():
            with open(file_path, 'r') as f:
                content = f.read()
            
            if "draft: true" in content:
                logger.info("Updating draft status for %s", file_path)
                content = content.replace("draft: true", "draft: false")
                
                with open(file_path, 'w') as f:
                    f.write(content)
                
                logger.info("Set draft: false for %s", file_path)


def main():
    parser = argparse.ArgumentParser(description="Generate IDA plugin activity reports")
    parser.add_argument("database", help="Path to the SQLite database")
    parser.add_argument("output_dir", help="Path to the output directory")
    parser.add_argument("--date", help="Date to process (YYYY-MM-DD), defaults to today")
    
    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.INFO,
        handlers=[RichHandler(console=Console(stderr=True))],
    )
    
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable is required")
    
    if args.date:
        target_date = datetime.strptime(args.date, '%Y-%m-%d').replace(tzinfo=timezone.utc)
    else:
        target_date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
    
    logger.info("Processing activity for date: %s", target_date.strftime('%Y-%m-%d'))
    
    logger.info("Reading plugins from database: %s", args.database)
    plugins = get_plugins_from_database(args.database)
    logger.info("Found %d plugins in database", len(plugins))
    
    start_time = time.time()
    activity_data = []
    
    # if the batch is too large, then we get HTTP 502
    batch_size = 50
    repo_names = [plugin['full_name'] for plugin in plugins]
    
    # Step 1: Pre-filter repositories by checking their pushedAt timestamps
    logger.info("Pre-filtering repositories by last push timestamp...")
    prefilter_start = time.time()
    all_timestamps = {}
    
    for i in range(0, len(repo_names), batch_size):
        batch_repos = repo_names[i:i + batch_size]
        logger.info("Fetching timestamps for batch %d/%d (%d repositories)", 
                   i // batch_size + 1, 
                   (len(repo_names) + batch_size - 1) // batch_size,
                   len(batch_repos))
        
        batch_timestamps = fetch_repositories_timestamps_batch(token, batch_repos)
        all_timestamps.update(batch_timestamps)
    
    prefilter_time = time.time() - prefilter_start
    logger.info("Pre-filtering took %.2f seconds", prefilter_time)
    
    # Filter to only repositories that were pushed to on or after the target date
    end_date = target_date + timedelta(days=1)
    candidate_repos = []
    candidate_plugins = []
    
    for plugin in plugins:
        repo_name = plugin['full_name']
        pushed_at = all_timestamps.get(repo_name)
        
        # Include repository if:
        # 1. It was pushed to on or after target date, OR
        # 2. It was added on the target date (new plugin), OR
        # 3. We couldn't get its timestamp (to be safe)
        added_date = datetime.fromisoformat(plugin['added_at'])
        is_new_plugin = added_date.date() == target_date.date()
        
        if (pushed_at is None or 
            pushed_at >= target_date or 
            is_new_plugin):
            candidate_repos.append(repo_name)
            candidate_plugins.append(plugin)
    
    reduction_pct = 100 * (1 - len(candidate_repos) / len(repo_names)) if len(repo_names) > 0 else 0
    logger.info("Filtered from %d to %d repositories that might have activity (%.1f%% reduction)", 
               len(repo_names), len(candidate_repos), reduction_pct)
    
    # Step 2: Fetch detailed activity for candidate repositories only
    detail_start = time.time()
    for i in range(0, len(candidate_repos), batch_size):
        batch_repos = candidate_repos[i:i + batch_size]
        batch_plugins = candidate_plugins[i:i + batch_size]
        logger.info("Processing detailed activity for batch %d/%d (%d repositories)", 
                   i // batch_size + 1, 
                   (len(candidate_repos) + batch_size - 1) // batch_size,
                   len(batch_repos))
        
        batch_results = fetch_repositories_activity_batch(token, batch_repos, target_date)
        
        for plugin in batch_plugins:
            repo_name = plugin['full_name']
            
            added_date = datetime.fromisoformat(plugin['added_at'])
            is_new_plugin = added_date.date() == target_date.date()
            
            activity = batch_results.get(repo_name, {"commits": [], "releases": []})
            
            if activity["commits"] or activity["releases"] or is_new_plugin:
                plugin_activity = PluginActivity(
                    repository=repo_name,
                    name=plugin['repository'],  # Just the repo name without org
                    commits=activity["commits"],
                    releases=activity["releases"],
                    new_plugin=is_new_plugin
                )
                activity_data.append(plugin_activity)
                logger.info("Found activity for %s: %d commits, %d releases, new: %s",
                           repo_name, len(activity["commits"]), len(activity["releases"]), is_new_plugin)
    
    detail_time = time.time() - detail_start
    total_time = time.time() - start_time
    logger.info("Detailed activity fetching took %.2f seconds", detail_time)
    logger.info("Total processing time: %.2f seconds", total_time)
    
    if activity_data:
        logger.info("Generating activity report for %d repositories", len(activity_data))
        
        output_dir = Path(args.output_dir)
        year = target_date.strftime('%Y')
        month = target_date.strftime('%m')
        day = target_date.strftime('%d')
        
        
        content_dir = output_dir / "content" / "ida" / "plugins" / "activity" / year / month
        content_dir.mkdir(parents=True, exist_ok=True)
        
        markdown_content = generate_markdown_content(activity_data, target_date)
        
        output_file = content_dir / f"{day}.md"
        with open(output_file, 'w') as f:
            f.write(markdown_content)
        
        logger.info("Activity report written to: %s", output_file)
        
        update_draft_status(output_dir, target_date)
        
    else:
        logger.info("No activity found for date: %s", target_date.strftime('%Y-%m-%d'))


if __name__ == "__main__":
    main()
