#!/usr/bin/env python3

import io
import zipfile
import argparse
from typing import Dict, List, Optional
from pathlib import Path
from urllib.parse import urlparse

import requests
from rich.tree import Tree
from rich.syntax import Syntax
from rich.console import Console

console = Console()


def extract_repo_info(repo_input: str) -> tuple[str, str]:
    """Extract owner and repo name from GitHub URL or owner/repo format."""
    if repo_input.startswith(("http://", "https://")):
        path = urlparse(repo_input).path.strip("/")
        owner, repo = path.split("/")[:2]
    else:
        owner, repo = repo_input.split("/")
    return owner, repo


def fetch_repo_zip(owner: str, repo: str) -> Optional[bytes]:
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

        console.print(f"[red]Failed to fetch repository: {owner}/{repo}[/red]")
        return None

    except requests.RequestException as e:
        console.print(f"[red]Error fetching repository: {e}[/red]")
        return None


def get_language(filename: str) -> Optional[str]:
    """Get language for syntax highlighting based on file extension."""
    ext = Path(filename).suffix.lower()
    lang_map = {
        ".py": "python",
        ".md": "markdown",
        ".js": "javascript",
        ".ts": "typescript",
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".sh": "bash",
        ".c": "c",
        ".cpp": "cpp",
        ".h": "c",
        ".hpp": "cpp",
        ".toml": "toml",
        ".gitignore": "gitignore",
    }
    return lang_map.get(ext)


def build_directory_tree(file_list: List[zipfile.ZipInfo]) -> Tree:
    """Build a rich Tree structure from the zip file list."""
    tree = Tree(".")
    dirs: Dict[str, Tree] = {"": tree}

    for file in sorted(file_list, key=lambda x: x.filename):
        if file.is_dir():
            continue

        parts = file.filename.split("/")
        current_path = ""

        # Build directory structure
        for i, part in enumerate(parts[:-1]):
            parent_path = current_path
            current_path = f"{current_path}/{part}" if current_path else part

            if current_path not in dirs:
                dirs[current_path] = dirs[parent_path].add(f"{part}")

        # Add file
        filename = parts[-1]
        if current_path:
            dirs[current_path].add(f"{filename}")
        else:
            tree.add(f"{filename}")

    return tree


def process_zipball(zip_content: bytes) -> None:
    """Process zipball contents and print files in markdown format."""
    with zipfile.ZipFile(io.BytesIO(zip_content)) as zip_file:
        console.print("\n[bold cyan]Directory Structure:[/bold cyan]")
        tree = build_directory_tree(zip_file.filelist)
        console.print(tree)
        console.print("\n[bold cyan]File Contents:[/bold cyan]\n")

        sorted_files = sorted(
            zip_file.filelist,
            key=lambda x: (
                x.filename.count("/"),  # Sort by directory depth
                x.filename.replace(".", "~"),  # period sorts after other characters
            ),
        )
        total_chars = 0
        for file in sorted_files:
            if file.is_dir():
                continue
            try:
                content = zip_file.read(file.filename).decode("utf-8")
            except UnicodeDecodeError:
                console.print(f"[yellow]Skipping binary file: {file.filename}[/yellow]")
                continue

            if not content:
                continue

            filename = Path(file.filename).name
            language = get_language(filename)

            print(f"{file.filename}:")
            if language:
                syntax = Syntax(content, language, theme="monokai", line_numbers=True)
                console.print(f"```{language}")
                console.print(syntax)
                console.print("```")
            else:
                console.print("```")
                console.print(content)
                console.print("```")
            console.print()

            total_chars += len(content)
            if total_chars >= 900_000:
                console.print("[yellow]Reached 900k character limit. Stopping.[/yellow]")
                break


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch and display GitHub repository contents")
    parser.add_argument("repo", help="GitHub repository (owner/repo or URL)")
    args = parser.parse_args()

    owner, repo = extract_repo_info(args.repo)
    zip_content = fetch_repo_zip(owner, repo)

    if zip_content:
        process_zipball(zip_content)


if __name__ == "__main__":
    main()
