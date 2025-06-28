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
import time
from datetime import datetime
from dataclasses import dataclass
from urllib.parse import urlparse
from typing import Optional

from jinja2 import Template
from rich.console import Console
from rich.logging import RichHandler

logger = logging.getLogger(__name__)

# these are handpicked repos to ignore
# due to embedding the IDA SDK/example plugins
DENYLIST = ("clovme/WTools", "zoronikkill/idk", "BraveCattle/ctf", "vAlerainTech/vAlerain-Ark", "carsond135/malwareanalysis", "Ph0en1x-XMU/Ph0en1x-Team", "zmrbak/IDAPython", "Russinovich/IDA7.5_SDK", "cedricp/ddt4all")

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

<p><strong>{{ plugins|length }} IDA Pro plugins found</strong></p>

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
<p class='feed-metadata-generated'>generated: {{now.strftime('%B %d, %Y at %H:%M:%S')}}</p>

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
    
    # Search for Python plugins
    python_query = 'language:python AND "def PLUGIN_ENTRY()" AND in:file'
    logger.info("Python query: %s", python_query)
    
    python_results = search_github_code(token, python_query, limit)
    logger.info("found %d Python IDA plugins", len(python_results))
    
    for result in python_results:
        repo_name = result["repository"]["full_name"]
        
        if repo_name in DENYLIST:
            logger.debug("skipping %s: denylist", result["html_url"])
            continue
            
        results.append(SearchResult(
            repository=repo_name,
            file=result["path"],
            url=result["html_url"],
            language="python"
        ))
        logger.info("Found Python plugin: %s", repo_name)
    
    # Search for C++ plugins
    cpp_query = '"idaapi init" AND in:file AND language:"C++"'
    logger.info("C++ query: %s", cpp_query)
    
    cpp_results = search_github_code(token, cpp_query, limit)
    logger.info("found %d C++ IDA plugins", len(cpp_results))
    
    for result in cpp_results:
        repo_name = result["repository"]["full_name"]
        
        if repo_name in DENYLIST:
            logger.debug("skipping %s: denylist", result["html_url"])
            continue
            
        results.append(SearchResult(
            repository=repo_name,
            file=result["path"],
            url=result["html_url"],
            language="C++"
        ))
        logger.info("Found C++ plugin: %s", repo_name)
    
    return results


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


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Find IDA Pro plugins on GitHub and generate HTML (no PyGithub version)")
    parser.add_argument("--limit", type=int, help="Limit the number of results")
    parser.add_argument(
        "--json", action="store_true", help="Output as JSONL instead of HTML (one JSON object per line)"
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        handlers=[RichHandler(console=Console(stderr=True))],
    )

    if args.json:
        search_and_render_plugins_json(args.limit)
    else:
        search_and_render_plugins(args.limit)


if __name__ == "__main__":
    main()
