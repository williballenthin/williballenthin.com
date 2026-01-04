# You can invoke this script with `uv run` (v0.3+):
#
#     uv run tools/github-ida-plugins/fetch-github-ida-plugins-no-pygithub.py \
#       > static/fragments/github-ida-plugins/list.html
#
# /// script
# dependencies = [
#    "rich>=13.0.0",
#    "jinja2>=3.1.0",
#    "requests>=2.31.0",
# ]
# ///
#
# requires env variable GITHUB_TOKEN to be set.
import os
import json
import logging
import requests
import sqlite3
import time
from datetime import datetime
from dataclasses import dataclass
from urllib.parse import urlparse
from typing import Optional

from jinja2 import Template
from rich.console import Console
from rich.logging import RichHandler

logger = logging.getLogger(__name__)

# URL for the official HexRays plugin repository metadata
HEXRAYS_PLUGIN_REPOSITORY_URL = "https://raw.githubusercontent.com/HexRaysSA/plugin-repository/refs/heads/v1/plugin-repository.json"

# these are handpicked repos to ignore
# due to embedding the IDA SDK/example plugins
DENYLIST = (
    "clovme/WTools",
    "zoronikkill/idk",
    "BraveCattle/ctf",
    "vAlerainTech/vAlerain-Ark",
    "carsond135/malwareanalysis",
    "Ph0en1x-XMU/Ph0en1x-Team",
    "zmrbak/IDAPython",
    "Russinovich/IDA7.5_SDK",
    "cedricp/ddt4all",
    "williballenthin/williballenthin.com",
    "datahaven-net/zenaida",
)

# we put the styles first because the body content can be pretty large (hundreds of KBs)
# which takes a moment to load.
PLUGIN_TEMPLATE = """
<style>
    #plugins.has-js thead {
        display: none;
    }

    #plugins tr td,
    table tr td {
        padding: 0;
        padding-top: 0.5em;
        vertical-align: top;
    }

    table tr td:nth-last-child(1) {
        text-align: right;
    }

    #plugins.no-js tr td:nth-last-child(1),
    #plugins.no-js tr td:nth-last-child(2),
    #plugins.no-js tr td:nth-last-child(3),
    #plugins.no-js tr td:nth-last-child(4),
    #plugins.no-js thead th:nth-last-child(1),
    #plugins.no-js thead th:nth-last-child(2),
    #plugins.no-js thead th:nth-last-child(3),
    #plugins.no-js thead th:nth-last-child(4) {
        display: none;
    }

    #sort-links.no-js {
        display: none;
    }
</style>

<p><strong>{{ plugins|length }} IDA Pro plugins found</strong>, generated: {{now.strftime('%B %d, %Y at %H:%M:%S')}}</p>

<div id="sort-links" class="no-js">
  <span>Sort by:</span>
  <a href="#" id="sort-repo">repo</a>
  <a href="#" id="sort-stars">stars</a>
  <a href="#" id="sort-forks">forks</a>
  <a href="#" id="sort-created">created</a>
  <a href="#" id="sort-pushed">pushed</a>*
</div>

<table id="plugins" class="no-js" style="table-layout: fixed; width: 100%;">
<thead>
    <tr>
        <th></th>
        <th width="100px"></th>
        <th>stars</th>
        <th>forks</th>
        <th>created</th>
        <th>pushed</th>
    </tr>
</thead>
<tbody>
    {% for plugin in plugins %}
  <tr>
    <td>
      <p>
        <b>
            <a class="contrast" href="https://www.github.com/{{ plugin.repository }}">
            {{ plugin.repository }}
            </a>
        </b>
        :: 
        <a href="{{ plugin.url }}">{{ plugin.file }}</a>
      </p>
      {% if plugin.description %}
        <p>
          {{ plugin.description }}
        </p>
      {% endif %}
    </td>
    <td>
        {{ plugin.stargazers_count }} <span class="decoration">stars</span><br />
        {{ plugin.forks_count }} <span class="decoration">forks</span><br />
        {% if plugin.created_at.year != plugin.pushed_at.year %}
            <span class="decoration">{{ plugin.created_at.year }}→{{ plugin.pushed_at.year - 2000 }}</span>
        {% else %}
            <span class="decoration">{{ plugin.created_at.year }}</span>
        {% endif %}
    </td>
    <td>{{plugin.stargazers_count}}</td>
    <td>{{plugin.forks_count}}</td>
    <td>{{plugin.created_at.date()}}</td>
    <td>{{plugin.pushed_at.date()}}</td>
  </tr>
  {% endfor %}
  </tbody>
</table>

<script src="/js/jquery-3.7.1.js"></script>
<link rel="stylesheet" type="text/css" href="/css/dataTables.dataTables.min.css">
<script src="/js/dataTables.min.js"></script>
<script>
    document.addEventListener('DOMContentLoaded', function() {
        const dt = new DataTable('#plugins', {
            pageLength: -1,
            layout: {
                topStart: null,
                topEnd: null,
                bottomStart: null,
                bottomEnd: null,
            },
            columnDefs: [
                { width: '100px', targets: 1 },
                { visible: false, targets: [2,3,4,5] }
            ],
            order: [[5, 'desc']],
        });

        $(".no-js").removeClass("no-js");
        $("#plugins").addClass("has-js");

        $('#sort-repo').click(function() {
            dt.column(0).order('asc').draw();
        });
        $('#sort-stars').click(function() {
            dt.column(2).order('desc').draw();
        });
        $('#sort-forks').click(function() {
            dt.column(3).order('desc').draw();
        });
        $('#sort-created').click(function() {
            dt.column(4).order('desc').draw();
        });
        $('#sort-pushed').click(function() {
            dt.column(5).order('desc').draw();
        });
    });
</script>
"""


@dataclass
class SearchResult:
    repository: str
    file: str
    url: str
    language: str


@dataclass
class IdaPlugin:
    repository: str
    parent: str | None  # parent repository if it's a fork
    description: str
    file: str
    url: str
    created_at: datetime
    pushed_at: datetime
    forks_count: int
    stargazers_count: int
    language: str


def extract_github_repo_from_url(url: str) -> Optional[str]:
    """Extract 'owner/repo' from a GitHub URL."""
    if not url:
        return None

    parsed = urlparse(url)
    if parsed.netloc not in ("github.com", "www.github.com"):
        return None

    # Path format: /owner/repo or /owner/repo/...
    parts = parsed.path.strip("/").split("/")
    if len(parts) >= 2:
        return f"{parts[0]}/{parts[1]}"
    return None


def fetch_hexrays_plugin_repositories() -> list[SearchResult]:
    """
    Fetch the official HexRays plugin repository JSON and extract GitHub repositories.

    Returns a list of SearchResult entries for GitHub-hosted plugins.
    """
    results = []

    try:
        logger.info("Fetching HexRays plugin repository from %s", HEXRAYS_PLUGIN_REPOSITORY_URL)
        response = requests.get(HEXRAYS_PLUGIN_REPOSITORY_URL, timeout=30)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logger.warning("Failed to fetch HexRays plugin repository: %s", e)
        return results
    except json.JSONDecodeError as e:
        logger.warning("Failed to parse HexRays plugin repository JSON: %s", e)
        return results

    plugins = data.get("plugins", [])
    logger.info("Found %d plugins in HexRays repository", len(plugins))

    seen_repos = set()

    for plugin in plugins:
        # Primary source: the 'host' field which is typically the repository URL
        host_url = plugin.get("host", "")
        repo_name = extract_github_repo_from_url(host_url)

        if repo_name and repo_name not in seen_repos and repo_name not in DENYLIST:
            seen_repos.add(repo_name)

            # Get plugin name from metadata if available
            plugin_name = plugin.get("name", "")

            # Try to get a description from metadata
            description = ""
            versions = plugin.get("versions", {})
            for version_key, distributions in versions.items():
                if distributions and len(distributions) > 0:
                    metadata = distributions[0].get("metadata", {})
                    description = metadata.get("description", "")
                    if description:
                        break

            results.append(SearchResult(
                repository=repo_name,
                file="(HexRays plugin repository)",
                url=host_url,
                language="plugin-repository",
            ))
            logger.info("Found HexRays plugin: %s (%s)", repo_name, plugin_name or "unnamed")

    logger.info("Extracted %d unique GitHub repositories from HexRays plugin repository", len(results))
    return results


def log_rate_limit_status(response: requests.Response, api_type: str = "REST") -> None:
    if api_type == "GraphQL":
        remaining = response.headers.get("x-ratelimit-remaining")
        limit = response.headers.get("x-ratelimit-limit")
        if remaining and limit:
            logger.debug("GraphQL rate limit: %s/%s points remaining", remaining, limit)
    else:
        remaining = response.headers.get("x-ratelimit-remaining")
        limit = response.headers.get("x-ratelimit-limit")
        if remaining and limit:
            logger.debug("REST rate limit: %s/%s requests remaining", remaining, limit)


def handle_rate_limit_response(response: requests.Response, attempt: int = 1) -> bool:
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


def search_github_code(token: str, query: str, limit: int | None = None) -> list[dict]:
    """Search GitHub code using REST API directly with rate limit handling."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    results = []
    page = 1
    per_page = 100  # GitHub's max per page
    
    while True:
        url = f"https://api.github.com/search/code"
        params = {
            "q": query,
            "page": page,
            "per_page": per_page
        }
        
        attempt = 1
        while attempt <= 5:
            if page > 1 or attempt > 1:
                time.sleep(7)
            
            response = requests.get(url, headers=headers, params=params)
            log_rate_limit_status(response, "REST")
            
            if response.status_code == 200:
                break
            elif handle_rate_limit_response(response, attempt):
                attempt += 1
                continue
            else:
                logger.error("Search request failed after retries: %s", response.text)
                return results
        
        if response.status_code != 200:
            logger.error("Search request failed: %s", response.text)
            break
            
        data = response.json()
        
        if "items" not in data:
            logger.error("No items in search response: %s", data)
            break
            
        results.extend(data["items"])
        logger.info("Collected %d results from page %d", len(data["items"]), page)
        
        if limit and len(results) >= limit:
            results = results[:limit]
            break
            
        if len(data["items"]) < per_page:
            break
            
        page += 1
        
    logger.info("Collected %d total search results", len(results))
    return results


def collect_search_results(token: str, limit: int | None = None) -> list[SearchResult]:
    """Collect search results using direct API calls."""
    results = []
    seen_repos = set()

    # First, fetch plugins from the official HexRays plugin repository
    # This doesn't require GitHub API calls, so we do it first
    hexrays_results = fetch_hexrays_plugin_repositories()
    for result in hexrays_results:
        if result.repository not in seen_repos:
            seen_repos.add(result.repository)
            results.append(result)

    logger.info("After HexRays repository: %d unique repositories", len(results))

    # Define search configurations for GitHub code search
    search_configs = [
        {
            'query': 'language:python AND "def PLUGIN_ENTRY()" AND in:file',
            'language': 'python',
            'description': 'Python IDA plugins'
        },
        {
            'query': '"idaapi init" AND in:file AND language:"C++"',
            'language': 'C++',
            'description': 'C++ IDA plugins'
        },
        {
            'query': 'language:python AND "ida_domain" AND in:file',
            'language': 'python',
            'description': 'Python files with ida_domain'
        }
    ]

    # Process each search configuration
    for config in search_configs:
        query = config['query']
        language = config['language']
        description = config['description']

        logger.info("%s query: %s", description, query)

        search_results = search_github_code(token, query, limit)
        logger.info("found %d %s", len(search_results), description)

        for result in search_results:
            repo_name = result["repository"]["full_name"]
            file_path = result["path"]

            # Apply filtering logic
            if should_skip_result(repo_name, file_path, result["html_url"]):
                continue

            # Skip if we already have this repo from another source
            if repo_name in seen_repos:
                logger.debug("Skipping duplicate repository: %s", repo_name)
                continue

            seen_repos.add(repo_name)
            results.append(SearchResult(
                repository=repo_name,
                file=result["path"],
                url=result["html_url"],
                language=language
            ))
            logger.info("Found %s: %s", description.lower(), repo_name)

    logger.info("Total unique repositories collected: %d", len(results))
    return results


def should_skip_result(repo_name: str, file_path: str, html_url: str) -> bool:
    """Determine if a search result should be skipped based on filtering criteria."""
    # Skip repositories containing 'ddt4'
    if "ddt4" in repo_name.lower() or "ddt4" in file_path.lower():
        logger.debug("skipping %s: contains 'ddt4'", html_url)
        return True
    
    # Skip repositories in the denylist
    if repo_name in DENYLIST:
        logger.debug("skipping %s: denylist", html_url)
        return True
    
    return False


def batch_fetch_repositories(token: str, repo_names: set[str]) -> dict[str, dict]:
    """Fetch repository metadata in batches using GraphQL API with rate limit handling."""
    repo_data = {}
    repo_list = list(repo_names)
    
    # Process repositories in batches of 100 (GraphQL limit)
    for i in range(0, len(repo_list), 100):
        batch = repo_list[i:i + 100]
        logger.info("Fetching batch %d-%d of %d repositories", i + 1, min(i + 100, len(repo_list)), len(repo_list))
        
        # Build the search query string
        repo_query = " ".join(f"repo:{repo}" for repo in batch)
        
        graphql_query = {
            "query": """
            query($searchQuery: String!) {
              search(type: REPOSITORY, query: $searchQuery, first: 100) {
                nodes {
                  ... on Repository {
                    nameWithOwner
                    description
                    stargazerCount
                    forkCount
                    createdAt
                    pushedAt
                    isFork
                    parent {
                      nameWithOwner
                    }
                  }
                }
              }
              rateLimit {
                limit
                remaining
                used
                resetAt
              }
            }
            """,
            "variables": {
                "searchQuery": repo_query
            }
        }
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        attempt = 1
        while attempt <= 5:
            if i > 0 or attempt > 1:
                time.sleep(1)
            
            response = requests.post(
                "https://api.github.com/graphql",
                json=graphql_query,
                headers=headers
            )
            
            log_rate_limit_status(response, "GraphQL")
            
            if response.status_code == 200:
                break
            elif handle_rate_limit_response(response, attempt):
                attempt += 1
                continue
            else:
                logger.error("GraphQL request failed after retries: %s", response.text)
                break
        
        if response.status_code != 200:
            logger.error("GraphQL request failed: %s", response.text)
            continue
            
        data = response.json()
        if "errors" in data:
            logger.error("GraphQL errors: %s", data["errors"])
            continue
            
        if "data" in data and "rateLimit" in data["data"]:
            rate_limit = data["data"]["rateLimit"]
            logger.debug("GraphQL rate limit: %s/%s points remaining", 
                       rate_limit["remaining"], rate_limit["limit"])
            
        for repo in data["data"]["search"]["nodes"]:
            if repo:
                repo_data[repo["nameWithOwner"]] = repo
                
    logger.info("Successfully fetched metadata for %d repositories", len(repo_data))
    return repo_data


def combine_results(search_results: list[SearchResult], repo_data: dict[str, dict]) -> list[IdaPlugin]:
    """Combine search results with repository metadata."""
    plugins = []
    
    for result in search_results:
        repo_info = repo_data.get(result.repository)
        if not repo_info:
            logger.warning("No repository data found for %s", result.repository)
            continue
            
        created_at = datetime.fromisoformat(repo_info["createdAt"].replace("Z", "+00:00"))
        pushed_at = datetime.fromisoformat(repo_info["pushedAt"].replace("Z", "+00:00"))
        
        plugin = IdaPlugin(
            repository=result.repository,
            parent=repo_info["parent"]["nameWithOwner"] if repo_info.get("parent") else None,
            description=repo_info.get("description", ""),
            file=result.file,
            url=result.url,
            created_at=created_at,
            pushed_at=pushed_at,
            forks_count=repo_info["forkCount"],
            stargazers_count=repo_info["stargazerCount"],
            language=result.language,
        )
        plugins.append(plugin)
        
    return plugins


def search_and_render_plugins(limit: int | None = None) -> None:
    """Search for IDA plugins on GitHub and render HTML directly."""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable is required")
        
    search_results = collect_search_results(token, limit)
    
    if not search_results:
        logger.warning("No search results found")
        return
        
    repo_names = {result.repository for result in search_results}
    repo_data = batch_fetch_repositories(token, repo_names)
    
    plugins = combine_results(search_results, repo_data)
    plugins.sort(key=lambda p: p.pushed_at, reverse=True)
    
    logger.info("Total plugins processed: %d", len(plugins))
    
    now = datetime.now()
    template = Template(PLUGIN_TEMPLATE)
    print(template.render(plugins=plugins, now=now))


def search_and_render_plugins_json(limit: int | None = None) -> None:
    """Search for IDA plugins on GitHub and output JSONL (one JSON object per line)."""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable is required")
        
    # Phase 1: Collect search results
    logger.info("Phase 1: Collecting search results...")
    search_results = collect_search_results(token, limit)
    
    if not search_results:
        logger.warning("No search results found")
        return
        
    # Phase 2: Batch fetch repository metadata
    logger.info("Phase 2: Batch fetching repository metadata...")
    repo_names = {result.repository for result in search_results}
    repo_data = batch_fetch_repositories(token, repo_names)
    
    # Phase 3: Combine results
    logger.info("Phase 3: Combining results...")
    plugins = combine_results(search_results, repo_data)
    
    # Sort by pushed_at date (descending)
    plugins.sort(key=lambda p: p.pushed_at, reverse=True)
    
    logger.info("Total plugins processed: %d", len(plugins))
    
    for plugin in plugins:
        plugin_dict = {
            "repository": plugin.repository,
            "parent": plugin.parent,
            "description": plugin.description,
            "file": plugin.file,
            "url": plugin.url,
            "created_at": plugin.created_at.isoformat(),
            "pushed_at": plugin.pushed_at.isoformat(),
            "forks_count": plugin.forks_count,
            "stargazers_count": plugin.stargazers_count,
            "language": plugin.language,
        }
        print(json.dumps(plugin_dict))


def init_database(db_path: str) -> None:
    """Initialize the SQLite database with the repositories table."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS repositories (
            org TEXT NOT NULL,
            repository TEXT NOT NULL,
            created_at DATETIME NOT NULL,
            added_at DATETIME NOT NULL,
            UNIQUE(org, repository)
        )
    """)
    
    conn.commit()
    conn.close()


def search_and_update_plugins_database(db_path: str, limit: int | None = None) -> None:
    """Search for IDA plugins on GitHub and update the SQLite database."""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable is required")
    
    # Initialize database if it doesn't exist
    init_database(db_path)
    
    # Phase 1: Collect search results
    logger.info("Phase 1: Collecting search results...")
    search_results = collect_search_results(token, limit)
    
    if not search_results:
        logger.warning("No search results found")
        return
    
    # Phase 2: Batch fetch repository metadata
    logger.info("Phase 2: Batch fetching repository metadata...")
    repo_names = {result.repository for result in search_results}
    repo_data = batch_fetch_repositories(token, repo_names)
    
    # Phase 3: Combine results
    logger.info("Phase 3: Combining results...")
    plugins = combine_results(search_results, repo_data)
    
    # Phase 4: Update database
    logger.info("Phase 4: Updating database...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    added_count = 0
    current_time = datetime.now()
    
    for plugin in plugins:
        org, repo = plugin.repository.split('/', 1)
        
        try:
            cursor.execute("""
                INSERT INTO repositories (org, repository, created_at, added_at)
                VALUES (?, ?, ?, ?)
            """, (org, repo, plugin.created_at, current_time))
            added_count += 1
            logger.info("Added new repository: %s", plugin.repository)
        except sqlite3.IntegrityError:
            # Repository already exists, skip
            logger.debug("Repository already exists: %s", plugin.repository)
    
    conn.commit()
    conn.close()
    
    logger.info("Database updated: %d new repositories added", added_count)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Find IDA Pro plugins on GitHub and generate HTML (no PyGithub version)")
    parser.add_argument("--limit", type=int, help="Limit the number of results")
    parser.add_argument(
        "--json", action="store_true", help="Output as JSONL instead of HTML (one JSON object per line)"
    )
    parser.add_argument(
        "--database", type=str, help="Path to SQLite database to update with repository information"
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        handlers=[RichHandler(console=Console(stderr=True))],
    )

    if args.database:
        search_and_update_plugins_database(args.database, args.limit)
    elif args.json:
        search_and_render_plugins_json(args.limit)
    else:
        search_and_render_plugins(args.limit)


if __name__ == "__main__":
    main()
