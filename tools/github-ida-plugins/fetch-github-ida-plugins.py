# You can invoke this script with `uv run` (v0.3+):
#
#     uv run tools/github-ida-plugins/fetch-github-ida-plugins.py \
#       content/posts/2025-05-15-github-ida-plugins/
#
# /// script
# dependencies = [
#    "pygithub>=2.6.1",
#    "rich>=14.0.0",
#    "tree-sitter>=0.24.0",
#    "tree-sitter-python>=0.23.6",
#    "requests>=2.32.3",
# ]
# ///
#
# requires env variable GITHUB_TOKEN to be set.
# TODO:
# - commit count
import os
import sys
import logging
import argparse
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
import sqlite3
import requests
from urllib.parse import urlparse
from collections import defaultdict

import rich
from rich.text import Text
from rich.table import Table
from rich.console import Console
from rich.logging import RichHandler
import tree_sitter_python as tspython
from tree_sitter import Language, Parser
from github import Github
from github import Auth


logger = logging.getLogger(__name__)


DATABASES_FILENAME = "plugins.db"
PY_LANGUAGE = Language(tspython.language())
PY_PARSER = Parser(PY_LANGUAGE)


def extract_repo_info(repo_input: str) -> tuple[str, str]:
    """Extract owner and repo name from GitHub URL or owner/repo format."""
    if repo_input.startswith(('http://', 'https://')):
        path = urlparse(repo_input).path.strip('/')
        owner, repo = path.split('/')[:2]
    else:
        owner, repo = repo_input.split('/')
    return owner, repo


def fetch_repo_zip(owner: str, repo: str) -> bytes | None:
    """Fetch the latest release zipball of a GitHub repository."""
    try:
        # Try main branch first
        url = f"https://github.com/{owner}/{repo}/archive/refs/heads/main.zip"
        response = requests.get(url)
        if response.status_code == 200:
            return response.content
            
        # Try master branch if main fails
        url = f"https://github.com/{owner}/{repo}/archive/refs/heads/master.zip"
        response = requests.get(url)
        if response.status_code == 200:
            return response.content
            
        logger.error("Failed to fetch repository: %s/%s", owner, repo)
        return None
        
    except requests.RequestException as e:
        logger.error("Error fetching repository: %s", e)
        return None


def store_repo_zip(data_dir: Path, owner: str, repo: str, zip_content: bytes) -> None:
    """Store repository zip file in the data directory."""
    repo_dir = data_dir / owner / repo
    repo_dir.mkdir(parents=True, exist_ok=True)
    
    zip_path = repo_dir / f"{repo}.zip"
    with open(zip_path, "wb") as f:
        f.write(zip_content)
    

@dataclass
class IdaPlugin:
    repository: str
    parent: str | None  # parent repository if it's a fork
    description: str
    file: str
    url: str
    content: str
    wanted_name: str | None
    comment: str | None
    created_at: datetime
    pushed_at: datetime
    forks_count: int
    stargazers_count: int


def render_plugin(plugin: IdaPlugin) -> None:
    """Render a plugin instance using rich tables."""
    table = Table(show_header=False, width=120)
    table.add_column("Property", style="grey69", width=15)
    table.add_column("Value", width=105)

    t = Table(show_header=False, width=100, box=None, padding=(0, 0, 0, 0))
    t.add_column("name", width=70, style="bold yellow")
    t.add_column(width=1, style="grey69")
    t.add_column("stars", width=12)
    t.add_column(width=1, style="grey69")
    t.add_column("forks", width=10)
    t.add_row(
        plugin.repository + (f" (from {plugin.parent})" if plugin.parent else ""),
        " ",
        f"[yellow]{plugin.stargazers_count}[/yellow] [grey69]stars[/grey69]",
        " ",
        f" [yellow]{plugin.forks_count}[/yellow] [grey69]forks[/grey69]",
    )
    table.add_row("Repository", t)

    t = Table(show_header=False, width=100, box=None, padding=(0, 0, 0, 0))
    t.add_column("file", width=70)
    t.add_column(width=1, style="grey69")
    t.add_column("created", width=10)
    t.add_column(width=3, style="grey69")
    t.add_column("pushed", width=10)
    t.add_row(f"[link={plugin.url}]{plugin.file}[/link]", " ", str(plugin.created_at.date()), " → ", str(plugin.pushed_at.date()))
    table.add_row("File", t)

    if plugin.wanted_name:
        table.add_row("Plugin Name", plugin.wanted_name)
    if plugin.comment:
        table.add_row("Plugin Cmt", plugin.comment)
    table.add_row("Repo Descr", plugin.description or "N/A")

    rich.print(table)


def init_db(db_path: Path) -> None:
    """Initialize the SQLite database with the required schema."""
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS plugins (
            repository TEXT,
            file TEXT,
            parent TEXT,
            description TEXT,
            url TEXT,
            content TEXT,
            wanted_name TEXT,
            comment TEXT,
            created_at TIMESTAMP,
            pushed_at TIMESTAMP,
            forks_count INTEGER,
            stargazers_count INTEGER,
            PRIMARY KEY (repository, file)
        )
        """)
        conn.commit()


def store_plugin(conn: sqlite3.Connection, plugin: IdaPlugin) -> None:
    """Store a plugin instance in the database."""
    conn.execute("""
    INSERT OR REPLACE INTO plugins (
        repository, file, parent, description, url, content,
        wanted_name, comment, created_at, pushed_at,
        forks_count, stargazers_count
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        plugin.repository, plugin.file, plugin.parent, plugin.description,
        plugin.url, plugin.content,
        plugin.wanted_name, plugin.comment,
        plugin.created_at, plugin.pushed_at,
        plugin.forks_count, plugin.stargazers_count
    ))
    conn.commit()


def load_plugin(row: tuple) -> IdaPlugin:
    """Create a plugin instance from a database row."""
    return IdaPlugin(
        repository=row[0],
        file=row[1],
        parent=row[2],
        description=row[3],
        url=row[4],
        content=row[5],
        wanted_name=row[6],
        comment=row[7],
        created_at=datetime.fromisoformat(row[8]),
        pushed_at=datetime.fromisoformat(row[9]),
        forks_count=row[10],
        stargazers_count=row[11]
    )


def extract_plugin_info(py_source: str) -> dict[str, str]:
    tree = PY_PARSER.parse(bytes(py_source, "utf-8"))
    # search for classes with class variables that are strings
    query = PY_LANGUAGE.query("""
        (class_definition
            body: (block
                    (expression_statement
                        (assignment
                            left: (identifier) @prop_name
                            right: (string) @prop_value
                        )
                    )
                  )
        )
    """)
    matches = query.captures(tree.root_node)
    
    props = {}
    for nodes in matches.values():
        for node in nodes:
            prop_name = node.parent.child_by_field_name("left").text.decode("utf-8")
            prop_value = node.parent.child_by_field_name("right").text.decode("utf-8").strip('"').strip("'")
            props[prop_name] = prop_value

    return props


def fetch_plugins(path: Path, limit: int, fetch_zipball: bool) -> None:
    """Fetch plugins from GitHub and store them in the database."""
    db_path = path / DATABASES_FILENAME

    auth = Auth.Token(os.getenv("GITHUB_TOKEN"))
    g = Github(auth=auth)

    query = "language:python AND \"def PLUGIN_ENTRY()\" AND in:file"
    logger.info("query: %s", query)
    
    results = g.search_code(query=query)
    logger.info("found %d IDA plugins", results.totalCount)

    with sqlite3.connect(db_path) as conn:
        max_results = limit or results.totalCount
        for result in results[:max_results]:
            parent: str | None = None
            if result.repository.fork:
                if result.repository.parent:
                    parent = result.repository.parent.full_name

            content = result.decoded_content.decode("utf-8")
            props = extract_plugin_info(content)

            plugin = IdaPlugin(
                repository=result.repository.full_name,
                parent=parent,
                description=result.repository.description,
                file=result.path,
                url=result.html_url,
                content=content,
                wanted_name=props.get("wanted_name"),
                comment=props.get("comment"),
                created_at=result.repository.created_at,
                pushed_at=result.repository.pushed_at,
                forks_count=result.repository.forks_count,
                stargazers_count=result.repository.stargazers_count,
            )
            store_plugin(conn, plugin)
            try:
                render_plugin(plugin)
            except Exception as e:
                logger.error("Error rendering plugin %s: %s", plugin.file, e, exc_info=True)

            owner, repo = extract_repo_info(result.repository.full_name)
            if fetch_zipball:
                zip_path = path / owner / repo / f"{repo}.zip"
                if not zip_path.exists():
                    zip_content = fetch_repo_zip(owner, repo)
                    if zip_content:
                        logger.info("fetched %s", zip_path)
                        store_repo_zip(path, owner, repo, zip_content)


def main():
    parser = argparse.ArgumentParser(description="Find IDA Pro plugins on GitHub")
    parser.add_argument("--limit", type=int, help="Limit the number of results")
    parser.add_argument("--fetch-zipball", type=bool, help="Fetch zipball for each plugin")
    parser.add_argument("path", type=Path, help="Path to directory containing database and repos")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        handlers=[RichHandler(console=Console(stderr=True))],
    )

    init_db(args.path / DATABASES_FILENAME)
    fetch_plugins(args.path, args.limit, args.fetch_zipball)


if __name__ == "__main__":
    main()
